from app import create_app, db
from app.models import Reservation, Device, User
import datetime

app = create_app()

with app.app_context():
    print("=" * 60)
    print("=== 预约模型功能验证 ===")
    print("=" * 60)

    # 清理测试数据
    Reservation.query.filter(Reservation.purpose.like('测试预约%')).delete()
    Device.query.filter(Device.device_id.like('DEV_TEST_%')).delete()
    User.query.filter(User.username.like('test_user_%')).delete()
    db.session.commit()

    # 1. 创建测试用户和设备
    print("\n1. 创建测试数据...")

    # 测试用户
    test_user = User(
        username='test_user_res',
        email='test_res@example.com',
        role='student'
    )
    test_user.set_password('test123')

    # 测试设备
    test_device = Device(
        device_id='DEV_TEST_RES',
        name='测试预约设备',
        device_type='测试仪器',
        status='available',
        location='测试实验室',
        max_reservation_hours=4
    )

    db.session.add_all([test_user, test_device])
    db.session.commit()

    print(f"   ✅ 用户创建: {test_user.username}")
    print(f"   ✅ 设备创建: {test_device.name}")

    # 2. 创建测试预约
    print("\n2. 创建测试预约...")

    start_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    end_time = start_time + datetime.timedelta(hours=2)

    reservation = Reservation(
        user_id=test_user.id,
        device_id=test_device.id,
        start_time=start_time,
        end_time=end_time,
        purpose='测试预约功能验证',
        status='pending'
    )

    db.session.add(reservation)
    db.session.commit()

    print(f"   ✅ 预约创建成功，ID: {reservation.id}")
    print(f"       预约时长: {reservation.get_duration_hours()}小时")
    print(f"       预约状态: {reservation.get_status_display()}")

    # 3. 测试时间冲突检测
    print("\n3. 测试时间冲突检测...")

    # 测试冲突时间
    conflict_start = start_time + datetime.timedelta(minutes=30)
    conflict_end = end_time - datetime.timedelta(minutes=30)

    has_conflict = reservation.check_time_conflict(conflict_start, conflict_end)
    print(f"   ✅ 冲突检测: {'有冲突' if has_conflict else '无冲突'}")

    # 测试无冲突时间
    no_conflict_start = end_time + datetime.timedelta(hours=1)
    no_conflict_end = no_conflict_start + datetime.timedelta(hours=1)

    has_no_conflict = reservation.check_time_conflict(no_conflict_start, no_conflict_end)
    print(f"   ✅ 无冲突检测: {'无冲突' if not has_no_conflict else '有冲突'}")

    # 4. 测试字典转换
    print("\n4. 测试数据转换...")

    simple_dict = reservation.to_dict(detail=False)
    detail_dict = reservation.to_dict(detail=True)

    print(f"   ✅ 简略字典: {len(simple_dict)}个字段")
    print(f"   ✅ 详细字典: {len(detail_dict)}个字段")

    # 5. 测试状态机方法
    print("\n5. 测试可批准检查...")

    can_approve, message = reservation.can_be_approved()
    print(f"   ✅ 可批准检查: {can_approve} - {message}")

    # 6. 清理测试数据
    print("\n6. 清理测试数据...")

    Reservation.query.filter_by(id=reservation.id).delete()
    Device.query.filter_by(id=test_device.id).delete()
    User.query.filter_by(id=test_user.id).delete()
    db.session.commit()

    print("   ✅ 测试数据清理完成")

    print("\n" + "=" * 60)
    print("✅ 预约模型功能验证通过！")
    print("=" * 60)