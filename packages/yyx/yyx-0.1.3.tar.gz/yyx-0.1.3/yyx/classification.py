import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib as mpl
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
import seaborn as sns
from matplotlib.colors import to_hex
from sklearn.decomposition import PCA
import os
import math
from adjustText import adjust_text

mpl.rcParams.update({
    'font.family': ['Times New Roman','Simhei'],
    'font.size': 12,  # 基础字体大小
    'axes.titlesize': 14,  # 标题字体大小
    'axes.labelsize': 12,  # 坐标轴标签字体大小
    'legend.fontsize': 10,  # 图例字体大小
    'xtick.labelsize': 10,  # x轴刻度字体大小
    'ytick.labelsize': 10,  # y轴刻度字体大小
    'lines.linewidth': 1.5,  # 线条宽度
    'lines.markersize': 4,  # 标记点大小（如需添加标记）
    'axes.linewidth': 0.8,  # 坐标轴边框宽度
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'legend.framealpha': 0.8,  # 图例透明度
})
class Softmax(nn.Module):
    def __init__(self,input_size,output_size,regularization,lambda_reg):
        super().__init__()
        self.linear=nn.Linear(input_size,output_size)
        self.regularization=regularization
        self.lambda_reg=lambda_reg
    def forward(self,x):
        return self.linear(x)
    def compute_reg_loss(self):
        if self.regularization== 'l1':
            return self.lambda_reg*torch.norm(self.linear.weight,p=1)
        elif self.regularization== 'l2':
            return self.lambda_reg*torch.norm(self.linear.weight,p=2)
        return 0.0
def train_model(model:nn.modules,train_loader:DataLoader,x_test:np.ndarray,y_test:np.ndarray,loss_fn,
                optimizer:torch.optim,device,epochs=1000):
    train_loss=[]
    test_loss=[]
    x_test_tensor=torch.tensor(x_test,dtype=torch.float32).to(device)
    y_test_tensor=torch.tensor(y_test,dtype=torch.long).to(device)
    for epoch in range(epochs):
        model.train()
        total_loss=0
        for batch_x,batch_y in train_loader:
            batch_x,batch_y=batch_x.to(device),batch_y.to(device).squeeze().long()
            out_put=model(batch_x)
            ce_loss=loss_fn(out_put,batch_y)
            reg_loss=model.compute_reg_loss()
            loss=ce_loss+reg_loss

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss+=loss.item()
        cur_loss = total_loss / len(train_loader)
        train_loss.append(cur_loss)
        model.eval()
        with torch.no_grad():
            test_output=model(x_test_tensor)
            loss1=loss_fn(test_output,y_test_tensor)
            loss2=model.compute_reg_loss()
            loss=(loss1+loss2).item()
            test_loss.append(loss)
        if (epoch+1)%100==0:
            print(f'Epoch[{epoch+1}/{epochs}]：训练损失={cur_loss:.4f}  测试损失={loss}')
    plt.figure(figsize=(10,6))
    plt.plot(range(1,epochs+1),train_loss,label='训练损失')
    plt.plot(range(1,epochs+1),test_loss,label='测试损失',linestyle='--')
    plt.legend(frameon=False,fontsize=11)
    plt.grid(alpha=0.3)
    plt.title('训练集与测试集损失')
    plt.savefig('loss_cur.png',dpi=300, bbox_inches='tight')
    plt.show()
    return train_loss,test_loss
def evaluate_model(model:nn.modules,x_test:np.ndarray,y_test:np.ndarray,device):
    model.eval()
    with torch.no_grad():
        x_test_tensor=torch.tensor(x_test,dtype=torch.float32).to(device)
        _,y_pre=torch.max(model(x_test_tensor),dim=1)
        y_pre=y_pre.cpu().numpy()
    accuracy=accuracy_score(y_test,y_pre)
    print(f'准确率:{accuracy:.4f}')
    _confusion_matrix=confusion_matrix(y_test,y_pre)
    print(f'混淆矩阵{_confusion_matrix}')
    print('分类报告')
    _classification_report=classification_report(y_test,y_pre)
    print(_classification_report)
    return {
        '准确率':accuracy,
        '混淆矩阵':_confusion_matrix,
        '分类报告':_classification_report
    }
def softmax_classifier(x:np.ndarray,y:np.ndarray,test_size:float=0.2,random_state:int=42,batch_size:int=32,
                       epochs:int=2000,lr:float=0.01,lambda_reg:float=0.001):
    '''
    softmax分类器，输入n*m的x和n*1的y，输出评估结果
    '''
    if x.ndim!=2:
        raise ValueError('x的维度必须为2')
    elif y.ndim!=1:
        raise ValueError('y的维度必须为1')
    elif len(x)!=len(y):
        raise ValueError('样本数不对应')
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=test_size,random_state=random_state)
    scaler=StandardScaler()
    x_train_scaled=scaler.fit_transform(x_train)
    x_test_scaled=scaler.transform(x_test)
    x_train_tensor=torch.tensor(x_train_scaled,dtype=torch.float32)
    y_train_tensor=torch.tensor(y_train,dtype=torch.float32)
    dataset=TensorDataset(x_train_tensor,y_train_tensor)
    dataloader=DataLoader(dataset,batch_size=batch_size,shuffle=True)
    input_size=x_train_tensor.shape[1]
    output_size= len(np.unique(y))
    model=Softmax(input_size,output_size,'l2',lambda_reg).to(device)
    optimizer=optim.Adam(model.parameters(),lr=lr)
    loss=nn.CrossEntropyLoss()
    train_model(model,dataloader,x_test_scaled,y_test,loss,optimizer,device,epochs)
    evaluate_model(model,x_test_scaled,y_test,device)
def fun():
    from sklearn.datasets import load_iris
    data=load_iris()
    x,y=data.data,data.target
    softmax_classifier(x,y,epochs=1000)
def hierarchical_clustering(df: pd.DataFrame,n_clusters: int = 2,title1: str = '层次聚类谱系图',title2:str=None,title3: str = '层次聚类二维散点图(PCA降维)',max_clusters: int = 10):
    '''
    层次聚类(平均组间连接)
    输入:带index的df
    输出聚类中心表格、谱系图、肘部法图、PCA降维散点图
    '''
    # -------- [1] 拆分样本名与指标 --------
    df = df.copy()
    sample_names = df.iloc[:, 0]
    df_features = df.iloc[:, 1:]

    # -------- [2] 标准化 --------
    scaler = StandardScaler()
    df_scaled = pd.DataFrame(
        scaler.fit_transform(df_features),
        index=sample_names,
        columns=df_features.columns
    )

    # -------- [3] 层次聚类 --------
    Z = linkage(df_scaled, method='ward', metric='euclidean')

    # -------- [4] 绘制谱系图 --------
    n_samples = len(sample_names)
    fig_height = max(6, n_samples * 0.3)
    plt.figure(figsize=(12, fig_height))
    color_palette = sns.color_palette("tab10", 10)
    link_color_func = lambda k: to_hex(color_palette[k % len(color_palette)])

    dendrogram(
        Z,
        labels=sample_names.tolist(),
        orientation='right',
        leaf_font_size=10,
        color_threshold=5,
        above_threshold_color='lightgray',
        link_color_func=link_color_func
    )
    if title1:
        plt.title(title1, fontsize=16, fontweight='bold')
    plt.xlabel('欧式距离', fontsize=13)
    plt.ylabel('样本名称', fontsize=13)
    plt.xticks(fontsize=11)
    plt.yticks(fontsize=9)
    plt.tight_layout()
    plt.savefig('dendrogram_vertical_adjusted.png', dpi=300, bbox_inches='tight')
    plt.show()
    # -------- [4.5] 肘部原则分析（仅绘图，不自动修改 n_clusters） --------
    # 无论 n_clusters 是否指定，都运行肘部分析并绘图
    print("执行肘部原则分析（仅绘图，不强制修改聚类数）...")
    sse = []
    possible_clusters = range(1, min(max_clusters + 1, len(sample_names)))

    for k in possible_clusters:
        clusters = fcluster(Z, t=k, criterion='maxclust')
        cluster_centers = np.zeros((k, df_scaled.shape[1]))
        for i in range(1, k + 1):
            cluster_points = df_scaled[clusters == i]
            cluster_centers[i - 1] = cluster_points.mean(axis=0)

        sse_val = 0
        for i in range(1, k + 1):
            cluster_points = df_scaled[clusters == i].values
            center = cluster_centers[i - 1]
            sse_val += np.sum((cluster_points - center) ** 2)
        sse.append(sse_val)

    # 绘制肘部图（不自动赋值 n_clusters，仅可视化）
    plt.figure(figsize=(10, 6))
    plt.plot(possible_clusters, sse, 'bo-')
    plt.xlabel('聚类数量 (k)')
    plt.ylabel('总误差平方和 (SSE)')
    plt.grid(alpha=0.3)
    if title2:
        plt.title(f'{title2}')
    plt.tight_layout()
    plt.savefig('肘部法.png', dpi=300)
    plt.show()
    # -------- [5] 获取簇标签（严格使用输入的 n_clusters） --------
    clusters = fcluster(Z, t=n_clusters, criterion='maxclust')
    df_result = df.copy()
    df_result['簇标签'] = clusters
    # -------- [6] PCA 降维 --------
    pca = PCA(n_components=2)
    df_pca = pd.DataFrame(
        pca.fit_transform(df_scaled),
        columns=['PC1', 'PC2'],
        index=sample_names
    )
    df_pca['簇标签'] = clusters
    # -------- [7] 聚类散点图 --------
    plt.figure(figsize=(10, 8))
    palette = sns.color_palette("tab10", len(set(clusters)))
    ax = sns.scatterplot(
        data=df_pca,
        x='PC1', y='PC2',
        hue='簇标签',
        palette=palette,
        s=50,
        edgecolor='black'
    )
    pca_centers = df_pca.groupby('簇标签')[['PC1', 'PC2']].mean()
    plt.scatter(pca_centers['PC1'], pca_centers['PC2'],
                s=120, c='black', marker='X', label='聚类中心')
    texts = []
    for i in range(df_pca.shape[0]):
        if abs(df_pca['PC1'].iloc[i]) + abs(df_pca['PC2'].iloc[i]) > 2.5:
            texts.append(
                plt.text(
                    df_pca['PC1'].iloc[i],
                    df_pca['PC2'].iloc[i],
                    sample_names[i],
                    fontsize=8
                )
            )

    adjust_text(texts, arrowprops=dict(arrowstyle='-', color='gray'))
    if title3:
        plt.title(title3, fontsize=14)
    plt.xlabel('PC1', fontsize=12)
    plt.ylabel('PC2', fontsize=12)
    plt.legend(title='簇标签', fontsize=10, loc='upper right')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("PCA降维聚类散点图.png", dpi=600)
    plt.show()

    # -------- [8] 导出聚类中心 --------
    cluster_centers = df_result.groupby('簇标签').mean(numeric_only=True).reset_index()
    center_file = '聚类中心.xlsx'
    cluster_centers.to_excel(center_file, index=False)
    print(f"✅ 聚类中心已保存为：{os.path.abspath(center_file)}")

    return df_result, n_clusters
def svm(df: pd.DataFrame,target_column: str,  # 新增参数，指定标签列名
        n_components: int = 2,  # PCA降维维度
        kernel: str = 'rbf',  # SVM核函数，可选 'linear'、'poly'、'rbf' 等
        C: float = 1.0,  # SVM正则化参数
        gamma: float = 'scale'  # SVM核系数，'scale' 为默认缩放方式
        ):
    '''
    SVM支持向量机
    '''
    from sklearn.svm import SVC
    # -------- [1] 拆分样本名、特征与标签 --------
    df = df.copy()
    sample_names = df.iloc[:, 0]  # 假设第一列为样本名称
    feature_columns = [col for col in df.columns if col != target_column and col != df.columns[0]]
    df_features = df[feature_columns]
    df_target = df[target_column]

    # -------- [2] 标准化 --------
    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df_features)

    # -------- [3] PCA降维（可选，用于可视化） --------
    pca = PCA(n_components=n_components)
    df_pca = pca.fit_transform(df_scaled)
    df_pca = pd.DataFrame(df_pca, columns=[f'PC{i + 1}' for i in range(n_components)], index=sample_names)
    df_pca['标签'] = df_target.values

    # -------- [4] 训练SVM模型 --------
    svm_model = SVC(kernel=kernel, C=C, gamma=gamma)
    svm_model.fit(df_scaled, df_target)

    # -------- [5] 预测（这里用训练集自身预测演示，实际可按需划分测试集） --------
    predictions = svm_model.predict(df_scaled)

    # -------- [6] 可视化分类结果（仅当n_components=2时做二维可视化） --------
    if n_components == 2:
        plt.figure(figsize=(10, 8))
        unique_labels = df_target.unique()
        palette = plt.cm.get_cmap('tab10', len(unique_labels))
        for i, label in enumerate(unique_labels):
            indices = df_target == label
            plt.scatter(df_pca.loc[indices, 'PC1'], df_pca.loc[indices, 'PC2'],
                        color=palette(i), label=f'标签_{label}', s=50, edgecolor='black')

        # 添加部分样本名称标签（离群点或远离中心点等，类似之前逻辑）
        texts = []
        for name in sample_names:
            pc1 = df_pca.loc[name, 'PC1']
            pc2 = df_pca.loc[name, 'PC2']
            if abs(pc1) + abs(pc2) > 2.5:  # 设定阈值筛选要标注的点
                texts.append(plt.text(pc1, pc2, name, fontsize=8))
        adjust_text(texts, arrowprops=dict(arrowstyle='-', color='gray'))

        plt.title('SVM分类结果可视化(PCA降维)', fontsize=14)
        plt.xlabel('PC1', fontsize=12)
        plt.ylabel('PC2', fontsize=12)
        plt.legend(fontsize=10, loc='upper right')
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig("svm_classification_scatter.png", dpi=600)
        plt.show()
    # -------- [7] 输出分类结果 --------
    classification_result = df.copy()
    classification_result['SVM预测标签'] = predictions
    classification_result.to_excel('svm_classification_result.xlsx', index=False)
    print(f"✅ 分类结果已保存为：{os.path.abspath('svm_classification_result.xlsx')}")

    return classification_result, svm_model











