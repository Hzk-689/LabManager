import requests
import json
import datetime
import time

BASE_URL = "http://127.0.0.1:5000"


def test_reservation_full_system():
    """预约系统完整流程测试"""
    print("=" * 70)
    print("=== 预约系统完整流程测试 ===")
    print("=" * 70)

    timestamp = int(time.time())

    # 1. 创建管理员账户
    print("\n1. 🎫 创建管理员账户...")
    admin_data = {
        "username": f"admin_res_{timestamp}",
        "email": f"admin_res{timestamp}@test.com",
        "password": "Admin123456",
        "role": "admin"
    }

    resp = requests.post(f"{BASE_URL}/api/auth/register", json=admin_data)
    if resp.status_code == 201:
        admin_token = resp.json()['token']
        admin_headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
        print(f"   ✅ 管理员创建成功")
    else:
        # 如果已存在，登录
        login_data = {"username": admin_data["username"], "password": admin_data["password"]}
        resp = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        admin_token = resp.json()['token']
        admin_headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
        print(f"   ✅ 管理员登录成功")

    # 2. 创建设备
    print("\n2. 📱 创建设备...")
    device_data = {
        "device_id": f"DEV_{timestamp}",
        "name": f"测试设备_{timestamp}",
        "device_type": "测试仪器",
        "status": "available",
        "location": "实验室A-101",
        "max_reservation_hours": 4
    }

    resp = requests.post(f"{BASE_URL}/api/devices/", json=device_data, headers=admin_headers)
    if resp.status_code == 201:
        device = resp.json()['data']
        device_id = device['id']
        print(f"   ✅ 设备创建成功，ID: {device_id}")
    else:
        print(f"   ❌ 设备创建失败: {resp.status_code} - {resp.text}")
        return False

    # 3. 创建普通用户
    print("\n3. 👤 创建普通用户...")
    user_data = {
        "username": f"user_res_{timestamp}",
        "email": f"user_res{timestamp}@test.com",
        "password": "User123456",
        "role": "student"
    }

    resp = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
    if resp.status_code == 201:
        user_token = resp.json()['token']
        user_headers = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json"
        }
        user_id = resp.json()['user']['id']
        print(f"   ✅ 用户创建成功，ID: {user_id}")
    else:
        print(f"   ❌ 用户创建失败: {resp.status_code} - {resp.text}")
        return False

    # 4. 测试创建预约
    print("\n4. 📅 测试创建预约...")
    start_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=1)).isoformat()
    end_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).isoformat()

    reservation_data = {
        "device_id": device_id,
        "start_time": start_time,
        "end_time": end_time,
        "purpose": "完整的预约系统测试",
        "experiment_name": "实验项目测试",
        "research_field": "计算机科学"
    }

    resp = requests.post(f"{BASE_URL}/api/reservations/",
                         json=reservation_data,
                         headers=user_headers)

    if resp.status_code == 201:
        reservation = resp.json()['reservation']
        reservation_id = reservation['id']
        print(f"   ✅ 预约创建成功")
        print(f"       预约ID: {reservation_id}")
        print(f"       设备ID: {reservation['device_id']}")
        print(f"       用户ID: {reservation['user_id']}")
        print(f"       开始时间: {reservation['start_time']}")
        print(f"       结束时间: {reservation['end_time']}")
        print(f"       预约状态: {reservation['status']}")
    else:
        print(f"   ❌ 预约创建失败: {resp.status_code} - {resp.text}")
        return False

    # 5. 测试时间冲突检测
    print("\n5. ⚠️ 测试时间冲突检测...")
    conflict_data = {
        "device_id": device_id,
        "start_time": (datetime.datetime.utcnow() + datetime.timedelta(hours=2)).isoformat(),
        "end_time": (datetime.datetime.utcnow() + datetime.timedelta(hours=4)).isoformat(),
        "purpose": "时间冲突测试"
    }

    resp = requests.post(f"{BASE_URL}/api/reservations/",
                         json=conflict_data,
                         headers=user_headers)

    if resp.status_code == 409:
        conflict_info = resp.json()
        print(f"   ✅ 时间冲突检测成功")
        print(f"       错误类型: {conflict_info.get('error')}")
        print(f"       错误信息: {conflict_info.get('message')}")
        conflicts = conflict_info.get('conflicts', [])
        print(f"       冲突数量: {len(conflicts)}")

        for i, conflict in enumerate(conflicts[:2]):  # 只显示前2个冲突
            print(f"       冲突{i + 1}: 预约ID={conflict.get('id')}, "
                  f"时间={conflict.get('start_time')} 到 {conflict.get('end_time')}")
    else:
        print(f"   ⚠️  时间冲突检测异常: {resp.status_code} - {resp.text}")

    # 6. 测试无冲突预约
    print("\n6. ✅ 测试无冲突预约...")
    no_conflict_data = {
        "device_id": device_id,
        "start_time": (datetime.datetime.utcnow() + datetime.timedelta(hours=5)).isoformat(),
        "end_time": (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).isoformat(),
        "purpose": "无冲突预约测试"
    }

    resp = requests.post(f"{BASE_URL}/api/reservations/",
                         json=no_conflict_data,
                         headers=user_headers)

    if resp.status_code == 201:
        second_reservation = resp.json()['reservation']
        second_id = second_reservation['id']
        print(f"   ✅ 无冲突预约创建成功")
        print(f"       预约ID: {second_id}")
        print(f"       开始时间: {second_reservation['start_time']}")
    else:
        print(f"   ❌ 无冲突预约创建失败: {resp.status_code} - {resp.text}")

    # 7. 测试设备不可用情况
    print("\n7. 🔧 测试设备不可用情况...")
    # 将设备状态设置为维护中
    status_data = {"status": "maintenance"}
    resp = requests.put(f"{BASE_URL}/api/devices/{device_id}/status",
                        json=status_data,
                        headers=admin_headers)

    if resp.status_code == 200:
        print(f"   ✅ 设备状态已更新为 maintenance")

    # 尝试预约
    maintenance_reservation_data = {
        "device_id": device_id,
        "start_time": (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).isoformat(),
        "end_time": (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).isoformat(),
        "purpose": "设备维护状态测试"
    }

    resp = requests.post(f"{BASE_URL}/api/reservations/",
                         json=maintenance_reservation_data,
                         headers=user_headers)

    if resp.status_code == 400 and "不可预约" in resp.json().get('error', ''):
        print(f"   ✅ 设备不可用检测成功")
        print(f"       错误信息: {resp.json().get('error')}")
    else:
        print(f"   ⚠️  设备不可用检测异常: {resp.status_code} - {resp.text}")

    # 8. 清理测试数据
    print("\n8. 🧹 清理测试数据...")

    # 恢复设备状态
    resp = requests.put(f"{BASE_URL}/api/devices/{device_id}/status",
                        json={"status": "available"},
                        headers=admin_headers)

    # 删除第二个预约
    if 'second_id' in locals():
        # 注意：预约删除接口可能未实现，这里只是示意
        print(f"   ℹ️  预约删除接口待实现")

    # 删除设备
    resp = requests.delete(f"{BASE_URL}/api/devices/{device_id}", headers=admin_headers)
    if resp.status_code == 200:
        print(f"   ✅ 测试设备删除成功")
    else:
        print(f"   ⚠️  测试设备删除失败: {resp.status_code}")

    print("\n" + "=" * 70)
    print("✅ 预约系统完整流程测试完成！")
    print("=" * 70)

    return True


if __name__ == "__main__":
    # 检查服务器是否运行
    try:
        resp = requests.get(f"{BASE_URL}/", timeout=3)
        print(f"✅ 服务器连接正常: {resp.status_code}")
        test_reservation_full_system()
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请先启动: python run.py")
    except Exception as e:
        print(f"❌ 错误: {e}")