import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram
from sklearn.datasets import make_blobs

# 1. 生成示例数据（3个聚类中心）
X, y_true = make_blobs(n_samples=30, centers=3, cluster_std=0.60, random_state=0)

# 2. 计算层次间距离（使用Ward方法，基于氏距离）
# linkage函数返回参数说明：
# - method：组间距离计算方式（'ward'/'single'/'complete'/'average'）
# - metric：样本本距离度量（'euclidean'/'manhattan'等）
Z = linkage(X, method='ward', metric='euclidean')

# 3. 设置绘图表样式（符合论文规范）
plt.style.use('seaborn-v0_8-whitegrid')
plt.figure(figsize=(10, 6))

# 4. 绘制谱系图
# dendrogram函数主要参数：
# - Z：linkage函数的输出结果
# - labels：样本标签（可选）
# - orientation：谱系图方向（'top'/'left'等）
# - distance_sort：距离排序方式（'descending'降序）
dendrogram(
    Z,
    leaf_rotation=90,  # 叶子节点标签旋转90度，避免重叠
    leaf_font_size=10,  # 叶子节点字体大小
    color_threshold=10,  # 颜色阈值，用于区分不同簇
    above_threshold_color='gray',  # 阈值以上的连接线颜色
    orientation='top'  # 谱系图从上到下绘制
)

# 5. 设置标题和标签
plt.title('Hierarchical Clustering Dendrogram', fontsize=14)
plt.xlabel('Sample Index', fontsize=12)
plt.ylabel('Distance', fontsize=12)

# 6. 调整布局并保存
plt.tight_layout()
plt.savefig('hierarchical_dendrogram.png', dpi=300, bbox_inches='tight')
plt.show()
