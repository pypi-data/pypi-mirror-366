import numpy as np
from scipy import stats

def bool_1d(x_sel, x_all): 
    
    idx = []
    for x0 in x_all:
        if x0 in x_sel:
            idx.append(True)
        else:
            idx.append(False) 
    idx = np.array(idx).squeeze()
    
    return idx


def ttest_3d(matrix1, matrix2, axis=0, equal_var=False):
    """
    对两个三维矩阵沿指定维度进行独立样本t检验，返回p值矩阵
    
    参数：
    matrix1 (np.ndarray) : 第一个三维数据矩阵
    matrix2 (np.ndarray) : 第二个三维数据矩阵
    axis (int)          : 沿哪个维度进行检验 (0/1/2)
    equal_var (bool)    : 是否假设方差齐性，默认False（使用Welch's t-test）
    
    返回：
    p_values (np.ndarray) : p值矩阵，维度比输入少一维
    
    示例：
    >>> A = np.random.randn(10, 20, 30)  # 维度0有10个样本
    >>> B = np.random.randn(15, 20, 30)  # 维度0有15个样本
    >>> p = ttest_3d(A, B, axis=0)       # 沿样本维度检验
    >>> p.shape
    (20, 30)
    """
    # 验证输入维度
    if matrix1.ndim != 3 or matrix2.ndim != 3:
        raise ValueError("输入必须是三维矩阵")
    
    # 验证非检验维度的一致性
    target_shape = [s for i, s in enumerate(matrix1.shape) if i != axis]
    compare_shape = [s for i, s in enumerate(matrix2.shape) if i != axis]
    if target_shape != compare_shape:
        raise ValueError(f"非检验维度不匹配: {target_shape} vs {compare_shape}")
    
    # 执行t检验
    _, p_values = stats.ttest_ind(matrix1, matrix2, axis=axis, equal_var=equal_var)
    
    return p_values


def fisher_exact_3d(arr1, arr2, axis=0, alternative='two-sided'):
    """
    对两个三维数组在指定维度进行费希尔精确检验

    参数：
    - arr1, arr2: 三维numpy数组，允许包含NaN
    - axis: 指定检验维度 (0/1/2)
    - alternative: 检验方向，可选['two-sided', 'less', 'greater']

    返回：
    - p_values: 二维数组，非检验维度的组合结果，全NaN位置返回NaN
    """
    # 输入校验
    if arr1.ndim != 3 or arr2.ndim != 3:
        raise ValueError("输入必须是三维数组")
    if axis not in {0, 1, 2}:
        raise ValueError("axis参数必须是0、1或2")
    if alternative not in ['two-sided', 'less', 'greater']:
        raise ValueError("alternative参数必须是['two-sided', 'less', 'greater']之一")

    # 校验非检验维度的一致性
    non_axis_dims = [i for i in range(3) if i != axis]
    if (arr1.shape[non_axis_dims[0]] != arr2.shape[non_axis_dims[0]]) or \
       (arr1.shape[non_axis_dims[1]] != arr2.shape[non_axis_dims[1]]):
        raise ValueError(f"非axis维度{non_axis_dims}必须一致")

    # 准备结果数组
    result_shape = tuple(arr1.shape[i] for i in non_axis_dims)
    p_values = np.full(result_shape, np.nan)
    
    # 遍历所有二维位置
    for idx in np.ndindex(result_shape):
        # 构建三维索引切片
        def get_sliced_data(arr):
            slice_idx = list(idx)
            slice_idx.insert(axis, slice(None))  # 在检验维度取全部数据
            return arr[tuple(slice_idx)].flatten()
        
        data1, data2 = map(get_sliced_data, [arr1, arr2])

        # 跳过全NaN的情况
        if np.all(np.isnan(data1)) or np.all(np.isnan(data2)):
            continue

        # 计算有效样本统计量
        def count_valid(data):
            valid_data = data[~np.isnan(data)]
            return len(valid_data), np.sum(valid_data)
        
        n1, s1 = count_valid(data1)
        n2, s2 = count_valid(data2)

        # 构建列联表
        contingency_table = [
            [s1, n1 - s1],
            [s2, n2 - s2]
        ]

        # 执行检验
        try:
            _, p_val = stats.fisher_exact(contingency_table, alternative=alternative)
            p_values[idx] = p_val
        except (ValueError, ZeroDivisionError):  # 处理无效表格
            pass

    return p_values


def bootstrap_mean_test(x, y, n_bootstraps=10000, confidence_level=0.95, alternative='two-sided'):
    """
    使用Bootstrap方法检验两个样本均值差异的显著性
    
    参数:
        x, y: 两组样本数据 (array-like)
        n_bootstraps: Bootstrap抽样次数 (默认10000)
        confidence_level: 置信水平 (默认0.95)
        alternative: 检验方向 
            'two-sided' - 双侧检验 (默认)
            'less' - 左尾检验 (x_mean < y_mean)
            'greater' - 右尾检验 (x_mean > y_mean)
    
    返回:
        result: 包含结果的字典
            'observed_diff': 观察到的均值差异 (x_mean - y_mean)
            'p_value': Bootstrap p值
            'conf_interval': 均值差异的置信区间
            'bootstrap_diffs': 所有Bootstrap样本的均值差异
            'effect_size': Cohen's d效应量
    """
    # 转换为numpy数组
    x = np.asarray(x)
    y = np.asarray(y)
    
    # 计算观察到的均值差异
    observed_diff = np.mean(x) - np.mean(y)
    
    # 存储所有Bootstrap样本的均值差异
    bootstrap_diffs = np.zeros(n_bootstraps)
    
    # 创建合并数据用于原假设下的抽样
    combined = np.concatenate([x, y])
    n_x = len(x)
    n_y = len(y)
    
    # 执行Bootstrap抽样
    for i in range(n_bootstraps):
        # 在原假设下抽样（假设两样本来自同一分布）
        resampled_combined = np.random.choice(combined, size=n_x + n_y, replace=True)
        resampled_x = resampled_combined[:n_x]
        resampled_y = resampled_combined[n_x:]
        
        # 计算该次抽样的均值差异
        bootstrap_diffs[i] = np.mean(resampled_x) - np.mean(resampled_y)
    
    # 计算p值
    if alternative == 'two-sided':
        # 计算比观察值更极端的比例（绝对值）
        p_value = np.mean(np.abs(bootstrap_diffs) >= np.abs(observed_diff))
    elif alternative == 'less':
        # 左尾检验：差异小于等于观察值
        p_value = np.mean(bootstrap_diffs <= observed_diff)
    elif alternative == 'greater':
        # 右尾检验：差异大于等于观察值
        p_value = np.mean(bootstrap_diffs >= observed_diff)
    else:
        raise ValueError("alternative必须为 'two-sided', 'less' 或 'greater'")
    
    # 计算置信区间（百分位数法）
    alpha = (1 - confidence_level) * 100
    conf_interval = np.percentile(bootstrap_diffs, [alpha/2, 100 - alpha/2])
    
    # 计算效应量 (Cohen's d)
    pooled_std = np.sqrt(((len(x)-1)*np.var(x, ddof=1) + (len(y)-1)*np.var(y, ddof=1)) / (len(x)+len(y)-2))
    effect_size = observed_diff / pooled_std
    
    # 封装结果
    result = {
        'observed_diff': observed_diff,
        'p_value': p_value,
        'conf_interval': conf_interval,
        'bootstrap_diffs': bootstrap_diffs,
        'effect_size': effect_size
    }
    
    return result

