from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Reservation, Device, User
from datetime import datetime
from functools import wraps
from app.auth import verify_token  # 正确的导入语句

bp = Blueprint('reservations', __name__, url_prefix='/api/reservations')


# 复用之前的token_required装饰器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # 从请求头获取令牌
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': '缺少认证令牌'}), 401

        # 解析Bearer令牌
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': '令牌格式错误，应为: Bearer <token>'}), 401

        token = parts[1]
        user_id = verify_token(token)  # 现在应该能正确导入
        if not user_id:
            return jsonify({'error': '令牌无效或已过期'}), 401

        # 获取用户并添加到请求上下文
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404

        # 将用户对象传递给被装饰的函数
        return f(user, *args, **kwargs)

    return decorated


@bp.route('/', methods=['POST'])
@token_required
def create_reservation(user):
    """创建新预约"""
    data = request.get_json()

    # 验证必要字段
    required_fields = ['device_id', 'start_time', 'end_time', 'purpose']
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({'error': f'缺少必要字段: {", ".join(missing_fields)}'}), 400

    try:
        # 解析时间
        start_time = datetime.fromisoformat(data['start_time'])
        end_time = datetime.fromisoformat(data['end_time'])

        # 检查时间有效性
        if start_time >= end_time:
            return jsonify({'error': '结束时间必须晚于开始时间'}), 400

        # 检查设备是否存在
        device = Device.query.get(data['device_id'])
        if not device:
            return jsonify({'error': '设备不存在'}), 404

        # 检查设备是否可用
        if not device.is_available():
            return jsonify({'error': f'设备当前状态为{device.status}，不可预约'}), 400

        # 检查时间冲突
        conflicting_reservations = Reservation.query.filter(
            Reservation.device_id == device.id,
            Reservation.status.in_(['approved', 'in_progress', 'pending']),  # 检查已批准、进行中和待审核的预约
            Reservation.start_time < end_time,
            Reservation.end_time > start_time
        ).all()

        if conflicting_reservations:
            conflict_info = []
            for res in conflicting_reservations:
                conflict_info.append({
                    'id': res.id,
                    'start_time': res.start_time.isoformat(),
                    'end_time': res.end_time.isoformat(),
                    'user_id': res.user_id,
                    'status': res.status
                })

            return jsonify({
                'error': '时间冲突',
                'message': '该时间段内设备已被预约',
                'conflicts': conflict_info
            }), 409

        # 创建预约对象
        reservation = Reservation(
            user_id=user.id,
            device_id=data['device_id'],
            start_time=start_time,
            end_time=end_time,
            purpose=data['purpose'],
            status='pending'  # 初始状态为待审核
        )

        # 可选字段
        optional_fields = ['experiment_name', 'research_field', 'course_name']
        for field in optional_fields:
            if field in data:
                setattr(reservation, field, data[field])

        # 保存到数据库
        db.session.add(reservation)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '预约创建成功，等待审核',
            'reservation': reservation.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({'error': f'时间格式错误: {e}'}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'创建预约失败: {e}')
        return jsonify({'error': '创建预约失败'}), 500


# 添加测试路由
@bp.route('/test', methods=['GET'])
def test():
    """测试预约路由是否正常工作"""
    return jsonify({
        'success': True,
        'message': '预约API工作正常',
        'timestamp': datetime.utcnow().isoformat()
    })