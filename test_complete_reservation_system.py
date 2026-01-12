import requests
import json
import datetime
import time
import sys

BASE_URL = "http://127.0.0.1:5000"


def test_complete_reservation_system():
    """完整的预约系统端到端测试"""
    print("=" * 70)
    print("=== 预约系统完整功能测试 ===")
    print("=" * 70)

    timestamp = int(time.time())
    test_results = []

    def log_test(name, success, message=""):
        """记录测试结果"""
        status = "✅" if success else "❌"
        test_results.append((name, success))
        print(f"{status} {name}: {message}")
        return success

    try:
        # 1. 测试基础连接
        print("\n1. 🔌 测试服务器连接...")
        resp = requests.get(f"{BASE_URL}/api/reservations/test", timeout=5)
        if resp.status_code == 200:
            log_test("API基础连接", True, "服务器响应正常")
        else:
            log_test("API基础连接", False, f"状态码: {resp.status_code}")
            return False

        # 2. 创建测试用户
        print("\n2. 👥 创建测试账户...")
        admin_data = {
            "username": f"admin_test_{timestamp}",
            "email": f"admin{timestamp}@test.com",
            "password": "Admin123456",
            "role": "admin"
        }

        resp = requests.post(f"{BASE_URL}/api/auth/register", json=admin_data)
        if resp.status_code in [201, 400]:  # 400可能是用户已存在
            if resp.status_code == 201:
                admin_token = resp.json()['token']
                log_test("管理员注册", True, "创建成功")
            else:
                # 尝试登录
                login_data = {"username": admin_data["username"], "password": admin_data["password"]}
                resp = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
                if resp.status_code == 200:
                    admin_token = resp.json()['token']
                    log_test("管理员登录", True, "登录成功")
                else:
                    log_test("管理员账户", False, "注册和登录都失败")
                    return False
        else:
            log_test("管理员注册", False, f"状态码: {resp.status_code}")
            return False

        admin_headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }

        # 创建普通用户
        user_data = {
            "username": f"user_test_{timestamp}",
            "email": f"user{timestamp}@test.com",
            "password": "User123456",
            "role": "student"
        }

        resp = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        if resp.status_code in [201, 400]:
            if resp.status_code == 201:
                user_token = resp.json()['token']
                log_test("用户注册", True, "创建成功")
            else:
                login_data = {"username": user_data["username"], "password": user_data["password"]}
                resp = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
                if resp.status_code == 200:
                    user_token = resp.json()['token']
                    log_test("用户登录", True, "登录成功")
                else:
                    log_test("用户账户", False, "注册和登录都失败")
                    return False
        else:
            log_test("用户注册", False, f"状态码: {resp.status_code}")
            return False

        user_headers = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json"
        }

        # 3. 创建设备
        print("\n3. 📱 创建设备...")
        device_data = {
            "device_id": f"DEV_TEST_{timestamp}",
            "name": f"测试设备_{timestamp}",
            "device_type": "测试仪器",
            "status": "available",
            "location": "测试实验室",
            "max_reservation_hours": 4
        }

        resp = requests.post(f"{BASE_URL}/api/devices/", json=device_data, headers=admin_headers)
        if resp.status_code == 201:
            device_id = resp.json()['data']['id']
            log_test("设备创建", True, f"设备ID: {device_id}")
        else:
            log_test("设备创建", False, resp.text)
            return False

        # 4. 测试预约创建
        print("\n4. 📅 测试预约创建...")
        start_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=1)).isoformat()
        end_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).isoformat()

        reservation_data = {
            "device_id": device_id,
            "start_time": start_time,
            "end_time": end_time,
            "purpose": "完整的预约系统功能测试",
            "experiment_name": "实验项目测试"
        }

        resp = requests.post(f"{BASE_URL}/api/reservations/", json=reservation_data, headers=user_headers)
        if resp.status_code == 201:
            reservation = resp.json()['reservation']
            reservation_id = reservation['id']
            log_test("预约创建", True, f"预约ID: {reservation_id}")
        else:
            log_test("预约创建", False, resp.text)
            return False

        # 5. 测试预约列表
        print("\n5. 📋 测试预约列表...")
        resp = requests.get(f"{BASE_URL}/api/reservations/", headers=user_headers)
        if resp.status_code == 200:
            data = resp.json()
            reservation_count = len(data['data'])
            log_test("预约列表", True, f"找到{reservation_count}个预约")
        else:
            log_test("预约列表", False, resp.text)

        # 6. 测试预约详情
        print("\n6. 🔍 测试预约详情...")
        resp = requests.get(f"{BASE_URL}/api/reservations/{reservation_id}", headers=user_headers)
        if resp.status_code == 200:
            reservation_detail = resp.json()['data']
            log_test("预约详情", True, f"状态: {reservation_detail['status']}")
        else:
            log_test("预约详情", False, resp.text)

        # 7. 测试管理员审批
        print("\n7. ✅ 测试管理员审批...")
        approve_data = {
            "status": "approved",
            "notes": "测试审批通过"
        }
        resp = requests.put(f"{BASE_URL}/api/reservations/{reservation_id}/status",
                            json=approve_data, headers=admin_headers)
        if resp.status_code == 200:
            approved_reservation = resp.json()['data']
            log_test("预约审批", True, f"新状态: {approved_reservation['status']}")
        else:
            log_test("预约审批", False, resp.text)

        # 8. 测试开始使用
        print("\n8. ⏱️ 测试开始使用...")
        start_data = {"status": "in_progress"}
        resp = requests.put(f"{BASE_URL}/api/reservations/{reservation_id}/status",
                            json=start_data, headers=admin_headers)
        if resp.status_code == 200:
            log_test("开始使用", True, "设备使用开始")
        else:
            log_test("开始使用", False, resp.text)

        # 9. 测试完成使用
        print("\n9. 🏁 测试完成使用...")
        complete_data = {
            "status": "completed",
            "actual_hours": 2.5,
            "usage_notes": "测试使用完成",
            "feedback": "设备工作正常",
            "rating": 5
        }
        resp = requests.put(f"{BASE_URL}/api/reservations/{reservation_id}/status",
                            json=complete_data, headers=admin_headers)
        if resp.status_code == 200:
            completed_reservation = resp.json()['data']
            actual_hours = completed_reservation.get('actual_usage_hours', 0)
            log_test("完成使用", True, f"实际使用: {actual_hours}小时")
        else:
            log_test("完成使用", False, resp.text)

        # 10. 测试权限控制
        print("\n10. 🔐 测试权限控制...")
        # 普通用户尝试审批（应该失败）
        unauthorized_data = {"status": "approved"}
        resp = requests.put(f"{BASE_URL}/api/reservations/{reservation_id}/status",
                            json=unauthorized_data, headers=user_headers)
        if resp.status_code == 403:
            log_test("权限验证", True, "普通用户无法审批预约")
        else:
            log_test("权限验证", False, f"权限控制异常: {resp.status_code}")

        # 11. 清理测试数据
        print("\n11. 🧹 清理测试数据...")
        resp = requests.delete(f"{BASE_URL}/api/devices/{device_id}", headers=admin_headers)
        if resp.status_code == 200:
            log_test("设备清理", True, "测试设备已删除")
        else:
            log_test("设备清理", False, f"删除失败: {resp.status_code}")

        # 统计测试结果
        print("\n" + "=" * 70)
        total_tests = len(test_results)
        passed_tests = sum(1 for _, success in test_results if success)
        success_rate = (passed_tests / total_tests) * 100

        print(f"📊 测试结果统计:")
        print(f"   总测试数: {total_tests}")
        print(f"   通过数: {passed_tests}")
        print(f"   成功率: {success_rate:.1f}%")

        if success_rate == 100:
            print("🎉 所有测试通过！预约系统功能完整！")
        elif success_rate >= 80:
            print("✅ 大部分测试通过，系统基本可用")
        else:
            print("⚠️  部分测试失败，需要检查")

        print("=" * 70)

        return success_rate >= 80

    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请先启动: python run.py")
        return False
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 检查服务器是否运行
    try:
        # 先测试基础连接
        test_resp = requests.get(f"{BASE_URL}/api/reservations/test", timeout=3)
        if test_resp.status_code == 200:
            print("✅ 服务器连接正常，开始测试...")
            success = test_complete_reservation_system()
            sys.exit(0 if success else 1)
        else:
            print(f"❌ 服务器响应异常: {test_resp.status_code}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请先启动: python run.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)