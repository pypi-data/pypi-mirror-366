from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import math
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from matplotlib.dates import DateFormatter, MonthLocator,DayLocator
import matplotlib as mpl
from matplotlib.ticker import MultipleLocator
import numpy as np
from . import corr
from .corr import positivation,normalize

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
def calculate_metrics(df, actual_col, pred_col, file_name='指标结果.xlsx'):
    """
    计算两列数据（实际值列和预测值列）之间的评估指标，输出指标表格并支持导出Excel
    参数:
        df: pandas.DataFrame，包含实际值和预测值的数据框
        actual_col: str，实际值列的列名（如'实际销量'）
        pred_col: str，预测值列的列名（如'预测销量'）
        output_excel: str，输出Excel文件路径
    返回:
        result_df: pandas.DataFrame，包含评估指标的结果表格
    """
    # 检查输入列是否存在
    if actual_col not in df.columns:
        raise ValueError(f"数据中不存在实际值列：{actual_col}")
    if pred_col not in df.columns:
        raise ValueError(f"数据中不存在预测值列：{pred_col}")

    # 剔除含有缺失值的行
    df_clean = df.dropna(subset=[actual_col, pred_col]).copy()

    # 提取实际值和预测值
    y_actual = df_clean[actual_col]
    y_pred = df_clean[pred_col]

    # 计算评估指标
    # 处理特殊情况：避免实际值和预测值完全相同时的计算警告
    if y_actual.nunique() == 1 and y_pred.nunique() == 1:
        r2 = 1.0 if y_actual.iloc[0] == y_pred.iloc[0] else 0.0
    else:
        r2 = r2_score(y_actual, y_pred)

    mse = mean_squared_error(y_actual, y_pred)
    rmse = math.sqrt(mse)
    mae = mean_absolute_error(y_actual, y_pred)
    mape = (abs((y_actual - y_pred) / y_actual).mean() * 100) if (y_actual != 0).all() else None  # 避免除以0

    # 整理结果
    results = [
        ['R²', round(r2, 4)],
        ['MSE', round(mse, 4)],
        ['RMSE', round(rmse, 4)],
        ['MAE', round(mae, 4)]
    ]
    if mape is not None:
        results.append(['MAPE(%)', round(mape, 2)])  # 增加MAPE指标（百分比）

    # 转换为DataFrame
    result_df = pd.DataFrame(results, columns=['指标', '值'])

    # 打印指标
    print(f"===== {actual_col} 与 {pred_col} 的评估指标 =====")
    print(result_df.to_string(index=False))  # 不显示行索引

    # 导出到Excel
    if file_name:
        try:
            result_df.to_excel(file_name, index=False)
            print(f"\n指标已保存至：{file_name}")
        except Exception as e:
            print(f"\n导出Excel失败：{str(e)}")

    return result_df
def time_series_decomposition(df, index_col:str=None, period=365, model='additive', split=False):
    """
    时间序列分解
    对 DataFrame 中的每列时间序列数据进行分解并绘图
    参数:
        df: pandas.DataFrame，索引或第一列为 datetime 类型，列为待分析的时间序列
        period: int，时间序列的周期
        model: str，分解模型，'additive'（加法）或 'multiplicative'（乘法），默认 'additive'
        split: bool，是否将四个子图分开展显示，默认False（合并显示）
    """
    if index_col is None:
        index_col=df.columns[0]
        df.set_index(df.columns[0],inplace=True)
    else:
        df.set_index(index_col,inplace=True)
    df.index=pd.to_datetime(df.index)
    # 遍历每列数据进行分解
    for col in df.columns:
        # 提取单列数据并去除缺失值
        ts_data = df[col].dropna()  # 去除可能的缺失值

        # 时间序列分解
        decomposition = seasonal_decompose(ts_data, model=model, period=period)

        # 定义更浅的颜色
        color_original = (169/255, 214/255, 220/255)  # 浅蓝色
        color_trend = (246/255, 199/255, 206/255)     # 浅粉色
        color_seasonal = (245/255, 209/255, 202/255)   # 浅橙色
        color_residual = (215/255, 194/255, 217/255)   # 浅紫色

        # 定义图表数据
        plots = [
            {
                'data': (ts_data.index, ts_data),
                'color': color_original,
                'label': 'Original',
                'title': f'{col}时间序列分解'
            },
            {
                'data': (decomposition.trend.index, decomposition.trend),
                'color': color_trend,
                'label': 'Trend',
                'title': ''
            },
            {
                'data': (decomposition.seasonal.index, decomposition.seasonal),
                'color': color_seasonal,
                'label': 'Seasonal',
                'title': ''
            },
            {
                'data': (decomposition.resid.index, decomposition.resid),
                'color': color_residual,
                'label': 'Residual',
                'title': ''
            }
        ]

        if not split:
            # 合并显示：4个子图纵向排列
            fig, axes = plt.subplots(4, 1, figsize=(16, 12), dpi=300, sharex=True)
            fig.suptitle(f'{col}销量时间序列分解', fontsize=16)

            for i, plot in enumerate(plots):
                x, y = plot['data']
                axes[i].plot(x, y, color=plot['color'], label=plot['label'])
                axes[i].grid(axis='x', linestyle='--', alpha=0.7)  # 横向网格
                axes[i].grid(axis='y', linestyle='--', alpha=0.3)  # 纵向网格
                axes[i].legend()

                # 残差图添加零线
                if i == 3:
                    axes[i].axhline(y=0, color='black', linestyle='-', alpha=0.3)

            # 设置x轴：每60天显示一个主刻度（核心修改）
            axes[-1].xaxis.set_major_locator(DayLocator(interval=60))  # 每60天一个主刻度
            axes[-1].xaxis.set_major_formatter(DateFormatter('%Y-%m'))  # 日期格式
            plt.xticks(rotation=45)

            plt.tight_layout(rect=[0, 0, 1, 0.96])
            plt.show()
        else:
            # 分开放置：每个子图单独显示
            for plot in plots:
                x, y = plot['data']
                fig, ax = plt.subplots(figsize=(16, 4), dpi=300)
                ax.plot(x, y, color=plot['color'], label=plot['label'])

                # 仅原始数据图显示标题
                if plot['label'] == 'Original':
                    ax.set_title(plot['title'], fontsize=14)

                ax.grid(axis='x', linestyle='--', alpha=0.7)
                ax.grid(axis='y', linestyle='--', alpha=0.3)
                ax.legend()

                # 残差图添加零线
                if plot['label'] == 'Residual':
                    ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)

                # 设置x轴：每60天显示一个主刻度（核心修改）
                ax.xaxis.set_major_locator(DayLocator(interval=60))  # 每60天一个主刻度
                ax.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
                plt.xticks(rotation=45)

                plt.tight_layout()
                plt.show()
def grey_relation_analysis(df, target_col, output_excel='灰色关联度表格'):
    """
    灰色关联分析
    对df中的目标列对其他列计算关联度
    输入:df和目标列名
    输出:灰色关联度表格
    """
    # 数据预处理
    if target_col not in df.columns:
        raise ValueError(f"数据中不存在目标列：{target_col}")

    # 提取数值型列并处理缺失值
    numeric_df = df.select_dtypes(include=[np.number]).dropna()
    if numeric_df.empty:
        raise ValueError("数据中没有有效的数值型列（可能全为缺失值或非数值）")

    if target_col not in numeric_df.columns:
        raise ValueError(f"目标列 {target_col} 不是数值型列或已被过滤（可能含缺失值）")

    # 分离参考序列和比较序列
    reference = numeric_df[target_col].values.reshape(-1, 1)
    compare_cols = [col for col in numeric_df.columns if col != target_col]
    if not compare_cols:
        raise ValueError("除目标列外，没有其他可分析的指标列")

    compare_matrix = numeric_df[compare_cols].values

    # 归一化（优化：增加防除零处理）
    def normalize(data):
        min_val = np.min(data, axis=0)
        max_val = np.max(data, axis=0)
        # 处理最大值等于最小值的情况（避免除零）
        range_val = np.where(max_val == min_val, 1, max_val - min_val)
        return (data - min_val) / range_val

    ref_norm = normalize(reference)
    comp_norm = normalize(compare_matrix)

    # 计算关联系数（优化：处理异常值）
    abs_diff = np.abs(comp_norm - ref_norm)
    min_min = np.nanmin(abs_diff)  # 使用nanmin忽略可能的NaN
    max_max = np.nanmax(abs_diff)
    rho = 0.5

    # 避免分母为零
    denominator = abs_diff + rho * max_max
    denominator = np.where(denominator == 0, 1e-10, denominator)
    correlation_coeff = (min_min + rho * max_max) / denominator

    # 计算关联度（优化：过滤NaN值）
    relation_degree = np.nanmean(correlation_coeff, axis=0)

    # 处理可能的异常关联度值
    relation_degree = np.clip(relation_degree, 0, 1)  # 关联度限制在[0,1]范围
    relation_degree = np.nan_to_num(relation_degree, nan=0.0)  # 将NaN替换为0

    # 整理结果
    result = pd.DataFrame({
        '指标名称': compare_cols,
        '关联度': relation_degree.round(4)
    })

    # 修复排名计算（处理可能的NaN值）
    result['排名'] = result['关联度'].rank(
        ascending=False,
        method='min',
        na_option='bottom'  # 将NaN值排在最后
    ).astype(int)

    # 排序并重置索引
    result = result.sort_values(by='关联度', ascending=False).reset_index(drop=True)

    # 打印结果
    print(f"===== 与 '{target_col}' 的灰色关联度分析结果 =====")
    print(result.to_string(index=False))

    # 导出到Excel
    if output_excel:
        try:
            result.to_excel(output_excel+'.xlsx', index=False)
            print(f"\n结果已保存至：{output_excel}")
        except Exception as e:
            print(f"\n导出Excel失败：{str(e)}")

    return result
def entropy_weight(normalized_array:np.ndarray):
    normalized_array = np.where(normalized_array == 0, 1e-10, normalized_array)
    p = normalized_array / np.sum(normalized_array, axis=0)  # 按列求和
    n_samples = normalized_array.shape[0]
    e = - (1 / np.log(n_samples)) * np.sum(p * np.log(p), axis=0)  # 按列求和
    weights = (1 - e) / np.sum(1 - e)
    return weights
def entropy_weight_method(df:pd.DataFrame,file_name:str='熵权法权重'):
    print("原始数据：")
    print(df.head())
    indicators = df.iloc[:, 1:].values
    indicator_names = df.iloc[:, 1:].columns.tolist()
    posited_data = positivation(indicators)
    normalized_data = normalize(posited_data)
    weights = entropy_weight(normalized_data)
    print("\n各指标的权重：")
    res = dict(zip(indicator_names, weights))
    print(res)
    df_result = pd.DataFrame(res, index=['权重'])
    df_result.to_excel(file_name+'.xlsx')

if __name__ == "__main__":
    df = pd.read_excel('分析指标.xlsx')  # 替换为你的文件路径



if __name__ == '__main__':
    df=pd.read_excel('示例数据.xlsx')
    grey_relation_analysis(df,'水生根茎类')