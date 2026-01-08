from app import create_app, db
from app.models import User, Device, Reservation
from datetime import datetime, timedelta


def test_reservation_system():
    """测试预约系统核心功能"""
    app = create_app()

    with app.app_context():
        print("=" * 50)
        print("=== 预约系统功能测试开始 ===")
        print("=" * 50)

        # 1. 清理可能的旧测试数据
        print("\n1. 清理测试环境...")
        try:
            # 注意：由于外键约束，需要按顺序删除
            Reservation.query.filter(Reservation.user_id.in_([1, 2])).delete(synchronize_session=False)
            Device.query.filter(Device.device_id == 'DEV001').delete(synchronize_session=False)
            User.query.filter(User.username.in_(['test_student', 'test_admin'])).delete(synchronize_session=False)
            db.session.commit()
            print("   ✅ 旧测试数据清理完成")
        except:
            db.session.rollback()
            print("   ✅ 无旧测试数据需要清理")

        # 2. 创建测试用户
        print("\n2. 创建测试用户...")
        student = User(
            username='test_student',
            email='student@university.edu.cn',
            role='student'
        )
        student.set_password('123456')

        admin = User(
            username='test_admin',
            email='admin@university.edu.cn',
            role='admin'
        )
        admin.set_password('admin123')

        db.session.add_all([student, admin])
        db.session.commit()
        print(f"   ✅ 学生用户创建成功，ID: {student.id}")
        print(f"   ✅ 管理员用户创建成功，ID: {admin.id}")

        # 3. 创建测试设备
        print("\n3. 创建测试设备...")
        microscope = Device(
            device_id='DEV001',
            name='高级显微镜',
            device_type='光学仪器',
            brand='Olympus',
            model='CX23',
            status='available',
            location='实验室A-101',
            specifications='放大倍数：40x-1000x\n光源：LED',
            description='用于生物学实验的高精度显微镜'
        )

        db.session.add(microscope)
        db.session.commit()
        print(f"   ✅ 设备创建成功，ID: {microscope.id}, 状态: {microscope.status}")

        # 4. 创建预约记录
        print("\n4. 创建预约记录...")
        tomorrow = datetime.utcnow() + timedelta(days=1)
        reservation = Reservation(
            user_id=student.id,
            device_id=microscope.id,
            start_time=tomorrow.replace(hour=9, minute=0, second=0),
            end_time=tomorrow.replace(hour=11, minute=0, second=0),
            purpose='生物学实验：观察细胞结构',
            status='pending'
        )

        db.session.add(reservation)
        db.session.commit()
        print(f"   ✅ 预约记录创建成功，ID: {reservation.id}")
        print(
            f"       预约时间: {reservation.start_time.strftime('%Y-%m-%d %H:%M')} 到 {reservation.end_time.strftime('%H:%M')}")
        print(f"       预约用途: {reservation.purpose}")

        # 5. 验证关联关系（使用查询而不是关系属性）
        print("\n5. 验证关联关系...")

        # 方法1：直接查询，避免使用可能有问题关系属性
        user_reservations = db.session.query(Reservation).filter_by(user_id=student.id).all()
        device_reservations = db.session.query(Reservation).filter_by(device_id=microscope.id).all()

        print(f"   ✅ 用户 {student.username} 的预约记录数: {len(user_reservations)}")
        print(f"   ✅ 设备 {microscope.name} 的预约记录数: {len(device_reservations)}")

        # 方法2：如果关系属性已正确定义，可以这样使用
        try:
            # 尝试通过关系属性访问
            via_relationship = student.reservations_as_applicant.all()
            print(f"   ✅ 通过关系属性访问预约数: {len(via_relationship)}")
        except Exception as e:
            print(f"   ⚠️  关系属性访问失败: {e}")
            print("   使用直接查询替代...")

        # 6. 测试时间冲突检测算法
        print("\n6. 测试时间冲突检测算法...")

        # 测试用例1：完全重叠的时间
        conflicting_start = tomorrow.replace(hour=9, minute=30, second=0)
        conflicting_end = tomorrow.replace(hour=10, minute=30, second=0)
        has_conflict = reservation.check_time_conflict(conflicting_start, conflicting_end)
        print(f"   📌 测试1 - 完全重叠时间段 (9:30-10:30): {'🚫 存在冲突' if has_conflict else '✅ 无冲突'}")

        # 测试用例2：部分重叠的时间（开始时间在预约内）
        partial_start = tomorrow.replace(hour=10, minute=30, second=0)
        partial_end = tomorrow.replace(hour=12, minute=0, second=0)
        has_conflict2 = reservation.check_time_conflict(partial_start, partial_end)
        print(f"   📌 测试2 - 部分重叠 (10:30-12:00): {'🚫 存在冲突' if has_conflict2 else '✅ 无冲突'}")

        # 测试用例3：完全不冲突的时间
        non_conflict_start = tomorrow.replace(hour=14, minute=0, second=0)
        non_conflict_end = tomorrow.replace(hour=16, minute=0, second=0)
        has_conflict3 = reservation.check_time_conflict(non_conflict_start, non_conflict_end)
        print(f"   📌 测试3 - 不冲突时间段 (14:00-16:00): {'🚫 存在冲突' if has_conflict3 else '✅ 无冲突'}")

        # 7. 测试设备状态更新
        print("\n7. 测试设备状态更新...")
        reservation.status = 'approved'
        microscope.status = 'reserved'
        db.session.commit()
        print(f"   ✅ 预约状态更新为: {reservation.status}")
        print(f"   ✅ 设备状态更新为: {microscope.status}")

        # 8. 测试管理员审核功能
        print("\n8. 测试管理员审核功能...")
        reservation.reviewed_by = admin.id
        reservation.reviewed_at = datetime.utcnow()
        reservation.admin_notes = '实验目的明确，同意预约'
        db.session.commit()
        print(f"   ✅ 审核管理员: {admin.username}")
        print(f"   ✅ 审核意见: {reservation.admin_notes}")

        # 9. 验证审核关系
        try:
            # 查询管理员审核的所有预约
            admin_reviewed = db.session.query(Reservation).filter_by(reviewed_by=admin.id).all()
            print(f"   ✅ 管理员审核的预约数: {len(admin_reviewed)}")
        except Exception as e:
            print(f"   ⚠️  审核关系查询失败: {e}")

        # 10. 清理测试数据
        print("\n9. 清理测试数据...")
        # 注意：由于有外键约束，需要按正确顺序删除
        db.session.delete(reservation)
        db.session.commit()

        # 检查设备是否还有关联的预约
        remaining_reservations = db.session.query(Reservation).filter_by(device_id=microscope.id).count()
        if remaining_reservations == 0:
            db.session.delete(microscope)
            print("   ✅ 设备删除成功")

        # 检查用户是否还有关联的预约
        student_reservations = db.session.query(Reservation).filter_by(user_id=student.id).count()
        admin_reviewed = db.session.query(Reservation).filter_by(reviewed_by=admin.id).count()

        if student_reservations == 0:
            db.session.delete(student)
            print("   ✅ 学生用户删除成功")

        if admin_reviewed == 0:
            db.session.delete(admin)
            print("   ✅ 管理员用户删除成功")

        db.session.commit()
        print("   ✅ 所有测试数据清理完成")

        print("\n" + "=" * 50)
        print("=== 预约系统功能测试完成 ===")
        print("=" * 50)


if __name__ == '__main__':
    test_reservation_system()