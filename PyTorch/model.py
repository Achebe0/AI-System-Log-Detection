import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import pandas as pd

class LogDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.FloatTensor(X)
        self.y = torch.LongTensor(y)
        
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

class LogClassifier(nn.Module):
    def __init__(self, input_size, num_classes):
        super(LogClassifier, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, num_classes)
        )
        
    def forward(self, x):
        return self.network(x)

def load_and_preprocess_data(jsonl_path):
    # Load logs
    data = []
    with open(jsonl_path, 'r') as f:
        for line in f:
            data.append(json.loads(line))
            
    df = pd.DataFrame(data)
    
    # Needs at least these columns: latency_ms, status_code, service, severity, scenario
    
    # Label Encoders
    le_service = LabelEncoder()
    le_severity = LabelEncoder()
    le_scenario = LabelEncoder()
    
    df['service_encoded'] = le_service.fit_transform(df['service'])
    df['severity_encoded'] = le_severity.fit_transform(df['severity'])
    
    # Target variable
    y = le_scenario.fit_transform(df['scenario'])
    
    # Feature matrix
    X = df[['latency_ms', 'status_code', 'service_encoded', 'severity_encoded']].values
    
    # Scale numerical features (latency & status code)
    scaler = StandardScaler()
    X[:, 0:2] = scaler.fit_transform(X[:, 0:2])
    
    return X, y, le_scenario

def train_model(jsonl_path="logs.jsonl", epochs=50, batch_size=16):
    print("Loading data...")
    X, y, le_scenario = load_and_preprocess_data(jsonl_path)
    num_classes = len(le_scenario.classes_)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    train_dataset = LogDataset(X_train, y_train)
    test_dataset = LogDataset(X_test, y_test)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    model = LogClassifier(input_size=X.shape[1], num_classes=num_classes)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    print(f"Training started for {epochs} epochs...")
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for inputs, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            
        if (epoch + 1) % 10 == 0:
            print(f"Epoch [{epoch+1}/{epochs}], Loss: {running_loss/len(train_loader):.4f}")
            
    # Evaluation
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for inputs, labels in test_loader:
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
    print(f"\nTest Accuracy: {100 * correct / total:.2f}%")
    
    # Save the model
    torch.save(model.state_dict(), "PyTorch/model.pth")
    print("Model saved to PyTorch/model.pth")
    return model, le_scenario

if __name__ == "__main__":
    train_model()
