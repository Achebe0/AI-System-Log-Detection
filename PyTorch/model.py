import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
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
            nn.Linear(input_size, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.4),
            
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
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
    
    # Create more sophisticated features
    df['latency_category'] = pd.cut(df['latency_ms'], bins=[0, 100, 500, 1000, 5000, float('inf')], 
                                   labels=[0, 1, 2, 3, 4])
    df['is_error'] = (df['status_code'] >= 400).astype(int)
    df['is_high_latency'] = (df['latency_ms'] > 200).astype(int)
    df['latency_status_interaction'] = df['latency_ms'] * df['status_code'] / 1000  # Normalized interaction
    
    # Feature matrix - enhanced features
    X = df[['latency_ms', 'status_code', 'service_encoded', 'severity_encoded', 'latency_category', 'is_error', 'is_high_latency', 'latency_status_interaction']].values
    
    # Convert categorical to numeric
    X = X.astype(float)
    
    # Scale features
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    
    return X, y, le_scenario

def test_sklearn_baseline(jsonl_path="logs.jsonl"):
    """Test with sklearn Random Forest to see maximum achievable accuracy"""
    print("Testing sklearn Random Forest baseline...")
    X, y, le_scenario = load_and_preprocess_data(jsonl_path)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    
    y_pred = rf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Random Forest Test Accuracy: {accuracy*100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=le_scenario.classes_))
    
    return accuracy

def train_model(jsonl_path="logs.jsonl", epochs=500, batch_size=16, patience=50):
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
    optimizer = optim.AdamW(model.parameters(), lr=0.0003, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=15)
    
    print(f"Training started for up to {epochs} epochs with early stopping (patience={patience})...")
    
    best_accuracy = 0.0
    patience_counter = 0
    
    for epoch in range(epochs):
        # Training
        model.train()
        running_loss = 0.0
        for inputs, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        
        # Validation
        model.eval()
        correct = 0
        total = 0
        val_loss = 0.0
        with torch.no_grad():
            for inputs, labels in test_loader:
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        accuracy = 100 * correct / total
        avg_train_loss = running_loss / len(train_loader)
        avg_val_loss = val_loss / len(test_loader)
        
        # Learning rate scheduling
        scheduler.step(accuracy)
        
        if (epoch + 1) % 10 == 0:
            print(f"Epoch [{epoch+1}/{epochs}], Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}, Val Accuracy: {accuracy:.2f}%")
        
        # Early stopping
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            patience_counter = 0
            # Save best model
            torch.save(model.state_dict(), "PyTorch/best_model.pth")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping at epoch {epoch+1}. Best accuracy: {best_accuracy:.2f}%")
                break
    
    # Load best model for final evaluation
    model.load_state_dict(torch.load("PyTorch/best_model.pth"))
    
    # Final evaluation
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for inputs, labels in test_loader:
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
    final_accuracy = 100 * correct / total
    print(f"\n🎉 Final Test Accuracy: {final_accuracy:.2f}%")
    
    # Save final model
    torch.save(model.state_dict(), "PyTorch/model.pth")
    print("Model saved to PyTorch/model.pth")
    return model, le_scenario

if __name__ == "__main__":
    # First test sklearn baseline
    test_sklearn_baseline()
    print("\n" + "="*50)
    # Then train neural network
    train_model()
