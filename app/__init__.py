from config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# 创建数据库实例
db = SQLAlchemy()


def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)

    # 加载配置
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    CORS(app)

    # 注册蓝图 - 添加详细的调试信息
    print("\n" + "=" * 50)
    print("=== 开始注册蓝图 ===")

    # 1. 主蓝图
    try:
        from app.routes.main import bp as main_bp
        app.register_blueprint(main_bp)
        print("✅ 主蓝图注册成功")
        print(f"   名称: {main_bp.name}, URL前缀: {main_bp.url_prefix}")
    except ImportError as e:
        print(f"❌ 主蓝图注册失败: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"❌ 主蓝图注册异常: {e}")

    # 2. 认证蓝图
    try:
        from app.routes.auth import bp as auth_bp
        app.register_blueprint(auth_bp)
        print("✅ 认证蓝图注册成功")
        print(f"   名称: {auth_bp.name}, URL前缀: {auth_bp.url_prefix}")
    except ImportError as e:
        print(f"❌ 认证蓝图注册失败: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"❌ 认证蓝图注册异常: {e}")

    # 3. 设备蓝图
    try:
        from app.routes.devices import bp as devices_bp
        app.register_blueprint(devices_bp)
        print("✅ 设备蓝图注册成功")
        print(f"   名称: {devices_bp.name}, URL前缀: {devices_bp.url_prefix}")
    except ImportError as e:
        print(f"❌ 设备蓝图注册失败: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"❌ 设备蓝图注册异常: {e}")

    # 4. 预约蓝图（新增）
    try:
        from app.routes.reservations import bp as reservations_bp
        app.register_blueprint(reservations_bp)
        print("✅ 预约蓝图注册成功")
        print(f"   名称: {reservations_bp.name}, URL前缀: {reservations_bp.url_prefix}")
    except ImportError as e:
        print(f"❌ 预约蓝图注册失败: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"❌ 预约蓝图注册异常: {e}")

    print("=== 蓝图注册完成 ===")
    print("=" * 50 + "\n")

    # 导入模型
    from app import models

    return app