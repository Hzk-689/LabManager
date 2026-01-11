# test_device_simple.py
import sys
import os

# 添加项目路径
sys.path.insert(0, os.getcwd())

from datetime import datetime
from app.models import Device

# 创建一个Device实例，不依赖数据库
print("=== 测试Device模型（独立模式）===")

# 创建设备对象
device = Device(
    device_id='TEST001',
    name='显微镜',
    device_type='光学仪器',
    status='available'
)

print(f"1. 设备创建: {device.name}")
print(f"   total_usage_hours初始值: {device.total_usage_hours}")
print(f"   usage_count初始值: {device.usage_count}")

# 测试record_usage方法
try:
    device.record_usage(2.5)
    print("2. ✅ record_usage成功！")
    print(f"   累计时长: {device.total_usage_hours}")
    print(f"   使用次数: {device.usage_count}")
except Exception as e:
    print(f"2. ❌ record_usage失败: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# 测试to_dict方法
try:
    data = device.to_dict()
    print(f"3. ✅ to_dict成功，字段数: {len(data)}")
except Exception as e:
    print(f"3. ❌ to_dict失败: {e}")

print("=== 测试完成 ===")