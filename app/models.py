from app import db
from datetime import datetime, timedelta
import json
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app


class User(db.Model):
    """用户表 - 管理系统用户账户"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='student', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系：用户发起的预约
    reservations_as_applicant = db.relationship(
        'Reservation',
        foreign_keys='Reservation.user_id',
        backref='applicant_user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    # 关系：用户审核的预约
    reservations_as_reviewer = db.relationship(
        'Reservation',
        foreign_keys='Reservation.reviewed_by',
        backref='reviewer_user',
        lazy='dynamic'
    )

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role in ['admin', 'super']

    def generate_auth_token(self, expires_in=3600):
        """生成JWT令牌"""
        from app.auth import generate_token
        return generate_token(self.id, expires_in)

    @staticmethod
    def verify_auth_token(token):
        """验证JWT令牌并返回用户对象"""
        from app.auth import verify_token
        user_id = verify_token(token)
        if user_id is None:
            return None
        return User.query.get(user_id)

    def to_dict(self):
        """将用户信息转为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Device(db.Model):
    """实验室设备表 - 增强版"""
    __tablename__ = 'devices'

    id = db.Column(db.Integer, primary_key=True)

    # 设备唯一标识
    device_id = db.Column(db.String(50), unique=True, nullable=False, index=True, comment='设备唯一编号')
    qr_code = db.Column(db.String(100), unique=True, nullable=True, comment='二维码标识')

    # 设备基本信息
    name = db.Column(db.String(100), nullable=False, comment='设备名称')
    device_type = db.Column(db.String(50), nullable=False, comment='设备类型')
    category = db.Column(db.String(50), default='general', comment='设备分类')

    # 设备厂商信息
    brand = db.Column(db.String(50), comment='品牌')
    model = db.Column(db.String(50), comment='型号')
    serial_number = db.Column(db.String(100), unique=True, nullable=True, comment='序列号')

    # 设备状态管理
    status = db.Column(db.String(20), default='available', nullable=False,
                       comment='设备状态：available(可用), reserved(已预约), in_use(使用中), maintenance(维修中), retired(已退役)')
    location = db.Column(db.String(100), comment='存放位置')
    lab_room = db.Column(db.String(50), comment='实验室房间号')

    # 设备规格参数
    specifications = db.Column(db.Text, comment='规格参数')
    description = db.Column(db.Text, comment='设备描述')
    technical_parameters = db.Column(db.JSON, nullable=True, comment='技术参数JSON格式')

    # 使用统计
    total_usage_hours = db.Column(db.Float, default=0.0, comment='累计使用时长(小时)')
    usage_count = db.Column(db.Integer, default=0, comment='使用次数')
    last_used_at = db.Column(db.DateTime, nullable=True, comment='上次使用时间')

    # 维护信息
    purchase_date = db.Column(db.DateTime, nullable=True, comment='购买日期')
    warranty_period = db.Column(db.Integer, nullable=True, comment='保修期(月)')
    maintenance_interval = db.Column(db.Integer, default=6, comment='维护间隔(月)')
    last_maintenance = db.Column(db.DateTime, nullable=True, comment='上次维护时间')
    next_maintenance = db.Column(db.DateTime, nullable=True, comment='下次计划维护')

    # 管理信息
    responsible_person = db.Column(db.String(50), nullable=True, comment='负责人')
    contact_info = db.Column(db.String(100), nullable=True, comment='联系方式')
    is_shared = db.Column(db.Boolean, default=True, comment='是否共享设备')
    max_reservation_hours = db.Column(db.Integer, default=4, comment='单次最大预约时长(小时)')

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='入库时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 关系
    reservations = db.relationship('Reservation',
                                   foreign_keys='[Reservation.device_id]',
                                   backref='device_info',
                                   lazy='dynamic',
                                   cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Device {self.device_id}: {self.name}>'

    def to_dict(self, detail=False):
        """将设备信息转为字典"""
        # 处理可能为None的字段
        total_hours = self.total_usage_hours if self.total_usage_hours is not None else 0.0
        usage_count = self.usage_count if self.usage_count is not None else 0
        is_shared = self.is_shared if self.is_shared is not None else True

        base_info = {
            'id': self.id,
            'device_id': self.device_id,
            'name': self.name,
            'type': self.device_type,
            'category': self.category if self.category else 'general',
            'status': self.status,
            'location': self.location,
            'lab_room': self.lab_room,
            'total_usage_hours': total_hours,
            'usage_count': usage_count,
            'is_shared': is_shared,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if detail:
            detail_info = {
                'brand': self.brand,
                'model': self.model,
                'serial_number': self.serial_number,
                'specifications': self.specifications,
                'description': self.description,
                'technical_parameters': self.technical_parameters,
                'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
                'warranty_period': self.warranty_period,
                'maintenance_interval': self.maintenance_interval if self.maintenance_interval is not None else 6,
                'last_maintenance': self.last_maintenance.isoformat() if self.last_maintenance else None,
                'next_maintenance': self.next_maintenance.isoformat() if self.next_maintenance else None,
                'responsible_person': self.responsible_person,
                'contact_info': self.contact_info,
                'max_reservation_hours': self.max_reservation_hours if self.max_reservation_hours is not None else 4,
                'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
                'qr_code': self.qr_code,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }
            base_info.update(detail_info)

        return base_info

    def update_status(self, new_status):
        """更新设备状态（包含状态验证）"""
        valid_statuses = ['available', 'reserved', 'in_use', 'maintenance', 'retired']
        if new_status not in valid_statuses:
            raise ValueError(f'状态无效，必须是: {", ".join(valid_statuses)}')

        self.status = new_status
        self.updated_at = datetime.utcnow()
        return True

    def record_usage(self, hours):
        """记录设备使用时长"""
        if hours <= 0:
            raise ValueError('使用时长必须大于0')

        # 处理可能为None的情况
        if self.total_usage_hours is None:
            self.total_usage_hours = 0.0
        if self.usage_count is None:
            self.usage_count = 0

        self.total_usage_hours += hours
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return True

    def is_available(self):
        """检查设备是否可用"""
        return self.status == 'available'

    def can_be_reserved(self, hours):
        """检查设备是否可以被预约"""
        if not self.is_available():
            return False, f'设备当前状态为{self.status}，不可预约'

        max_hours = self.max_reservation_hours if self.max_reservation_hours is not None else 4
        if hours > max_hours:
            return False, f'超过单次最大预约时长({max_hours}小时)'

        if self.status in ['maintenance', 'retired']:
            return False, f'设备{self.status}，不可预约'

        return True, '设备可预约'

    def schedule_maintenance(self, next_date=None):
        """安排维护"""
        if next_date:
            self.next_maintenance = next_date
        else:
            # 默认维护间隔月后
            interval = self.maintenance_interval if self.maintenance_interval is not None else 6
            self.next_maintenance = datetime.utcnow() + timedelta(days=30 * interval)

        self.updated_at = datetime.utcnow()
        return self.next_maintenance

    def to_qr_data(self):
        """生成设备二维码数据"""
        return {
            'device_id': self.device_id,
            'name': self.name,
            'type': self.device_type,
            'status': self.status,
            'location': self.location,
            'qr_code': self.qr_code or f'device_{self.device_id}'
        }


class Reservation(db.Model):
    """设备预约表 - 增强版"""
    __tablename__ = 'reservations'

    id = db.Column(db.Integer, primary_key=True)

    # 关联信息
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True, comment='预约用户ID')
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False, index=True, comment='预约设备ID')

    # 预约时间
    start_time = db.Column(db.DateTime, nullable=False, index=True, comment='预约开始时间')
    end_time = db.Column(db.DateTime, nullable=False, index=True, comment='预约结束时间')
    actual_start_time = db.Column(db.DateTime, nullable=True, comment='实际开始时间')
    actual_end_time = db.Column(db.DateTime, nullable=True, comment='实际结束时间')

    # 预约信息
    purpose = db.Column(db.String(500), nullable=False, comment='使用目的')
    experiment_name = db.Column(db.String(200), comment='实验名称')
    research_field = db.Column(db.String(100), comment='研究领域')
    course_name = db.Column(db.String(100), comment='课程名称')

    # 预约状态管理
    status = db.Column(db.String(20), default='pending', nullable=False,
                       comment='预约状态：pending(待审核), approved(已批准), rejected(已拒绝), in_progress(进行中), completed(已完成), cancelled(已取消)')
    review_notes = db.Column(db.Text, comment='审核意见')
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, comment='审核人ID')
    reviewed_at = db.Column(db.DateTime, comment='审核时间')

    # 使用反馈
    actual_usage_hours = db.Column(db.Float, default=0.0, comment='实际使用时长(小时)')
    usage_notes = db.Column(db.Text, comment='使用备注')
    device_feedback = db.Column(db.Text, comment='设备使用反馈')
    rating = db.Column(db.Integer, comment='设备评分(1-5)')

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    cancelled_at = db.Column(db.DateTime, comment='取消时间')

    def __repr__(self):
        return f'<Reservation {self.id}: {self.user_id}->{self.device_id}>'

    def to_dict(self, detail=False):
        """将预约信息转为字典"""
        base_info = {
            'id': self.id,
            'user_id': self.user_id,
            'device_id': self.device_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'purpose': self.purpose,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'duration_hours': self.get_duration_hours() if self.start_time and self.end_time else 0
        }

        if detail:
            detail_info = {
                'actual_start_time': self.actual_start_time.isoformat() if self.actual_start_time else None,
                'actual_end_time': self.actual_end_time.isoformat() if self.actual_end_time else None,
                'experiment_name': self.experiment_name,
                'research_field': self.research_field,
                'course_name': self.course_name,
                'review_notes': self.review_notes,
                'reviewed_by': self.reviewed_by,
                'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
                'actual_usage_hours': self.actual_usage_hours if self.actual_usage_hours is not None else 0.0,
                'usage_notes': self.usage_notes,
                'device_feedback': self.device_feedback,
                'rating': self.rating,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None,
                'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None
            }
            base_info.update(detail_info)

        return base_info

    def get_duration_hours(self):
        """计算预约时长（小时）"""
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds() / 3600
            return round(duration, 2)
        return 0

    def get_actual_duration_hours(self):
        """计算实际使用时长（小时）"""
        if self.actual_start_time and self.actual_end_time:
            duration = (self.actual_end_time - self.actual_start_time).total_seconds() / 3600
            return round(duration, 2)
        return self.actual_usage_hours or 0

    def check_time_conflict(self, other_start, other_end):
        """检查时间冲突（核心算法）"""
        # 如果当前预约已取消或拒绝，不视为冲突
        if self.status in ['cancelled', 'rejected']:
            return False

        return (self.start_time < other_end) and (self.end_time > other_start)

    def can_be_approved(self):
        """检查预约是否可以被批准"""
        if self.status != 'pending':
            return False, f'当前状态为{self.status}，不可批准'

        # 检查设备是否可用
        device = Device.query.get(self.device_id)
        if not device:
            return False, '设备不存在'

        if device.status != 'available':
            return False, f'设备当前状态为{device.status}，不可预约'

        return True, '可批准'

    def approve(self, reviewer_id, notes=None):
        """批准预约"""
        can_approve, message = self.can_be_approved()
        if not can_approve:
            raise ValueError(message)

        # 更新预约状态
        self.status = 'approved'
        self.reviewed_by = reviewer_id
        self.reviewed_at = datetime.utcnow()
        self.review_notes = notes
        self.updated_at = datetime.utcnow()

        # 更新设备状态
        device = Device.query.get(self.device_id)
        device.update_status('reserved')

        db.session.add(device)

        return True

    def reject(self, reviewer_id, notes):
        """拒绝预约"""
        if self.status != 'pending':
            raise ValueError(f'只有待审核的预约可拒绝，当前状态: {self.status}')

        self.status = 'rejected'
        self.reviewed_by = reviewer_id
        self.reviewed_at = datetime.utcnow()
        self.review_notes = notes
        self.updated_at = datetime.utcnow()

        return True

    def start_usage(self):
        """开始使用设备"""
        if self.status != 'approved':
            raise ValueError(f'只有已批准的预约可开始使用，当前状态: {self.status}')

        self.status = 'in_progress'
        self.actual_start_time = datetime.utcnow()
        self.updated_at = datetime.utcnow()

        # 更新设备状态
        device = Device.query.get(self.device_id)
        device.update_status('in_use')

        db.session.add(device)

        return True

    def complete_usage(self, actual_hours=None, notes=None, feedback=None, rating=None):
        """完成使用"""
        if self.status != 'in_progress':
            raise ValueError(f'只有进行中的预约可完成，当前状态: {self.status}')

        self.status = 'completed'
        self.actual_end_time = datetime.utcnow()
        self.usage_notes = notes
        self.device_feedback = feedback
        self.rating = rating
        self.updated_at = datetime.utcnow()

        # 计算实际使用时长
        if actual_hours:
            self.actual_usage_hours = actual_hours
        elif self.actual_start_time and self.actual_end_time:
            self.actual_usage_hours = self.get_actual_duration_hours()

        # 更新设备状态和使用统计
        device = Device.query.get(self.device_id)
        device.update_status('available')
        if self.actual_usage_hours:
            device.record_usage(self.actual_usage_hours)

        db.session.add(device)

        return True

    def cancel(self, user_id, reason=None):
        """取消预约"""
        # 只有预约本人或管理员可取消
        if user_id != self.user_id:
            user = User.query.get(user_id)
            if not user or not user.is_admin():
                raise ValueError('无权取消他人预约')

        # 检查是否可取消
        if self.status in ['cancelled', 'completed', 'in_progress']:
            raise ValueError(f'当前状态为{self.status}，不可取消')

        # 如果是已批准的预约，需要释放设备
        if self.status == 'approved':
            device = Device.query.get(self.device_id)
            device.update_status('available')
            db.session.add(device)

        self.status = 'cancelled'
        self.cancelled_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

        if reason:
            self.review_notes = f'取消原因: {reason}'

        return True

    def is_overdue(self):
        """检查是否超时（结束时间已过但未完成）"""
        if self.status in ['completed', 'cancelled', 'rejected']:
            return False

        if self.end_time and self.end_time < datetime.utcnow():
            return True

        return False

    def get_status_display(self):
        """获取状态显示文本"""
        status_map = {
            'pending': '待审核',
            'approved': '已批准',
            'rejected': '已拒绝',
            'in_progress': '进行中',
            'completed': '已完成',
            'cancelled': '已取消'
        }
        return status_map.get(self.status, self.status)