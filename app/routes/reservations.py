from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Reservation, Device, User
from datetime import datetime, timezone
from functools import wraps
from app.auth import verify_token

bp = Blueprint('reservations', __name__, url_prefix='/api/reservations')


# ==================== 权限验证装饰器 ====================

def token_required(f):
    """验证JWT令牌的装饰器"""

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
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'error': '令牌无效或已过期'}), 401

        # 获取用户并添加到请求上下文
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404

        # 将用户对象传递给被装饰的函数
        return f(user, *args, **kwargs)

    return decorated


def admin_required(f):
    """验证管理员权限的装饰器"""

    @wraps(f)
    def decorated(user, *args, **kwargs):
        if not user.is_admin():
            return jsonify({'error': '需要管理员权限'}), 403
        return f(user, *args, **kwargs)

    return decorated


# ==================== 预约API接口 ====================

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
        start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))

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
            Reservation.device_id == data['device_id'],
            Reservation.status.in_(['approved', 'pending', 'in_progress']),
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


@bp.route('/', methods=['GET'])
@token_required
def get_reservations(user):
    """获取预约列表（支持分页、筛选、排序）"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # 筛选参数
        user_id = request.args.get('user_id', type=int)
        device_id = request.args.get('device_id', type=int)
        status = request.args.get('status')

        # 时间范围
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # 搜索关键词
        search = request.args.get('search')

        # 构建查询
        query = Reservation.query

        # 权限控制：普通用户只能查看自己的预约
        if not user.is_admin():
            query = query.filter(Reservation.user_id == user.id)
        elif user_id:  # 管理员可以按用户筛选
            query = query.filter(Reservation.user_id == user_id)

        # 其他筛选条件
        if device_id:
            query = query.filter(Reservation.device_id == device_id)

        if status:
            status_list = status.split(',')
            query = query.filter(Reservation.status.in_(status_list))

        # 时间范围筛选
        if start_date:
            start_time = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(Reservation.start_time >= start_time)

        if end_date:
            end_time = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(Reservation.end_time <= end_time)

        # 搜索功能
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                (Reservation.purpose.ilike(search_pattern)) |
                (Reservation.experiment_name.ilike(search_pattern))
            )

        # 排序：默认按创建时间倒序
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')

        if sort_order == 'asc':
            query = query.order_by(getattr(Reservation, sort_by).asc())
        else:
            query = query.order_by(getattr(Reservation, sort_by).desc())

        # 分页查询
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        reservations = pagination.items

        return jsonify({
            'success': True,
            'data': [res.to_dict(detail=True) for res in reservations],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            },
            'filters': {
                'user_id': user_id,
                'device_id': device_id,
                'status': status,
                'start_date': start_date,
                'end_date': end_date,
                'search': search,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
        })

    except Exception as e:
        current_app.logger.error(f'获取预约列表失败: {e}')
        return jsonify({'success': False, 'error': '获取预约列表失败'}), 500


@bp.route('/<int:reservation_id>', methods=['GET'])
@token_required
def get_reservation(user, reservation_id):
    """获取单个预约详情"""
    try:
        reservation = Reservation.query.get_or_404(reservation_id)

        # 权限验证：普通用户只能查看自己的预约
        if not user.is_admin() and reservation.user_id != user.id:
            return jsonify({'error': '无权查看此预约'}), 403

        return jsonify({
            'success': True,
            'data': reservation.to_dict(detail=True)
        })

    except Exception as e:
        current_app.logger.error(f'获取预约详情失败: {e}')
        return jsonify({'success': False, 'error': '获取预约详情失败'}), 500


@bp.route('/<int:reservation_id>/status', methods=['PUT'])
@token_required
@admin_required
def update_reservation_status(user, reservation_id):
    """更新预约状态（管理员权限）"""
    try:
        reservation = Reservation.query.get_or_404(reservation_id)
        data = request.get_json()

        if not data or 'status' not in data:
            return jsonify({'success': False, 'error': '缺少状态字段'}), 400

        new_status = data['status']
        notes = data.get('notes')

        # 根据目标状态执行相应的操作
        if new_status == 'approved':
            # 批准预约
            can_approve, message = reservation.can_be_approved()
            if not can_approve:
                return jsonify({'success': False, 'error': message}), 400

            reservation.status = 'approved'
            reservation.reviewed_by = user.id
            reservation.reviewed_at = datetime.now(timezone.utc)
            reservation.review_notes = notes
            reservation.updated_at = datetime.now(timezone.utc)

            # 更新设备状态
            device = Device.query.get(reservation.device_id)
            if device:
                device.status = 'reserved'
                db.session.add(device)

        elif new_status == 'rejected':
            # 拒绝预约
            if reservation.status != 'pending':
                return jsonify(
                    {'success': False, 'error': f'只有待审核的预约可拒绝，当前状态: {reservation.status}'}), 400

            reservation.status = 'rejected'
            reservation.reviewed_by = user.id
            reservation.reviewed_at = datetime.now(timezone.utc)
            reservation.review_notes = notes or '预约被拒绝'
            reservation.updated_at = datetime.now(timezone.utc)

        elif new_status == 'in_progress':
            # 开始使用
            if reservation.status != 'approved':
                return jsonify(
                    {'success': False, 'error': f'只有已批准的预约可开始使用，当前状态: {reservation.status}'}), 400

            reservation.status = 'in_progress'
            reservation.actual_start_time = datetime.now(timezone.utc)
            reservation.updated_at = datetime.now(timezone.utc)

            # 更新设备状态
            device = Device.query.get(reservation.device_id)
            if device:
                device.status = 'in_use'
                db.session.add(device)

        elif new_status == 'completed':
            # 完成使用
            if reservation.status != 'in_progress':
                return jsonify(
                    {'success': False, 'error': f'只有进行中的预约可完成，当前状态: {reservation.status}'}), 400

            reservation.status = 'completed'
            reservation.actual_end_time = datetime.now(timezone.utc)
            reservation.updated_at = datetime.now(timezone.utc)

            # 处理使用时长和反馈
            actual_hours = data.get('actual_hours')
            usage_notes = data.get('usage_notes')
            feedback = data.get('feedback')
            rating = data.get('rating')

            if actual_hours:
                reservation.actual_usage_hours = float(actual_hours)
            elif reservation.actual_start_time and reservation.actual_end_time:
                duration = (reservation.actual_end_time - reservation.actual_start_time).total_seconds() / 3600
                reservation.actual_usage_hours = round(duration, 2)

            if usage_notes:
                reservation.usage_notes = usage_notes
            if feedback:
                reservation.device_feedback = feedback
            if rating:
                reservation.rating = int(rating)

            # 更新设备状态和使用统计
            device = Device.query.get(reservation.device_id)
            if device:
                device.status = 'available'
                if reservation.actual_usage_hours:
                    # 处理可能为None的情况
                    if device.total_usage_hours is None:
                        device.total_usage_hours = 0.0
                    if device.usage_count is None:
                        device.usage_count = 0

                    device.total_usage_hours += reservation.actual_usage_hours
                    device.usage_count += 1
                db.session.add(device)

        else:
            return jsonify({'success': False, 'error': f'不支持的状态: {new_status}'}), 400

        # 保存更改
        db.session.commit()

        current_app.logger.info(f'管理员 {user.username} 更新预约状态: {reservation.id} -> {new_status}')

        return jsonify({
            'success': True,
            'message': f'预约状态已更新为 {reservation.status}',
            'data': reservation.to_dict(detail=True)
        })

    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'更新预约状态失败: {e}')
        return jsonify({'success': False, 'error': '更新预约状态失败'}), 500


@bp.route('/<int:reservation_id>', methods=['DELETE'])
@token_required
def cancel_reservation(user, reservation_id):
    """取消预约"""
    try:
        reservation = Reservation.query.get_or_404(reservation_id)

        # 权限验证：普通用户只能取消自己的预约
        if not user.is_admin() and reservation.user_id != user.id:
            return jsonify({'error': '无权取消此预约'}), 403

        data = request.get_json() or {}
        reason = data.get('reason', '用户取消')

        # 检查是否可取消
        if reservation.status in ['completed', 'cancelled']:
            return jsonify({'error': f'当前状态为{reservation.status}，不可取消'}), 400

        # 如果是已批准的预约，需要释放设备
        if reservation.status == 'approved':
            device = Device.query.get(reservation.device_id)
            if device:
                device.status = 'available'
                db.session.add(device)

        # 更新预约状态
        reservation.status = 'cancelled'
        reservation.cancelled_at = datetime.now(timezone.utc)
        reservation.updated_at = datetime.now(timezone.utc)
        reservation.review_notes = f'取消原因: {reason}'

        # 保存更改
        db.session.commit()

        current_app.logger.info(f'用户 {user.username} 取消预约: {reservation.id}')

        return jsonify({
            'success': True,
            'message': '预约已取消',
            'data': reservation.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'取消预约失败: {e}')
        return jsonify({'success': False, 'error': '取消预约失败'}), 500


# ==================== 测试路由 ====================

@bp.route('/test', methods=['GET'])
def test():
    """测试预约路由是否正常工作"""
    return jsonify({
        'success': True,
        'message': '预约API工作正常',
        'endpoints': [
            {'method': 'POST', 'path': '/api/reservations/', 'description': '创建预约'},
            {'method': 'GET', 'path': '/api/reservations/', 'description': '获取预约列表'},
            {'method': 'GET', 'path': '/api/reservations/<id>', 'description': '获取预约详情'},
            {'method': 'PUT', 'path': '/api/reservations/<id>/status', 'description': '更新预约状态'},
            {'method': 'DELETE', 'path': '/api/reservations/<id>', 'description': '取消预约'}
        ],
        'timestamp': datetime.now(timezone.utc).isoformat()
    })