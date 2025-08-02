import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


class SoftmaxRegression(nn.Module):
    """PyTorch实现的Softmax回归模型"""

    def __init__(self, input_dim, num_classes, regularization='l2', lambda_reg=0.01):
        super(SoftmaxRegression, self).__init__()
        # 线性层：输入维度 -> 类别数
        self.linear = nn.Linear(input_dim, num_classes)
        self.regularization = regularization
        self.lambda_reg = lambda_reg

    def forward(self, x):
        """前向传播：返回未归一化的logits"""
        return self.linear(x)

    def compute_regularization_loss(self):
        """计算正则化损失"""
        if self.regularization == 'l2':
            return 0.5 * self.lambda_reg * torch.norm(self.linear.weight, p=2) ** 2
        elif self.regularization == 'l1':
            return self.lambda_reg * torch.norm(self.linear.weight, p=1)
        return 0.0


def train_model(model, train_loader, loss, optimizer, device, epochs=1000):
    """训练模型"""
    model.train()  # 训练模式
    for epoch in range(epochs):
        total_loss = 0.0
        for batch_X, batch_y in train_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)

            # 前向传播
            outputs = model(batch_X)
            # 计算交叉熵损失（内置Softmax）
            ce_loss = loss(outputs, batch_y)
            # 加上正则化损失
            reg_loss = model.compute_regularization_loss()
            loss = ce_loss + reg_loss

            # 反向传播和优化
            optimizer.zero_grad()  # 清零梯度
            loss.backward()  # 反向传播
            optimizer.step()  # 更新参数

            total_loss += loss.item()

        # 每100轮打印一次损失
        if (epoch + 1) % 100 == 0:
            avg_loss = total_loss / len(train_loader)
            print(f"Epoch [{epoch + 1}/{epochs}], Loss: {avg_loss:.4f}")


def evaluate_model(model, X_test, y_test, device):
    """评估模型性能"""
    model.eval()  # 评估模式
    with torch.no_grad():  # 禁用梯度计算
        X_test_tensor = torch.tensor(X_test, dtype=torch.float32).to(device)
        outputs = model(X_test_tensor)
        _, y_pred = torch.max(outputs.data, 1)
        y_pred = y_pred.cpu().numpy()

    # 计算评估指标
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy:.4f}")
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    return {
        'accuracy': accuracy,
        'confusion_matrix': confusion_matrix(y_test, y_pred),
        'classification_report': classification_report(y_test, y_pred, output_dict=True)
    }


def main():
    # 设置设备（GPU如果可用）
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"使用设备: {device}")

    # 示例1：使用鸢尾花数据集
    from sklearn.datasets import load_iris
    data = load_iris()
    X, y = data.data, data.target

    # 数据预处理
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 特征标准化
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 转换为PyTorch张量
    X_train_tensor = torch.tensor(X_train_scaled, dtype=torch.float32)
    y_train_tensor = torch.tensor(y_train, dtype=torch.long)
    X_test_tensor = torch.tensor(X_test_scaled, dtype=torch.float32)

    # 创建数据加载器
    batch_size = 32
    train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    # 模型参数
    input_dim = X_train.shape[1]
    num_classes = len(np.unique(y))

    # 初始化模型、损失函数和优化器
    model = SoftmaxRegression(
        input_dim=input_dim,
        num_classes=num_classes,
        regularization='l2',
        lambda_reg=0.001
    ).to(device)

    # 交叉熵损失（包含Softmax操作）
    criterion = nn.CrossEntropyLoss()
    # 优化器（Adam通常比SGD效果更好）
    optimizer = optim.Adam(model.parameters(), lr=0.01)

    # 训练模型
    print("开始训练鸢尾花数据集...")
    train_model(model, train_loader, criterion, optimizer, device, epochs=2000)

    # 评估模型
    print("\n鸢尾花数据集测试集评估:")
    evaluate_model(model, X_test_scaled, y_test, device)

    # 示例2：使用自定义数据集
    def custom_dataset_example():
        # 生成模拟数据
        np.random.seed(42)
        n_samples = 1000
        n_features = 15
        n_classes = 5

        X = np.random.randn(n_samples, n_features)
        y = np.random.randint(0, n_classes, size=n_samples)

        # 数据划分和预处理
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # 转换为张量
        X_train_tensor = torch.tensor(X_train_scaled, dtype=torch.float32)
        y_train_tensor = torch.tensor(y_train, dtype=torch.long)
        train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
        train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)

        # 初始化模型
        model = SoftmaxRegression(
            input_dim=n_features,
            num_classes=n_classes,
            regularization=None
        ).to(device)

        criterion = nn.CrossEntropyLoss()
        optimizer = optim.SGD(model.parameters(), lr=0.05, momentum=0.9)

        # 训练和评估
        print("\n开始训练自定义数据集...")
        train_model(model, train_loader, criterion, optimizer, device, epochs=1500)

        print("\n自定义数据集测试集评估:")
        evaluate_model(model, X_test_scaled, y_test, device)

    # 运行自定义数据集示例
    custom_dataset_example()


if __name__ == "__main__":
    main()