import jwt
import datetime
from flask import current_app


def generate_token(user_id, expires_in=3600):
    """生成JWT访问令牌"""
    try:
        payload = {
            'user_id': user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in),
            'iat': datetime.datetime.utcnow(),
            'type': 'access'
        }
        # 从应用配置获取密钥
        secret_key = current_app.config.get('SECRET_KEY')
        if not secret_key:
            raise ValueError("SECRET_KEY未在应用配置中设置")

        return jwt.encode(payload, secret_key, algorithm='HS256')

    except Exception as e:
        current_app.logger.error(f"生成令牌失败: {e}")
        raise


def verify_token(token):
    """验证JWT令牌的有效性"""
    try:
        secret_key = current_app.config.get('SECRET_KEY')
        if not secret_key:
            raise ValueError("SECRET_KEY未在应用配置中设置")

        payload = jwt.decode(token, secret_key, algorithms=['HS256'])

        # 验证令牌类型
        if payload.get('type') != 'access':
            return None

        return payload['user_id']

    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except Exception:
        return None