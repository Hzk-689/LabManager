import os
import shutil
import sys


def organize_tests_final():
    """最终整理测试文件"""
    print("=" * 60)
    print("=== 最终整理测试文件 ===")
    print("=" * 60)

    # 确保tests目录存在
    test_dirs = ['tests/unit', 'tests/integration', 'tests/e2e', 'tests/utils']
    for dir_path in test_dirs:
        os.makedirs(dir_path, exist_ok=True)
        with open(f"{dir_path}/__init__.py", 'w') as f:
            f.write("# Test package\n")

    # 文件映射：旧位置 -> 新位置
    file_mapping = [
        # 单元测试
        ('test_device_simple.py', 'tests/unit/test_device_basic.py'),
        ('test_device_full.py', 'tests/unit/test_device_model.py'),
        ('test_reservation_model.py', 'tests/unit/test_reservation_model.py'),

        # 集成测试
        ('test_devices_api.py', 'tests/integration/test_devices_api.py'),
        ('test_reservation.py', 'tests/integration/test_reservations_api.py'),

        # 端到端测试
        ('test_reservation_full_system.py', 'tests/e2e/test_reservation_workflow.py'),

        # 工具脚本
        ('verify_blueprints_full.py', 'tests/utils/verify_blueprints.py'),
    ]

    moved_count = 0
    skipped_count = 0

    print("\n📁 整理测试文件:")
    for src, dst in file_mapping:
        if os.path.exists(src):
            try:
                shutil.move(src, dst)
                moved_count += 1
                print(f"  ✅ 移动: {src:30} → {dst}")
            except Exception as e:
                print(f"  ⚠️  跳过: {src} (移动失败: {e})")
                skipped_count += 1
        else:
            print(f"  ⚠️  不存在: {src}")

    # 删除临时文件
    print("\n🗑️ 删除临时文件:")
    files_to_delete = [
        'debug_device_model.py',
        'organize_tests.py',
        'test_import.py',
        'verify_blueprints.py',
    ]

    deleted_count = 0
    for file in files_to_delete:
        if os.path.exists(file):
            try:
                os.remove(file)
                deleted_count += 1
                print(f"  ✅ 删除: {file}")
            except Exception as e:
                print(f"  ⚠️  删除失败: {file} ({e})")
        else:
            print(f"  ℹ️  不存在: {file}")

    print(f"\n📊 整理结果:")
    print(f"  - 移动文件: {moved_count} 个")
    print(f"  - 跳过文件: {skipped_count} 个")
    print(f"  - 删除文件: {deleted_count} 个")

    # 显示整理后的结构
    print("\n📁 最终测试结构:")
    for root, dirs, files in os.walk("tests"):
        level = root.replace("tests", "").count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 2 * (level + 1)
        for file in files[:5]:  # 最多显示5个文件
            if file.endswith(".py") and not file.startswith("__"):
                print(f"{subindent}{file}")
        if len(files) > 5:
            print(f"{subindent}... 还有 {len(files) - 5} 个文件")

    print("\n" + "=" * 60)
    print("✅ 测试文件整理完成！")
    print("=" * 60)

    return True


if __name__ == "__main__":
    organize_tests_final()