import os
import sys


def verify_test_structure():
    print("=" * 60)
    print("=== 测试文件结构验证 ===")
    print("=" * 60)

    # 1. 检查根目录
    print("\n1. 检查根目录:")
    root_files = [f for f in os.listdir('.')
                  if f.endswith('.py') and not f.startswith('__')]

    test_files_in_root = []
    for file in root_files:
        if file.startswith('test_') or 'debug' in file.lower() or 'verify' in file.lower():
            test_files_in_root.append(file)

    if test_files_in_root:
        print(f"   ❌ 根目录仍有测试文件 ({len(test_files_in_root)}个):")
        for file in test_files_in_root[:5]:  # 只显示前5个
            print(f"      - {file}")
        if len(test_files_in_root) > 5:
            print(f"      ... 还有 {len(test_files_in_root) - 5} 个")
    else:
        print("   ✅ 根目录干净，无测试文件")

    # 2. 检查tests目录结构
    print("\n2. 检查tests目录结构:")
    if not os.path.exists('tests'):
        print("   ❌ tests目录不存在")
        return False

    test_categories = ['unit', 'integration', 'e2e', 'utils']
    for category in test_categories:
        path = f'tests/{category}'
        if os.path.exists(path):
            files = [f for f in os.listdir(path) if f.endswith('.py') and not f.startswith('__')]
            print(f"   ✅ {category}: {len(files)}个测试文件")
            for file in files[:3]:  # 只显示前3个
                print(f"      - {file}")
            if len(files) > 3:
                print(f"      ... 还有 {len(files) - 3} 个")
        else:
            print(f"   ❌ {category}目录不存在")

    # 3. 检查文件数量
    print("\n3. 统计测试文件数量:")
    total_tests = 0
    for category in test_categories:
        path = f'tests/{category}'
        if os.path.exists(path):
            files = [f for f in os.listdir(path) if f.endswith('.py') and not f.startswith('__')]
            total_tests += len(files)

    print(f"   总测试文件数: {total_tests}")

    # 4. 检查关键测试文件
    print("\n4. 检查关键测试文件:")
    key_tests = [
        ('tests/unit/test_device_model.py', '设备模型测试'),
        ('tests/unit/test_reservation_model.py', '预约模型测试'),
        ('tests/integration/test_devices_api.py', '设备API测试'),
        ('tests/integration/test_reservations_api.py', '预约API测试'),
        ('tests/e2e/test_reservation_workflow.py', '端到端测试')
    ]

    missing = []
    for path, description in key_tests:
        if os.path.exists(path):
            print(f"   ✅ {description}: 存在")
        else:
            print(f"   ❌ {description}: 缺失")
            missing.append(description)

    if missing:
        print(f"\n   ⚠️  缺少 {len(missing)} 个关键测试文件")

    print("\n" + "=" * 60)
    if not test_files_in_root and total_tests >= 5:
        print("✅ 测试文件结构验证通过！")
    else:
        print("⚠️  测试文件结构需要调整")
    print("=" * 60)

    return len(test_files_in_root) == 0


if __name__ == "__main__":
    verify_test_structure()