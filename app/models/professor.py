# -*- coding: utf-8 -*-
import time
from .base import db, BaseModel

class ProfessionalInfo(db.Model, BaseModel):
    __tablename__ = 'professional_info'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), unique=True, nullable=False)
    auditor_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'), nullable=True)
    
    real_name = db.Column(db.String(50), nullable=False, comment='姓名')
    pro_title = db.Column(db.String(100), comment='职称')
    organization = db.Column(db.String(100), comment='机构')
    certificate_file = db.Column(db.String(255), nullable=False, comment='证明材料')
    expertise_field = db.Column(db.Text, comment='研究领域')
    
    audit_status = db.Column(db.Integer, default=0, comment='审核状态') # 0:待审, 1:通过, 2:驳回
    reject_reason = db.Column(db.String(255), comment='拒绝理由')
    audit_time = db.Column(db.Integer, comment='审核时间')

    # 关联 User 对象
    user = db.relationship('User', back_populates='pro_info')
    auditor = db.relationship('Admin', foreign_keys=[auditor_id])

    @property
    def auditor_name(self):
        """获取审核员真实姓名，如果没有则返回用户名"""
        if self.auditor:
            return self.auditor.real_name if self.auditor.real_name else self.auditor.username
        return u"系统自动"

    @property
    def apply_time_format(self):
        """格式化申请时间"""
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.c_time)) if self.c_time else ""

    @property
    def audit_time_format(self):
        """格式化审核时间"""
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.audit_time)) if self.audit_time else "尚未审核"

    def to_dict(self):
        import os
        file_path = self.certificate_file or ""
        # 获取后缀名
        extension = os.path.splitext(file_path)[-1].lower()
        
        return {
            "id": self.id,
            "user_id": self.user_id,
            "real_name": self.real_name,
            "pro_title": self.pro_title or "",
            "audit_status": self.audit_status,
            "reject_reason": self.reject_reason or "",
            "apply_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.c_time)) if self.c_time else "",
            "audit_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.audit_time)) if self.audit_time else ""
        }