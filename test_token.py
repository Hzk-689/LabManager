from app import create_app, db
from app.models import User


def test_token_auth():
    app = create_app()

    with app.app_context():
        print("=== 测试令牌认证流程 ===")

        # 1. 清理可能存在的旧测试用户
        User.query.filter_by(username='token_test').delete()
        db.session.commit()

        # 2. 创建并保存测试用户
        test_user = User(
            username='token_test',
            email='token@test.com',
            role='student'
        )
        test_user.set_password('test123')

        db.session.add(test_user)
        db.session.commit()
        print(f"✅ 测试用户保存成功，ID: {test_user.id}")

        # 3. 生成令牌
        token = test_user.generate_auth_token()
        print(f"✅ 令牌生成成功 (截取前30位): {token[:30]}...")

        # 4. 验证令牌
        verified_user = User.verify_auth_token(token)
        if verified_user:
            print(f"✅ 令牌验证成功，用户: {verified_user.username}")
            print(f"   用户ID匹配: {verified_user.id == test_user.id}")

            # 5. 测试令牌失效场景（可选）
            import jwt
            try:
                # 尝试篡改令牌
                invalid_token = token[:-5] + "XXXXX"
                invalid_user = User.verify_auth_token(invalid_token)
                print(f"✅ 篡改令牌测试: {'验证失败(正确)' if not invalid_user else '验证通过(错误)'}")
            except:
                print("✅ 令牌篡改测试完成")

        else:
            print("❌ 令牌验证失败")

        print("=== 测试完成 ===")


if __name__ == '__main__':
    test_token_auth()