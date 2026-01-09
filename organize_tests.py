import os
import shutil
import sys


def organize_tests():
    """整理测试文件到专业目录结构"""

    # 创建测试目录
    test_dirs = ['tests/unit', 'tests/integration', 'tests/e2e', 'tests/utils']
    for dir_path in test_dirs:
        os.makedirs(dir_path, exist_ok=True)
        with open(f"{dir_path}/__init__.py", 'w') as f:
            f.write("# Test package\n")

    # 文件映射：旧文件 -> 新位置/新名称
    file_mapping = {
        'test_api_auth.py': 'tests/integration/test_auth_api.py',
        'test_complete_system.py': 'tests/e2e/test_full_system.py',
        'check_auth.py': 'tests/utils/system_check.py',
        'test_token.py': 'tests/unit/test_token_auth.py',  # 可选
    }

    # 移动并重命名文件
    moved_files = []
    for old_file, new_path in file_mapping.items():
        if os.path.exists(old_file):
            shutil.move(old_file, new_path)
            moved_files.append((old_file, new_path))
            print(f"✅ 移动: {old_file} -> {new_path}")
        else:
            print(f"⚠️  文件不存在: {old_file}")

    # 创建测试运行器
    with open('tests/__init__.py', 'w') as f:
        f.write('''\"\"\"测试套件 - 实验室设备管理系统\"\"\"

def run_all_tests():
    \"\"\"运行所有测试\"\"\"
    import unittest
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=\'.\', pattern=\'test_*.py\')
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)

if __name__ == \"__main__\":
    run_all_tests()
''')

    # 创建单元测试示例
    with open('tests/unit/test_models.py', 'w') as f:
        f.write('''\"\"\"用户模型单元测试\"\"\"
import unittest
from app import create_app, db
from app.models import User

class TestUserModel(unittest.TestCase):
    \"\"\"用户模型测试用例\"\"\"

    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        \"\"\"测试密码哈希\"\"\"
        u = User(username='test')
        u.set_password('cat')
        self.assertTrue(u.check_password('cat'))
        self.assertFalse(u.check_password('dog'))

    def test_user_creation(self):
        \"\"\"测试用户创建\"\"\"
        user = User(username='testuser', email='test@test.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        self.assertIsNotNone(user.id)

if __name__ == '__main__':
    unittest.main()
''')

    print(f"\\n🎯 测试文件整理完成！共移动 {len(moved_files)} 个文件")
    print("\\n新的测试结构:")
    for old, new in moved_files:
        print(f"  {old:25} → {new}")

    return True


if __name__ == "__main__":
    print("开始整理测试文件...")
    if organize_tests():
        print("\\n✅ 整理完成！现在可以提交到GitHub")
    else:
        print("❌ 整理失败")