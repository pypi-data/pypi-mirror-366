# GEMINI.md

This file provides guidance to Gemini when working with code in this repository.

## 项目概述

这是一个支持多领域的航测数据处理和自动化报告生成工具（AeroSpot AutoReport V3）。项目采用插件化架构，目前支持水质监测领域，可扩展到农业、环境监测等其他领域。

## 🏗️ 核心架构

### 插件化领域架构
```
src/autoreport/
├── domains/                    # 🔌 领域插件系统
│   ├── base/                   # 基础接口定义
│   │   ├── domain_interface.py # 领域处理器接口
│   │   ├── indicator.py        # 指标定义基类
│   │   └── report_template.py  # 报告模板基类
│   │
│   └── water_quality/          # 水质领域实现
│       ├── domain.py           # 水质领域处理器
│       ├── indicators.py       # 水质指标定义和GB标准
│       ├── standards.py        # 水质标准(GB 3838-2002)
│       └── report_template.py  # 水质专用报告模板
│
├── processor/                  # 通用数据处理模块
│   ├── data/processor.py      # 多领域数据处理器
│   ├── config.py              # 多领域配置生成器
│   ├── maps.py                # 卫星图像和可视化
│   └── extractor.py           # 数据解压提取
│
├── document/                  # 通用文档生成组件
├── utils/                     # 通用工具函数
├── config/                    # 全局配置管理
└── main.py                    # 主程序入口
```

### 领域扩展模式
- **接口驱动**: 所有领域实现统一的`DomainInterface`接口
- **配置驱动**: 通过`domain`字段选择应用领域
- **插件注册**: 自动发现和注册领域处理器
- **模板系统**: 每个领域可定制专用报告模板

### 数据处理流程
1. **领域初始化**: 根据配置加载特定领域处理器
2. **资源下载**: 从远程服务器获取数据和图像资源
3. **数据提取**: 解压ZIP文件，提取INDEXS.CSV、POS.TXT等
4. **领域处理**: 使用领域特定逻辑处理和标准化数据
5. **分析建模**: 执行领域特定的数据分析和建模
6. **可视化**: 生成领域相关的图表和地图
7. **报告生成**: 使用领域模板生成专业Word报告

### 主要依赖
- **领域特定**:
  - `autowaterqualitymodeler`: 水质建模核心库
- **通用依赖**:
  - `python-docx`: Word文档生成
  - `pandas/numpy`: 数据处理
  - `matplotlib/seaborn`: 数据可视化
  - `opencv-python`: 图像处理
  - `spire-doc`: 文档水印功能

## 常用命令

### 运行项目
```bash
# 运行水质分析（默认领域）
uv run python interface.py test.json

# 明确指定领域
uv run python interface.py test.json --domain water_quality

# 使用管道输入配置文件路径
cat path.txt | uv run python interface.py

# 直接运行主程序
uv run python src/autoreport/main.py test.json --domain water_quality

# 查看可用领域
uv run python -c "from autoreport.domains import list_domains; print(list_domains())"
```

### 开发环境
```bash
# 安装开发依赖
pip install -e .[dev]

# 运行测试
pytest

# 代码格式化
black src/

# 类型检查
mypy src/
```

### 缓存控制
在 `interface.py` 中修改 `CACHE_ENABLED` 变量控制资源下载缓存：
- `True`: 启用缓存，重复运行时使用缓存文件
- `False`: 禁用缓存，每次重新下载资源

## 配置文件格式

项目使用JSON配置文件（如test.json），主要包含：

### 基础配置
- `domain`: 应用领域（"water_quality", "agriculture"等）
- `data_root`: 输出目录路径
- `company_info`: 公司信息和资源URL
  - 各种资源的OSS下载链接（logo、卫星图、航线图、数据文件等）
  - 地理边界坐标（north_east, south_west等）
  - 水印配置

### 领域特定配置
- `domain_config`: 领域专用配置
  - `enabled_indicators`: 启用的指标列表
  - `quality_standards`: 质量标准（如"GB_3838_2002"）
  - `analysis_methods`: 分析方法

### 配置示例
```json
{
    "domain": "water_quality",
    "data_root": "./AutoReportResults/",
    "company_info": { ... },
    "domain_config": {
        "enabled_indicators": ["nh3n", "tp", "cod", "turbidity", "chla"],
        "quality_standards": "GB_3838_2002",
        "analysis_methods": ["spectral_modeling", "interpolation"]
    }
}
```

## 输出结构

程序在指定目录下创建时间戳子目录，包含：
- `reports/`: 生成的Word报告和配置文件
- `maps/`: 各指标的分布图、插值图、等级图
- `logs/`: 运行日志
- `extracted/`: 解压的数据文件
- `uav_data/`: 处理后的无人机数据
- `predict/`: 模型预测结果
- `models/`: 加密保存的模型文件

## 开发注意事项

### 插件化开发
- **新增领域**: 在`domains/`下创建新目录，实现`DomainInterface`接口
- **指标定义**: 使用`IndicatorDefinition`类定义领域指标
- **报告模板**: 继承`ReportTemplate`基类创建领域专用模板
- **自动注册**: 新领域会自动注册到插件系统

### 领域实现指南
```python
# 实现新领域的最小示例
class NewDomain(DomainInterface):
    @property
    def domain_name(self) -> str:
        return "new_domain"
    
    def get_indicators(self) -> Dict[str, IndicatorDefinition]:
        return {"indicator1": IndicatorDefinition(...)}
    
    def process_analysis_data(self, ...):
        # 领域特定的分析逻辑
        return analysis_result
```

### 架构优势
- **领域解耦**: 各领域独立开发，互不影响
- **配置驱动**: 通过配置文件切换领域
- **接口统一**: 所有领域遵循相同接口规范
- **模板系统**: 支持领域专用报告模板

### 错误处理
- 使用 `@safe_operation` 装饰器进行错误处理
- 自定义异常类型在 `exceptions.py` 中定义
- 统一的日志配置在 `log_config.py` 中

### 数据标准化
- **领域特定标准化**: 每个领域可定义自己的标准化逻辑
- **指标名称映射**: 通过`IndicatorDefinition`的aliases实现
- **单位管理**: 领域处理器负责指标单位的获取

### 依赖管理
- 使用 `uv.lock` 进行精确的依赖版本锁定
- 支持条件依赖（如Windows特定的pywin32）
- 开发依赖通过 `[dev]` 选项安装

## 测试

测试文件位于根目录，包含：
- `test_numerical_stability.py`: 数值稳定性测试
- `test_performance_comparison.py`: 性能对比测试
- `test_gps_alignment.py`: GPS对齐测试

运行测试：
```bash
pytest
```

## 调试

查看详细日志：
- 运行日志保存在输出目录的 `logs/` 文件夹
- 使用 `logging` 模块进行日志记录
- 不同级别的日志信息用于调试和监控
