from app import create_app, db
from sqlalchemy import inspect
import os

app = create_app()

with app.app_context():
    print("=" * 60)
    print("=== 实验室设备管理系统 - 数据库初始化 ===")
    print("=" * 60)

    # 1. 检查当前环境
    print(f"📁 工作目录: {os.getcwd()}")
    print(f"📁 数据库文件位置: app.db")

    # 2. 显示模型定义
    expected_tables = ['users', 'devices', 'reservations']
    print(f"\n📊 期望创建的表: {expected_tables}")

    # 3. 清理旧表
    print("\n🧹 步骤 1/4: 清理旧表结构...")
    try:
        db.drop_all()
        print("   ✅ 旧表清理完成")
    except Exception as e:
        print(f"   ⚠️  清理时出现警告: {e}")

    # 4. 创建新表
    print("\n🛠️ 步骤 2/4: 创建新表...")
    try:
        db.create_all()
        print("   ✅ 新表创建完成")
    except Exception as e:
        print(f"   ❌ 创建表时出错: {e}")
        exit(1)

    # 5. 验证结果
    print("\n🔍 步骤 3/4: 验证创建结果...")
    inspector = inspect(db.engine)
    actual_tables = inspector.get_table_names()

    print(f"   📋 数据库中的实际表 ({len(actual_tables)}个): {actual_tables}")

    # 6. 详细检查每个表
    print("\n📊 步骤 4/4: 检查表结构...")
    success_count = 0

    for table_name in expected_tables:
        if table_name in actual_tables:
            columns = inspector.get_columns(table_name)
            print(f"   ✅ {table_name}: 有 {len(columns)} 个字段")
            # 显示前3个字段作为示例
            for i, col in enumerate(columns[:3]):
                print(f"      {i + 1}. {col['name']} ({str(col['type'])})")
            if len(columns) > 3:
                print(f"      ... 还有 {len(columns) - 3} 个字段")
            success_count += 1
        else:
            print(f"   ❌ {table_name}: 未找到")

    # 7. 最终报告
    print("\n" + "=" * 60)
    if success_count == len(expected_tables):
        print("🎉 成功！所有表都已正确创建。")
        print("   你现在可以运行测试脚本了：")
        print("   python test_reservation.py")
    else:
        print(f"⚠️  部分成功：创建了 {success_count}/{len(expected_tables)} 个表")

    # 8. 文件系统验证
    db_file = 'app.db'
    if os.path.exists(db_file):
        size = os.path.getsize(db_file)
        print(f"💾 数据库文件: {db_file} ({size} 字节)")
    else:
        print("❌ 数据库文件未创建")

    print("=" * 60)