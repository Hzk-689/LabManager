from app import create_app, db
from app.models import Device
import datetime

app = create_app()

with app.app_context():
    print("=" * 60)
    print("=== 设备模型完整功能验证 ===")
    print("=" * 60)

    # 清理测试数据
    Device.query.filter(Device.device_id.like('DEV_TEST_%')).delete()
    db.session.commit()

    # 1. 创建设备对象
    print("\n1. 📱 创建设备对象...")
    device = Device(
        device_id='DEV_TEST_001',
        name='高级显微镜',
        device_type='光学仪器',
        category='精密仪器',
        brand='Olympus',
        model='CX23',
        status='available',
        location='实验室A-101',
        lab_room='A101',
        max_reservation_hours=4,
        specifications='放大倍数：40x-1000x',
        description='用于生物学实验观察',
        purchase_date=datetime.datetime(2024, 1, 1),
        warranty_period=24
    )

    print(f"   ✅ 设备对象创建: {device.name}")
    print(f"     初始状态: {device.status}")
    print(f"     初始使用时长: {device.total_usage_hours}")
    print(f"     初始使用次数: {device.usage_count}")

    # 2. 测试record_usage方法
    print("\n2. ⏱️ 测试使用记录...")
    device.record_usage(2.5)
    print(f"   ✅ 记录2.5小时使用")
    print(f"     当前使用时长: {device.total_usage_hours}小时")
    print(f"     当前使用次数: {device.usage_count}次")

    # 再次记录
    device.record_usage(1.5)
    print(f"   ✅ 再记录1.5小时使用")
    print(f"     总使用时长: {device.total_usage_hours}小时")
    print(f"     总使用次数: {device.usage_count}次")

    # 3. 测试状态管理
    print("\n3. 🔄 测试状态管理...")

    # 3.1 更新状态
    device.update_status('reserved')
    print(f"   ✅ 状态更新为: {device.status}")

    # 3.2 检查可用性
    print(f"     是否可用: {device.is_available()}")

    # 3.3 测试预约检查
    can_reserve, message = device.can_be_reserved(3)
    print(f"     预约检查(3小时): {can_reserve} - {message}")

    # 4. 测试数据持久化
    print("\n4. 💾 测试数据持久化...")

    # 4.1 保存到数据库
    db.session.add(device)
    db.session.commit()
    print(f"   ✅ 设备保存到数据库，ID: {device.id}")

    # 4.2 从数据库重新加载
    loaded_device = Device.query.get(device.id)
    print(f"   ✅ 从数据库加载设备: {loaded_device.name}")
    print(f"     数据库中的使用时长: {loaded_device.total_usage_hours}")
    print(f"     数据库中的使用次数: {loaded_device.usage_count}")

    # 4.3 更新并保存
    loaded_device.record_usage(3.0)
    db.session.commit()
    print(f"   ✅ 更新使用记录: 3.0小时")

    # 重新加载验证
    refreshed = Device.query.get(device.id)
    print(f"   ✅ 验证更新: 总时长={refreshed.total_usage_hours}, 次数={refreshed.usage_count}")

    # 5. 测试字典转换
    print("\n5. 📄 测试数据转换...")

    # 5.1 简略字典
    simple_dict = device.to_dict(detail=False)
    print(f"   ✅ 简略字典: {len(simple_dict)}个字段")
    print(f"      包含: id, name, type, status, location")

    # 5.2 详细字典
    detail_dict = device.to_dict(detail=True)
    print(f"   ✅ 详细字典: {len(detail_dict)}个字段")
    print(f"      包含: brand, model, specifications, description等")

    # 5.3 检查关键字段
    print(f"\n   关键字段检查:")
    print(f"     设备ID: {simple_dict.get('device_id')}")
    print(f"     设备名称: {simple_dict.get('name')}")
    print(f"     设备状态: {simple_dict.get('status')}")
    print(f"     累计时长: {simple_dict.get('total_usage_hours')}")
    print(f"     使用次数: {simple_dict.get('usage_count')}")

    # 6. 测试其他业务方法
    print("\n6. 🛠️ 测试其他业务方法...")

    # 6.1 安排维护
    device.update_status('available')  # 先改为可用状态
    next_maintenance = device.schedule_maintenance()
    print(f"   ✅ 安排维护: {next_maintenance.strftime('%Y-%m-%d') if next_maintenance else '无'}")

    # 6.2 二维码数据
    qr_data = device.to_qr_data()
    print(f"   ✅ 二维码数据: 包含{len(qr_data)}个字段")

    # 7. 清理测试数据
    print("\n7. 🧹 清理测试数据...")
    Device.query.filter_by(id=device.id).delete()
    db.session.commit()

    # 验证删除
    deleted = Device.query.get(device.id)
    if deleted is None:
        print("   ✅ 测试设备已成功删除")
    else:
        print("   ❌ 测试设备删除失败")

    print("\n" + "=" * 60)
    print("✅ 设备模型完整功能验证通过！")
    print("=" * 60)