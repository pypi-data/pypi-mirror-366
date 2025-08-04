# sysinfo-collector

一个获取电脑系统信息的Python包。可以获取系统基本信息、CPU信息和内存信息。

## 功能特点

- 获取系统基本信息（操作系统、版本、架构等）
- 获取CPU信息（核心数、频率、使用率等）
- 获取内存信息（总内存、可用内存、使用率等）

## 安装方法

```bash
pip install sysinfo-collector
```

## 使用示例

```python
from sysinfo import get_system_info, get_cpu_info, get_memory_info

# 获取系统基本信息
system_info = get_system_info()
print("系统信息:", system_info)

# 获取CPU信息
cpu_info = get_cpu_info()
print("CPU信息:", cpu_info)

# 获取内存信息
memory_info = get_memory_info()
print("内存信息:", memory_info)
```

## 开发和贡献

1. 克隆仓库: `git clone https://github.com/yourusername/sysinfo-collector.git`
2. 安装依赖: `uv install`
3. 运行测试: `pytest`

欢迎提交issue和pull request。

## 许可证

本项目使用MIT许可证，详情见LICENSE文件。