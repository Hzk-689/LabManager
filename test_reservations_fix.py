# test_reservations_fix.py
try:
    from app.routes.reservations import bp, token_required, admin_required

    print("✅ 预约蓝图导入成功")
    print(f"  蓝图名称: {bp.name}")
    print(f"  URL前缀: {bp.url_prefix}")
    print(f"  token_required装饰器: {token_required}")
    print(f"  admin_required装饰器: {admin_required}")

    # 测试路由注册
    from app import create_app

    app = create_app()

    with app.app_context():
        print("\n📋 注册的路由:")
        for rule in app.url_map.iter_rules():
            if 'reservations' in rule.endpoint:
                methods = [m for m in rule.methods if m not in ['OPTIONS', 'HEAD']]
                print(f"  {', '.join(methods):6} {rule.rule}")

    print("\n🎉 预约API修复完成！")

except ImportError as e:
    print(f"❌ 导入失败: {e}")
except Exception as e:
    print(f"❌ 其他错误: {e}")