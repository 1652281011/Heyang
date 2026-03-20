# app/models/species_audit.py
from app.models import db
import json
import time

class SpeciesAudit(db.Model):
    __tablename__ = 'species_audit'
    __table_args__ = {'comment': '物种数据审核表'}

    audit_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='审核记录ID')
    
    # 申请人信息
    applicant_id = db.Column(db.String(20), nullable=False, comment='申请人ID(Professor ID)')
    
    # 审核目标
    target_species_id = db.Column(db.String(20), nullable=True, comment='目标物种ID(新增时可能为空/自增，修改时必填)')
    operate_type = db.Column(db.String(10), nullable=False, comment='操作类型: add(新增), update(修改)')
    
    # 核心数据：将物种的所有字段打包成 JSON 存入这里
    content_snapshot = db.Column(db.Text, nullable=False, comment='数据快照(JSON)')
    
    # 审核状态
    status = db.Column(db.Integer, default=0, comment='状态: 0-待审核, 1-已通过, 2-已驳回')
    reject_reason = db.Column(db.String(200), nullable=True, comment='驳回原因')
    
    create_time = db.Column(db.Integer, default=lambda: int(time.time()))
    audit_time = db.Column(db.Integer, nullable=True)
    auditor_id = db.Column(db.Integer, nullable=True, comment='审核管理员ID')

    @staticmethod
    def create_audit(applicant_id, operate_type, data_dict, target_id=None):
        """创建审核记录"""
        audit = SpeciesAudit()
        audit.applicant_id = applicant_id
        audit.operate_type = operate_type
        audit.target_species_id = target_id
        # 将字典转为 JSON 字符串存储
        audit.content_snapshot = json.dumps(data_dict, ensure_ascii=False)
        audit.create_time = int(time.time())
        
        db.session.add(audit)
        db.session.commit()
        return audit

    def get_content(self):
        """获取解析后的字典数据"""
        if self.content_snapshot:
            return json.loads(self.content_snapshot)
        return {}