# app/auth.py
"""
认证工具模块
包含JWT令牌生成和验证功能
"""
import jwt
import datetime
from flask import current_app

SECRET_KEY = 'dev-secret-key-change-in-production'


def generate_token(user_id, username, role, expires_in=24 * 3600):
    """
    生成JWT令牌

    Args:
        user_id: 用户ID
        username: 用户名
        role: 用户角色
        expires_in: 过期时间（秒），默认24小时

    Returns:
        str: JWT令牌字符串
    """
    try:
        payload = {
            'user_id': user_id,
            'username': username,
            'role': role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return token
    except Exception as e:
        print(f"生成令牌失败: {e}")
        return None


def verify_token(token):
    """
    验证JWT令牌

    Args:
        token: JWT令牌字符串

    Returns:
        dict or None: 解码后的令牌数据，如果无效返回None
    """
    try:
        if not token:
            return None

        # 解码令牌
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        print("令牌已过期")
        return None
    except jwt.InvalidTokenError as e:
        print(f"无效令牌: {e}")
        return None
    except Exception as e:
        print(f"令牌验证失败: {e}")
        return None


def get_token_payload(request):
    """
    从请求中提取令牌并验证

    Args:
        request: Flask请求对象

    Returns:
        dict or None: 令牌数据
    """
    try:
        # 从请求头获取令牌
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header[7:]  # 去掉'Bearer '前缀
        return verify_token(token)
    except Exception as e:
        print(f"获取令牌数据失败: {e}")
        return None


def token_required(f):
    """
    装饰器：需要有效令牌才能访问
    """
    from functools import wraps
    from flask import request, jsonify

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # 从请求头获取令牌
            auth_header = request.headers.get('Authorization')

            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': '未提供认证令牌'}), 401

            token = auth_header[7:]  # 去掉'Bearer '前缀

            # 验证令牌
            payload = verify_token(token)
            if not payload:
                return jsonify({'error': '无效或过期的令牌'}), 401

            # 将用户信息传递给被装饰的函数
            return f(payload, *args, **kwargs)
        except Exception as e:
            return jsonify({'error': f'认证失败: {str(e)}'}), 500

    return decorated_function


def admin_required(f):
    """
    装饰器：需要管理员权限
    """
    from functools import wraps
    from flask import request, jsonify

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # 从请求头获取令牌
            auth_header = request.headers.get('Authorization')

            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': '未提供认证令牌'}), 401

            token = auth_header[7:]  # 去掉'Bearer '前缀

            # 验证令牌
            payload = verify_token(token)
            if not payload:
                return jsonify({'error': '无效或过期的令牌'}), 401

            # 检查是否是管理员
            if payload.get('role') != 'admin':
                return jsonify({'error': '需要管理员权限'}), 403

            # 将用户信息传递给被装饰的函数
            return f(payload, *args, **kwargs)
        except Exception as e:
            return jsonify({'error': f'认证失败: {str(e)}'}), 500

    return decorated_function


# 测试函数
if __name__ == "__main__":
    # 测试令牌生成和验证
    test_user = {
        'user_id': 1,
        'username': 'testuser',
        'role': 'admin'
    }

    token = generate_token(**test_user)
    print(f"生成的令牌: {token}")

    if token:
        payload = verify_token(token)
        print(f"验证结果: {payload}")