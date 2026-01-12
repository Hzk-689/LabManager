import requests
import json
import datetime
import time

BASE_URL = "http://127.0.0.1:5000"


def test_complete_reservation_system():
    """完整预约系统测试"""
    print("=" * 70)
    print("=== 完整预约系统测试 ===")
    print("=" * 70)

    timestamp = int(time.time())

    # 1. 创建测试账户
    print("\n1. 创建测试账户...")
    admin_data = {
        "username": f"admin_{timestamp}",
        "email": f"admin{timestamp}@test.com",
        "password": "Admin123456",
        "role": "admin"
    }

    resp = requests.post(f"{BASE_URL}/api/auth/register", json=admin_data)
    if resp.status_code == 201:
        admin_token = resp.json()['token']
        admin_headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
        admin_id = resp.json()['user']['id']
        print(f"   ✅ 管理员创建成功，ID: {admin_id}")
    else:
        print(f"   ❌ 管理员创建失败")
        return False

    user_data = {
        "username": f"user_{timestamp}",
        "email": f"user{timestamp}@test.com",
        "password": "User123456",
        "role": "student"
    }

    resp = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
    if resp.status_code == 201:
        user_token = resp.json()['token']
        user_headers = {"Authorization": f"Bearer {user_token}", "Content-Type": "application/json"}
        user_id = resp.json()['user']['id']
        print(f"   ✅ 用户创建成功，ID: {user_id}")
    else:
        print(f"   ❌ 用户创建失败")
        return False

    # 2. 创建设备
    print("\n2. 创建设备...")
    device_data = {
        "device_id": f"DEV_{timestamp}",
        "name": f"测试设备_{timestamp}",
        "device_type": "测试仪器",
        "status": "available"
    }

    resp = requests.post(f"{BASE_URL}/api/devices/", json=device_data, headers=admin_headers)
    if resp.status_code == 201:
        device = resp.json()['data']
        device_id = device['id']
        print(f"   ✅ 设备创建成功，ID: {device_id}")
    else:
        print(f"   ❌ 设备创建失败")
        return False

    # 3. 创建预约
    print("\n3. 创建预约...")
    start_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=1)).isoformat()
    end_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).isoformat()

    reservation_data = {
        "device_id": device_id,
        "start_time": start_time,
        "end_time": end_time,
        "purpose": "完整预约系统测试"
    }

    resp = requests.post(f"{BASE_URL}/api/reservations/", json=reservation_data, headers=user_headers)
    if resp.status_code == 201:
        reservation = resp.json()['reservation']
        reservation_id = reservation['id']
        print(f"   ✅ 预约创建成功，ID: {reservation_id}")
        print(f"       状态: {reservation['status']}")
    else:
        print(f"   ❌ 预约创建失败: {resp.text}")
        return False

    # 4. 测试获取预约列表
    print("\n4. 测试预约列表...")
    resp = requests.get(f"{BASE_URL}/api/reservations/", headers=user_headers)
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ 预约列表获取成功")
        print(f"       预约数量: {len(data['data'])}")
    else:
        print(f"   ❌ 预约列表获取失败")

    # 5. 测试管理员审批
    print("\n5. 测试管理员审批...")
    approve_data = {"status": "approved", "notes": "测试审批"}
    resp = requests.put(f"{BASE_URL}/api/reservations/{reservation_id}/status",
                        json=approve_data,
                        headers=admin_headers)
    if resp.status_code == 200:
        result = resp.json()
        print(f"   ✅ 预约审批成功")
        print(f"       新状态: {result['data']['status']}")
    else:
        print(f"   ❌ 预约审批失败: {resp.text}")

    # 6. 测试开始使用
    print("\n6. 测试开始使用...")
    start_data = {"status": "in_progress"}
    resp = requests.put(f"{BASE_URL}/api/reservations/{reservation_id}/status",
                        json=start_data,
                        headers=admin_headers)
    if resp.status_code == 200:
        print(f"   ✅ 开始使用成功")
    else:
        print(f"   ❌ 开始使用失败: {resp.text}")

    # 7. 测试完成使用
    print("\n7. 测试完成使用...")
    complete_data = {
        "status": "completed",
        "actual_hours": 2.5,
        "usage_notes": "测试使用完成",
        "feedback": "设备工作正常",
        "rating": 5
    }
    resp = requests.put(f"{BASE_URL}/api/reservations/{reservation_id}/status",
                        json=complete_data,
                        headers=admin_headers)
    if resp.status_code == 200:
        result = resp.json()
        print(f"   ✅ 完成使用成功")
        print(f"       实际使用时长: {result['data']['actual_usage_hours']}小时")
    else:
        print(f"   ❌ 完成使用失败: {resp.text}")

    # 8. 测试用户取消（应该失败，因为已完成）
    print("\n8. 测试用户取消（应失败）...")
    cancel_data = {"reason": "测试取消"}
    resp = requests.delete(f"{BASE_URL}/api/reservations/{reservation_id}",
                           json=cancel_data,
                           headers=user_headers)
    if resp.status_code == 400:
        print(f"   ✅ 取消失败（正确，已完成预约不可取消）")
    else:
        print(f"   ⚠️  取消结果异常: {resp.status_code}")

    # 9. 清理测试数据
    print("\n9. 清理测试数据...")
    resp = requests.delete(f"{BASE_URL}/api/devices/{device_id}", headers=admin_headers)
    if resp.status_code == 200:
        print(f"   ✅ 测试设备删除成功")
    else:
        print(f"   ⚠️  测试设备删除失败: {resp.status_code}")

    print("\n" + "=" * 70)
    print("✅ 完整预约系统测试完成！")
    print("=" * 70)

    return True


if __name__ == "__main__":
    try:
        resp = requests.get(f"{BASE_URL}/", timeout=3)
        test_complete_reservation_system()
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请先启动: python run.py")
    except Exception as e:
        print(f"❌ 错误: {e}")