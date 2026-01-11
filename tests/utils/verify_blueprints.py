# verify_blueprints_full.py
from app import create_app

app = create_app()

print("=" * 60)
print("=== 完整蓝图注册验证 ===")
print("=" * 60)

# 1. 检查已注册的蓝图
print(f"\n📊 已注册的蓝图 ({len(app.blueprints)}个):")
for name, blueprint in app.blueprints.items():
    print(f"  - {name}: {blueprint}")
    print(f"    蓝图名称: {blueprint.name}")
    print(f"    URL前缀: {getattr(blueprint, 'url_prefix', '无')}")

# 2. 列出所有注册的路由
print("\n🔗 所有注册的路由:")
routes_by_blueprint = {}
for rule in app.url_map.iter_rules():
    if not rule.rule.startswith('/static/'):  # 过滤静态文件路由
        blueprint_name = rule.endpoint.split('.')[0] if '.' in rule.endpoint else ''
        if blueprint_name not in routes_by_blueprint:
            routes_by_blueprint[blueprint_name] = []

        methods = [m for m in rule.methods if m not in ['OPTIONS', 'HEAD']]
        routes_by_blueprint[blueprint_name].append({
            'rule': rule.rule,
            'endpoint': rule.endpoint,
            'methods': methods
        })

for blueprint_name, routes in routes_by_blueprint.items():
    print(f"\n  {blueprint_name} 蓝图:")
    for route in routes:
        print(f"    {', '.join(route['methods']):6} {route['rule']}")

# 3. 测试路由访问
print("\n🧪 测试蓝图连通性:")
with app.test_client() as client:
    # 主蓝图
    resp = client.get('/')
    print(f"  GET /: {resp.status_code}")

    # 认证蓝图
    resp = client.get('/api/auth/test')
    print(f"  GET /api/auth/test: {resp.status_code}")

    # 设备蓝图
    resp = client.get('/api/devices/')
    print(f"  GET /api/devices/: {resp.status_code}")

    # 预约蓝图
    resp = client.get('/api/reservations/')
    print(f"  GET /api/reservations/: {resp.status_code}")

    resp = client.get('/api/reservations/test')
    print(f"  GET /api/reservations/test: {resp.status_code}")

print("\n" + "=" * 60)
print("=== 验证完成 ===")
print("=" * 60)