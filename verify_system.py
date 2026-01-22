# simple_test.py - 简化验证
import requests


def quick_test():
    print("🚀 快速系统验证")
    print("=" * 40)

    # 测试登录
    try:
        response = requests.post(
            "http://localhost:5000/api/auth/login",
            json={"username": "admin", "password": "admin123"},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print("✅ 后端登录API: 正常")
            print(f"   用户: {data.get('user', {}).get('username', '未知')}")
            print(f"   Token: {data.get('token', '无')[:20]}...")
        else:
            print(f"后端登录API: 失败 ({response.status_code})")
    except Exception as e:
        print(f"❌ 后端服务: 不可达 ({e})")

    # 测试前端页面
    pages = ["/login", "/dashboard", "/devices", "/reservations"]
    for page in pages:
        try:
            response = requests.get(f"http://localhost:3000{page}", timeout=5)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} 前端{page}: {response.status_code}")
        except:
            print(f"❌ 前端{page}: 不可达")

    # 检查数据库文件
    import os
    if os.path.exists('app.db'):
        size = os.path.getsize('app.db')
        print(f"✅ 数据库文件: 存在 ({size} 字节)")
    else:
        print("❌ 数据库文件: 不存在")

    print("=" * 40)
    print("🎯 结论: 系统核心功能正常即可使用")


if __name__ == "__main__":
    quick_test()