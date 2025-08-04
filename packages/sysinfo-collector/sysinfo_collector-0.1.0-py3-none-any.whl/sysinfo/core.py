import psutil
import platform
import sys

def get_system_info():
    """获取系统基本信息"""
    info = {
        "system": platform.system(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
    }
    return info


def get_cpu_info():
    """获取CPU信息"""
    cpu_info = {
        "physical_cores": psutil.cpu_count(logical=False),
        "total_cores": psutil.cpu_count(logical=True),
        "cpu_freq_current": psutil.cpu_freq().current if psutil.cpu_freq() else None,
        "cpu_freq_min": psutil.cpu_freq().min if psutil.cpu_freq() else None,
        "cpu_freq_max": psutil.cpu_freq().max if psutil.cpu_freq() else None,
        "cpu_percent": psutil.cpu_percent(interval=1, percpu=True),
    }
    return cpu_info


def get_memory_info():
    """获取内存信息"""
    memory = psutil.virtual_memory()
    memory_info = {
        "total": memory.total,
        "available": memory.available,
        "used": memory.used,
        "percent": memory.percent,
    }
    return memory_info