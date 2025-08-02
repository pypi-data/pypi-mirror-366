import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


class Softmax回归(nn.Module):
    """使用PyTorch实现的Softmax回归模型"""

    def __init__(self, 输入维度, 类别数量, 正则化方式='l2', 正则化系数=0.01):
        super(Softmax回归, self).__init__()
        # 线性层：输入维度 -> 类别数量（相当于权重和偏置的组合）
        self.线性层 = nn.Linear(输入维度, 类别数量)
        self.正则化方式 = 正则化方式
        self.正则化系数 = 正则化系数

    def forward(self, x):
        """前向传播：返回未经过softmax的原始输出（logits）"""
        return self.线性层(x)

    def 计算正则化损失(self):
        """计算正则化损失，防止过拟合"""
        if self.正则化方式 == 'l2':
            # L2正则化：权重的L2范数平方
            return 0.5 * self.正则化系数 * torch.norm(self.线性层.weight, p=2) ** 2
        elif self.正则化方式 == 'l1':
            # L1正则化：权重的L1范数
            return self.正则化系数 * torch.norm(self.线性层.weight, p=1)
        return 0.0  # 无正则化


def 训练模型(模型, 训练数据加载器, 损失函数, 优化器, 设备, 训练轮数=1000):
    """训练模型的函数"""
    模型.train()  # 切换到训练模式
    for 轮次 in range(训练轮数):
        总损失 = 0.0
        for 批次特征, 批次标签 in 训练数据加载器:
            # 将数据移动到指定设备（GPU或CPU）
            批次特征, 批次标签 = 批次特征.to(设备), 批次标签.to(设备)

            # 前向传播：计算模型输出
            输出 = 模型(批次特征)
            # 计算交叉熵损失（PyTorch的CrossEntropyLoss内置了Softmax）
            交叉熵损失 = 损失函数(输出, 批次标签)
            # 加上正则化损失
            正则化损失 = 模型.计算正则化损失()
            总损失值 = 交叉熵损失 + 正则化损失

            # 反向传播和参数优化
            优化器.zero_grad()  # 清零梯度，防止累积
            总损失值.backward()  # 反向传播计算梯度
            优化器.step()  # 更新模型参数

            总损失 += 总损失值.item()

        # 每100轮打印一次平均损失
        if (轮次 + 1) % 100 == 0:
            平均损失 = 总损失 / len(训练数据加载器)
            print(f"轮次 [{轮次 + 1}/{训练轮数}], 损失: {平均损失:.4f}")


def 评估模型(模型, 测试特征, 测试标签, 设备):
    """评估模型性能的函数"""
    模型.eval()  # 切换到评估模式
    with torch.no_grad():  # 禁用梯度计算，节省内存和计算资源
        # 将测试数据转换为张量并移动到指定设备
        测试特征张量 = torch.tensor(测试特征, dtype=torch.float32).to(设备)
        输出 = 模型(测试特征张量)
        # 取概率最大的类别作为预测结果
        _, 预测标签 = torch.max(输出.data, 1)
        # 将结果从GPU移回CPU并转换为numpy数组
        预测标签 = 预测标签.cpu().numpy()

    # 计算并打印评估指标
    准确率 = accuracy_score(测试标签, 预测标签)
    print(f"准确率: {准确率:.4f}")
    print("\n混淆矩阵:")
    print(confusion_matrix(测试标签, 预测标签))
    print("\n分类报告:")
    print(classification_report(测试标签, 预测标签))

    return {
        '准确率': 准确率,
        '混淆矩阵': confusion_matrix(测试标签, 预测标签),
        '分类报告': classification_report(测试标签, 预测标签, output_dict=True)
    }


def 主函数():
    # 设置计算设备（优先使用GPU，如果可用）
    设备 = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"使用计算设备: {设备}")

    # 示例1：使用鸢尾花数据集
    from sklearn.datasets import load_iris
    数据 = load_iris()
    特征, 标签 = 数据.data, 数据.target

    # 划分训练集和测试集
    训练特征, 测试特征, 训练标签, 测试标签 = train_test_split(
        特征, 标签, test_size=0.2, random_state=42
    )

    # 特征标准化（使每个特征均值为0，标准差为1）
    标准化器 = StandardScaler()
    训练特征标准化 = 标准化器.fit_transform(训练特征)
    测试特征标准化 = 标准化器.transform(测试特征)

    # 将数据转换为PyTorch张量
    训练特征张量 = torch.tensor(训练特征标准化, dtype=torch.float32)
    训练标签张量 = torch.tensor(训练标签, dtype=torch.long)

    # 创建数据加载器（用于批量加载数据）
    批次大小 = 32
    训练数据集 = TensorDataset(训练特征张量, 训练标签张量)
    训练数据加载器 = DataLoader(训练数据集, batch_size=批次大小, shuffle=True)

    # 模型参数
    输入维度 = 训练特征.shape[1]  # 特征数量
    类别数量 = len(np.unique(标签))  # 类别数量

    # 初始化模型
    模型 = Softmax回归(
        输入维度=输入维度,
        类别数量=类别数量,
        正则化方式='l2',
        正则化系数=0.001
    ).to(设备)  # 将模型移动到指定设备

    # 定义损失函数（交叉熵损失，内置Softmax操作）
    损失函数 = nn.CrossEntropyLoss()
    # 定义优化器（Adam优化器通常收敛更快）
    优化器 = optim.Adam(模型.parameters(), lr=0.01)  # lr是学习率

    # 训练模型
    print("开始训练鸢尾花数据集...")
    训练模型(模型, 训练数据加载器, 损失函数, 优化器, 设备, 训练轮数=2000)

    # 评估模型
    print("\n鸢尾花数据集测试集评估结果:")
    评估模型(模型, 测试特征标准化, 测试标签, 设备)

    # 示例2：使用自定义数据集
    def 自定义数据集示例():
        # 生成模拟数据（可替换为自己的数据集）
        np.random.seed(42)
        样本数量 = 1000
        特征数量 = 15
        类别总数 = 5

        # 生成随机特征和标签
        特征 = np.random.randn(样本数量, 特征数量)
        标签 = np.random.randint(0, 类别总数, size=样本数量)

        # 数据划分和预处理
        训练特征, 测试特征, 训练标签, 测试标签 = train_test_split(
            特征, 标签, test_size=0.2, random_state=42
        )
        标准化器 = StandardScaler()
        训练特征标准化 = 标准化器.fit_transform(训练特征)
        测试特征标准化 = 标准化器.transform(测试特征)

        # 转换为PyTorch张量
        训练特征张量 = torch.tensor(训练特征标准化, dtype=torch.float32)
        训练标签张量 = torch.tensor(训练标签, dtype=torch.long)
        训练数据集 = TensorDataset(训练特征张量, 训练标签张量)
        训练数据加载器 = DataLoader(训练数据集, batch_size=64, shuffle=True)

        # 初始化模型
        模型 = Softmax回归(
            输入维度=特征数量,
            类别数量=类别总数,
            正则化方式=None  # 不使用正则化
        ).to(设备)

        # 定义损失函数和优化器
        损失函数 = nn.CrossEntropyLoss()
        优化器 = optim.SGD(模型.parameters(), lr=0.05, momentum=0.9)  # 使用SGD优化器

        # 训练和评估
        print("\n开始训练自定义数据集...")
        训练模型(模型, 训练数据加载器, 损失函数, 优化器, 设备, 训练轮数=1500)

        print("\n自定义数据集测试集评估结果:")
        评估模型(模型, 测试特征标准化, 测试标签, 设备)

    # 运行自定义数据集示例
    自定义数据集示例()


if __name__ == "__main__":
    主函数()