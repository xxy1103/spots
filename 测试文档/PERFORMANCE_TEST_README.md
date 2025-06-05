# 景点推荐算法性能测试说明

## 概述

本测试套件用于全面评测个性化旅游系统中两种景点推荐算法的性能：
- **传统算法**: K路归并排序算法
- **优化算法**: 基于IndexHeap的统一排序算法

## 测试文件说明

### 1. 全面性能测试 (`test_ultra_optimized_performance.py`)

**功能特点**:
- 全面的性能指标测量（执行时间、内存使用、CPU利用率）
- 结果一致性验证
- 多轮测试取平均值，减少随机误差
- 自动生成可视化图表和详细报告
- 支持多种数据规模测试

**测试指标**:
- ⏱️ 执行时间对比
- 🧠 内存使用分析
- 🎯 结果准确性验证
- 📊 性能提升倍数
- 📈 扩展性分析

### 2. 快速验证测试 (`quick_performance_test.py`)

**功能特点**:
- 轻量级快速测试
- 基本性能对比
- 适合开发阶段快速验证

### 3. 测试运行脚本 (`run_performance_test.py`)

**功能特点**:
- 统一的测试入口
- 支持命令行参数配置
- 两种测试模式选择

## 使用方法

### 快速测试

```bash
# 运行快速性能测试
python run_performance_test.py --mode quick
```

### 全面测试

```bash
# 运行全面性能测试（默认参数）
python run_performance_test.py --mode full

# 自定义测试参数
python run_performance_test.py --mode full --users 50 --iterations 5 --topk 5 10 20 50 100
```

### 直接运行

```bash
# 直接运行快速测试
python quick_performance_test.py

# 直接运行全面测试
python test_ultra_optimized_performance.py
```

## 命令行参数

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `--mode` | 测试模式 (quick/full) | quick | `--mode full` |
| `--users` | 测试用户数量 | 30 | `--users 50` |
| `--iterations` | 重复测试次数 | 3 | `--iterations 5` |
| `--topk` | TopK值列表 | [5,10,20,50] | `--topk 10 20 50` |

## 输出文件

全面测试完成后会生成以下文件：

1. **性能对比图表** (`comprehensive_performance_analysis.png`)
   - 执行时间对比柱状图
   - 性能提升倍数图
   - 内存使用对比图
   - 结果准确性分析图

2. **详细分析报告** (`detailed_performance_report.md`)
   - 完整的测试结果表格
   - 性能分析和建议
   - 算法适用场景推荐

3. **原始测试数据** (`performance_raw_data.json`)
   - 所有测试的原始数据
   - 便于后续分析和验证

## 测试原理

### 传统算法测试流程
1. 对每种用户喜好类型调用 `spotManager.getTopKByType()`
2. 使用K路归并算法合并排序结果
3. 提取前TopK个景点

### 优化算法测试流程
1. 创建IndexHeap堆结构
2. 遍历所有相关景点并插入堆中
3. 使用堆的getTopK方法获取结果

### 性能指标测量
- **执行时间**: 使用 `time.perf_counter()` 高精度计时
- **内存使用**: 使用 `tracemalloc` 和 `psutil` 监控内存
- **结果验证**: 比较两种算法返回结果的一致性

## 预期结果分析

### 理论预期
- **大规模数据**: 优化算法应该显著更快
- **小规模数据**: 传统算法可能因常数因子优势表现更好
- **内存使用**: 根据具体实现可能有所不同

### 实际影响因素
1. **数据规模**: 景点数量、用户喜好类型数量
2. **TopK值大小**: 影响堆操作和归并操作的效率
3. **系统环境**: CPU性能、内存大小、Python版本
4. **数据分布**: 景点评分分布、用户喜好分布

## 故障排除

### 常见问题

1. **ImportError**: 确保在项目根目录运行脚本
2. **ModuleNotFoundError**: 检查Python路径和模块导入
3. **内存不足**: 减少测试用户数量或TopK值
4. **图表显示问题**: 确保安装了matplotlib和支持中文字体

### 环境要求

```bash
# 必需的Python包
pip install numpy matplotlib psutil
```

## 自定义测试

### 添加新的测试场景

可以修改 `test_ultra_optimized_performance.py` 中的 `create_test_users()` 方法来创建特定的测试场景：

```python
def create_custom_test_users(self):
    """创建自定义测试用户"""
    test_users = [
        {'user_id': 'heavy_user', 'likes_type': ['自然风光', '人文历史', '美食特色', '休闲娱乐']},
        {'user_id': 'light_user', 'likes_type': ['自然风光']},
        # 添加更多测试场景...
    ]
    return test_users
```

### 添加新的性能指标

可以在 `PerformanceProfiler` 类中添加新的监控指标：

```python
def measure_cpu_usage(self):
    """测量CPU使用率"""
    import psutil
    return psutil.cpu_percent(interval=1)
```

## 注意事项

1. **测试环境**: 建议在相对空闲的系统上运行，避免其他程序干扰
2. **重复测试**: 多次运行测试以验证结果稳定性
3. **数据准备**: 确保测试数据充足且具有代表性
4. **结果解读**: 结合具体应用场景分析测试结果

---

**最后更新**: 2025年6月5日  
**版本**: v1.0
