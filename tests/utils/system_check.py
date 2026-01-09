from app import create_app

app = create_app()

print("=" * 60)
print("=== 验证认证系统 ===")
print("=" * 60)

# 检查蓝图
print(f"\n📊 已注册的蓝图: {list(app.blueprints.keys())}")

# 检查路由
print("\n🔗 认证相关路由:")
auth_routes = []
for rule in app.url_map.iter_rules():
    if 'auth' in rule.endpoint:
        auth_routes.append(rule)

if auth_routes:
    for rule in auth_routes:
        print(f"  ✅ {rule.rule}")
else:
    print("  ❌ 没有找到认证路由")

# 测试应用上下文
print("\n🧪 测试应用上下文和数据库:")
with app.app_context():
    from app import db
    from sqlalchemy import inspect

    # 检查数据库连接
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"  ✅ 数据库连接正常，表数量: {len(tables)}")
        if 'users' in tables:
            print(f"  ✅ users表存在")
    except Exception as e:
        print(f"  ❌ 数据库连接失败: {e}")

print("\n" + "=" * 60)
print("=== 验证完成 ===")
print("=" * 60)