import argparse
import json
import re
from collections import Counter
from pathlib import Path

from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


TEXT_KEYS = ["message", "log", "text", "event", "description", "msg"]
LABEL_KEYS = ["label", "is_failure", "failed", "status", "level", "severity", "result", "outcome"]
FAILURE_HINTS = {
	"fail",
	"failure",
	"error",
	"exception",
	"fatal",
	"critical",
	"crash",
	"timeout",
	"denied",
	"unavailable",
}


def normalize_text(s: str) -> str:
	s = str(s).lower()
	s = re.sub(r"\s+", " ", s)
	return s.strip()


def extract_text(record: dict) -> str:
	for key in TEXT_KEYS:
		if key in record and record[key] is not None:
			return normalize_text(record[key])
	return normalize_text(json.dumps(record, ensure_ascii=False))


def parse_bool_like(value):
	if isinstance(value, bool):
		return int(value)
	if isinstance(value, (int, float)):
		return int(value != 0)
	if isinstance(value, str):
		v = value.strip().lower()
		if v in {"1", "true", "yes", "y", "fail", "failed", "failure", "error", "critical", "fatal"}:
			return 1
		if v in {"0", "false", "no", "n", "ok", "success", "passed", "info", "warning"}:
			return 0
	return None


def infer_label(record: dict, text: str):
	for key in LABEL_KEYS:
		if key in record:
			parsed = parse_bool_like(record[key])
			if parsed is not None:
				return parsed

	for hint in FAILURE_HINTS:
		if hint in text:
			return 1
	return 0


def load_jsonl(path: Path):
	texts, labels = [], []
	with path.open("r", encoding="utf-8") as f:
		for line in f:
			line = line.strip()
			if not line:
				continue
			try:
				record = json.loads(line)
			except json.JSONDecodeError:
				continue

			text = extract_text(record)
			label = infer_label(record, text)
			texts.append(text)
			labels.append(label)
	return texts, labels


def tokenize(text: str):
	return re.findall(r"[a-zA-Z0-9_]+", text.lower())


def failure_patterns(texts, labels, top_k=20):
	fail_counter = Counter()
	ok_counter = Counter()

	for t, y in zip(texts, labels):
		toks = tokenize(t)
		if y == 1:
			fail_counter.update(toks)
			fail_counter.update(" ".join(bg) for bg in zip(toks, toks[1:]))
		else:
			ok_counter.update(toks)
			ok_counter.update(" ".join(bg) for bg in zip(toks, toks[1:]))

	fail_total = max(sum(fail_counter.values()), 1)
	ok_total = max(sum(ok_counter.values()), 1)

	scored = []
	for term, f_count in fail_counter.items():
		if f_count < 2:
			continue
		o_count = ok_counter.get(term, 0)
		score = (f_count / fail_total) / ((o_count + 1) / ok_total)
		scored.append((score, term, f_count, o_count))

	scored.sort(reverse=True)
	return scored[:top_k]


def cluster_failure_texts(texts, labels, max_clusters=3):
	failed = [t for t, y in zip(texts, labels) if y == 1]
	if len(failed) < 6:
		return []

	n_clusters = min(max_clusters, max(2, len(failed) // 5))
	vect = TfidfVectorizer(stop_words="english", max_features=3000, ngram_range=(1, 2), min_df=2)
	X = vect.fit_transform(failed)
	if X.shape[0] <= n_clusters:
		return []

	model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
	model.fit(X)

	terms = vect.get_feature_names_out()
	patterns = []
	for i in range(n_clusters):
		top_idx = model.cluster_centers_[i].argsort()[::-1][:8]
		top_terms = [terms[j] for j in top_idx]
		cluster_size = int((model.labels_ == i).sum())
		patterns.append((i, cluster_size, top_terms))
	return patterns


def train_and_report(texts, labels):
	if len(set(labels)) < 2:
		print("Not enough label variety (need both failure and non-failure).")
		return

	X_train, X_test, y_train, y_test = train_test_split(
		texts, labels, test_size=0.2, random_state=42, stratify=labels
	)

	clf = Pipeline(
		[
			("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=10000)),
			("model", LogisticRegression(max_iter=1000, class_weight="balanced")),
		]
	)
	clf.fit(X_train, y_train)
	preds = clf.predict(X_test)

	print(f"Accuracy: {accuracy_score(y_test, preds):.4f}")
	print(classification_report(y_test, preds, digits=4))


def main():
	parser = argparse.ArgumentParser(description="Train a simple failure detector from logs.jsonl and find failure patterns.")
	parser.add_argument("--data", type=str, default="logs.jsonl", help="Path to logs.jsonl")
	args = parser.parse_args()

	path = Path(args.data)
	if not path.exists():
		print(f"Data file not found: {path}")
		return

	texts, labels = load_jsonl(path)
	if not texts:
		print("No valid log records found.")
		return

	print(f"Loaded {len(texts)} records")
	print(f"Failures: {sum(labels)} | Non-failures: {len(labels) - sum(labels)}")

	train_and_report(texts, labels)

	print("\nTop failure-associated patterns:")
	for score, term, f_count, o_count in failure_patterns(texts, labels):
		print(f"{term:<30} score={score:.2f} fail={f_count} non_fail={o_count}")

	clusters = cluster_failure_texts(texts, labels)
	if clusters:
		print("\nFailure clusters:")
		for cid, size, terms in clusters:
			print(f"Cluster {cid} (size={size}): {', '.join(terms)}")


if __name__ == "__main__":
	main()

