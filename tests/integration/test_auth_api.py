import requests
import json
import time

# API 基础 URL
BASE_URL = "http://127.0.0.1:5000"


def test_auth_api():
    """测试认证API的完整流程"""
    print("=" * 60)
    print("=== 认证API完整测试开始 ===")
    print("=" * 60)

    # 生成唯一用户名，避免重复注册冲突
    timestamp = int(time.time())
    test_username = f"testuser_{timestamp}"
    test_email = f"test{timestamp}@university.edu.cn"
    test_password = "TestPassword123"

    # 1. 测试服务器连通性
    print("\n1. 测试服务器连通性...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print(f"   ✅ 服务器连接正常: {response.json().get('message')}")
        else:
            print(f"   ❌ 服务器异常: 状态码 {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 无法连接到服务器: {e}")
        return False

    # 2. 测试用户注册
    print("\n2. 测试用户注册接口...")
    register_data = {
        "username": test_username,
        "email": test_email,
        "password": test_password,
        "role": "student"
    }

    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        result = response.json()

        if response.status_code == 201:
            user_id = result.get("user", {}).get("id")
            token = result.get("token")
            print(f"   ✅ 注册成功！用户ID: {user_id}")
            print(f"      令牌长度: {len(token) if token else 0} 字符")
        else:
            print(f"   ❌ 注册失败: {result.get('error', '未知错误')}")
            # 如果是用户名冲突，尝试使用备用用户名
            if "已存在" in result.get('error', ''):
                test_username = f"testuser_{timestamp}_alt"
                register_data["username"] = test_username
                response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
                if response.status_code == 201:
                    result = response.json()
                    user_id = result.get("user", {}).get("id")
                    token = result.get("token")
                    print(f"   ✅ 使用备用用户名注册成功！用户ID: {user_id}")
                else:
                    return False
            else:
                return False
    except Exception as e:
        print(f"   ❌ 注册请求异常: {e}")
        return False

    # 3. 测试用户登录
    print("\n3. 测试用户登录接口...")
    login_data = {
        "username": test_username,
        "password": test_password
    }

    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        result = response.json()

        if response.status_code == 200:
            login_token = result.get("token")
            print(f"   ✅ 登录成功！")
            print(f"      用户: {result.get('user', {}).get('username')}")
            print(f"      角色: {result.get('user', {}).get('role')}")
            print(f"      令牌长度: {len(login_token) if login_token else 0} 字符")

            # 验证注册和登录的令牌是否一致（理论上应该不同，因为是两次生成的）
            if token and login_token and token != login_token:
                print("   ℹ️  注册和登录令牌不同（正常现象，每次生成新令牌）")
            else:
                print("   ⚠️  注册和登录令牌相同")

        else:
            print(f"   ❌ 登录失败: {result.get('error', '未知错误')}")
            return False
    except Exception as e:
        print(f"   ❌ 登录请求异常: {e}")
        return False

    # 4. 测试令牌验证
    print("\n4. 测试令牌验证接口...")
    verify_data = {
        "token": login_token  # 使用登录获得的令牌
    }

    try:
        response = requests.post(f"{BASE_URL}/api/auth/verify", json=verify_data)
        result = response.json()

        if response.status_code == 200:
            print(f"   ✅ 令牌验证成功！")
            verified_user = result.get("user", {})
            print(f"      验证用户: {verified_user.get('username')}")
            print(f"      用户ID: {verified_user.get('id')}")
        else:
            print(f"   ❌ 令牌验证失败: {result.get('error', '未知错误')}")
            return False
    except Exception as e:
        print(f"   ❌ 令牌验证请求异常: {e}")
        return False

    # 5. 测试错误情况
    print("\n5. 测试错误处理...")

    # 5.1 测试无效令牌
    invalid_token_data = {
        "token": "invalid.token.here"
    }
    response = requests.post(f"{BASE_URL}/api/auth/verify", json=invalid_token_data)
    if response.status_code == 401:
        print(f"   ✅ 无效令牌被正确拒绝")
    else:
        print(f"   ⚠️  无效令牌处理异常: 状态码 {response.status_code}")

    # 5.2 测试错误密码登录
    wrong_password_data = {
        "username": test_username,
        "password": "WrongPassword123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=wrong_password_data)
    if response.status_code == 401:
        print(f"   ✅ 错误密码被正确拒绝")
    else:
        print(f"   ⚠️  错误密码处理异常: 状态码 {response.status_code}")

    # 6. 测试完成，清理测试数据（可选）
    print("\n6. 测试数据清理...")
    # 在实际项目中，这里可以添加删除测试用户的代码
    # 但为了测试完整性，我们保留测试数据以便手动检查
    print("   ℹ️  测试用户保留在数据库中，可用于后续检查")
    print(f"      用户名: {test_username}")
    print(f"      邮箱: {test_email}")

    print("\n" + "=" * 60)
    print("=== 认证API测试完成 ===")
    print("=" * 60)

    return True


if __name__ == "__main__":
    # 检查服务器是否运行
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            test_auth_api()
        else:
            print("❌ 服务器未正常运行，请先启动: python run.py")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保 Flask 应用正在运行")
        print("   启动命令: python run.py")
    except Exception as e:
        print(f"❌ 检查服务器时发生错误: {e}")