"""用户模型单元测试"""
import unittest
from app import create_app, db
from app.models import User

class TestUserModel(unittest.TestCase):
    """用户模型测试用例"""

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
        """测试密码哈希"""
        u = User(username='test')
        u.set_password('cat')
        self.assertTrue(u.check_password('cat'))
        self.assertFalse(u.check_password('dog'))

    def test_user_creation(self):
        """测试用户创建"""
        user = User(username='testuser', email='test@test.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        self.assertIsNotNone(user.id)

if __name__ == '__main__':
    unittest.main()
