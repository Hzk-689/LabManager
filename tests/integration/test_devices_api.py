import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"


def test_devices_api():
    """测试设备管理API"""
    print("=" * 60)
    print("=== 设备管理API测试开始 ===")
    print("=" * 60)

    # 1. 注册管理员用户
    print("\n1. 准备管理员账户...")
    timestamp = int(time.time())
    admin_username = f"admin_{timestamp}"

    admin_data = {
        "username": admin_username,
        "email": f"admin{timestamp}@test.com",
        "password": "Admin123456",
        "role": "admin"
    }

    resp = requests.post(f"{BASE_URL}/api/auth/register", json=admin_data)
    if resp.status_code == 201:
        admin_token = resp.json()['token']
        print(f"   ✅ 管理员注册成功，用户名: {admin_username}")
        print(f"       令牌: {admin_token[:20]}...")
    else:
        # 如果已存在，尝试登录
        print(f"   ⚠️ 注册失败，尝试登录...")
        login_data = {
            "username": admin_data['username'],
            "password": admin_data['password']
        }
        resp = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if resp.status_code == 200:
            admin_token = resp.json()['token']
            print(f"   ✅ 管理员登录成功")
        else:
            print(f"   ❌ 无法获取管理员令牌: {resp.status_code} - {resp.text}")
            return False

    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }

    # 2. 测试创建设备
    print("\n2. 测试创建设备...")
    device_data = {
        "device_id": f"DEV_{timestamp}",
        "name": "高级测试显微镜",
        "device_type": "光学仪器",
        "category": "精密仪器",
        "status": "available",
        "location": "实验室A-101",
        "max_reservation_hours": 4,
        "description": "通过设备管理API创建的测试设备",
        "specifications": "放大倍数：1000x，光源：LED"
    }

    resp = requests.post(f"{BASE_URL}/api/devices/", json=device_data, headers=headers)
    if resp.status_code == 201:
        device = resp.json()['data']
        device_id = device['id']
        print(f"   ✅ 设备创建成功")
        print(f"       ID: {device_id}")
        print(f"       编号: {device['device_id']}")
        print(f"       名称: {device['name']}")
    else:
        print(f"   ❌ 设备创建失败: {resp.status_code}")
        print(f"       响应: {resp.text}")
        return False

    # 3. 测试获取设备列表
    print("\n3. 测试获取设备列表...")
    resp = requests.get(f"{BASE_URL}/api/devices/", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        device_count = len(data['data'])
        print(f"   ✅ 获取设备列表成功")
        print(f"       设备总数: {data['pagination']['total']}")
        print(f"       当前页数量: {device_count}")
    else:
        print(f"   ❌ 获取设备列表失败: {resp.status_code}")

    # 4. 测试获取设备详情
    print("\n4. 测试获取设备详情...")
    resp = requests.get(f"{BASE_URL}/api/devices/{device_id}", headers=headers)
    if resp.status_code == 200:
        device = resp.json()['data']
        print(f"   ✅ 获取设备详情成功")
        print(f"       设备状态: {device['status']}")
        print(f"       设备位置: {device['location']}")
        print(f"       设备描述: {device['description'][:30]}...")
    else:
        print(f"   ❌ 获取设备详情失败: {resp.status_code}")

    # 5. 测试更新设备状态
    print("\n5. 测试更新设备状态...")
    status_data = {"status": "maintenance"}
    resp = requests.put(f"{BASE_URL}/api/devices/{device_id}/status", json=status_data, headers=headers)
    if resp.status_code == 200:
        result = resp.json()
        print(f"   ✅ 设备状态更新成功")
        print(f"       新状态: {result['data']['status']}")
    else:
        print(f"   ❌ 设备状态更新失败: {resp.status_code}")

    # 6. 测试记录设备使用
    print("\n6. 测试记录设备使用...")
    usage_data = {"hours": 2.5}
    resp = requests.post(f"{BASE_URL}/api/devices/{device_id}/usage", json=usage_data, headers=headers)
    if resp.status_code == 200:
        result = resp.json()
        print(f"   ✅ 设备使用记录成功")
        print(f"       累计时长: {result['data']['total_usage_hours']}小时")
    else:
        print(f"   ❌ 设备使用记录失败: {resp.status_code}")

    # 7. 测试更新设备信息
    print("\n7. 测试更新设备信息...")
    update_data = {
        "location": "实验室A-102（已转移）",
        "description": "更新后的设备描述信息",
        "responsible_person": "张老师"
    }
    resp = requests.put(f"{BASE_URL}/api/devices/{device_id}", json=update_data, headers=headers)
    if resp.status_code == 200:
        result = resp.json()
        print(f"   ✅ 设备信息更新成功")
        print(f"       新位置: {result['data']['location']}")
        print(f"       负责人: {result['data']['responsible_person']}")
    else:
        print(f"   ❌ 设备信息更新失败: {resp.status_code}")

    # 8. 测试权限验证
    print("\n8. 测试权限验证...")
    # 创建普通用户
    user_username = f"student_{timestamp}"
    user_data = {
        "username": user_username,
        "email": f"student{timestamp}@test.com",
        "password": "Student123456",
        "role": "student"
    }

    resp = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
    if resp.status_code == 201:
        user_token = resp.json()['token']
        user_headers = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json"
        }

        # 普通用户尝试删除设备（应失败）
        resp = requests.delete(f"{BASE_URL}/api/devices/{device_id}", headers=user_headers)
        if resp.status_code == 403:
            print(f"   ✅ 权限验证成功：普通用户无法删除设备")
        else:
            print(f"   ⚠️  权限验证异常: {resp.status_code} - {resp.text}")
    else:
        print(f"   ⚠️  创建普通用户失败，跳过权限测试")

    # 9. 清理测试数据
    print("\n9. 清理测试数据...")
    resp = requests.delete(f"{BASE_URL}/api/devices/{device_id}", headers=headers)
    if resp.status_code == 200:
        print(f"   ✅ 测试设备删除成功")
    else:
        print(f"   ⚠️  测试设备删除失败: {resp.status_code}")

    print("\n" + "=" * 60)
    print("=== 设备管理API测试完成 ===")
    print("=" * 60)

    return True


if __name__ == "__main__":
    # 检查服务器是否运行
    try:
        resp = requests.get(f"{BASE_URL}/", timeout=3)
        print(f"✅ 连接到服务器: {resp.status_code}")
        test_devices_api()
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请先启动: python run.py")
    except Exception as e:
        print(f"❌ 错误: {e}")