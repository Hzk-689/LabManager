"""测试套件 - 实验室设备管理系统"""

def run_all_tests():
    """运行所有测试"""
    import unittest
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir='.', pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)

if __name__ == "__main__":
    run_all_tests()
