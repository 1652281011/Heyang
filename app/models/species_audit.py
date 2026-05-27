# app/models/species_audit.py
import json
import time
from app.models import db

class SpeciesAudit(db.Model):
    __tablename__ = 'species_audit'
    __table_args__ = {'comment': '物种数据审核表'}

    audit_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    applicant_id = db.Column(db.String(20), nullable=False)
    target_species_id = db.Column(db.Integer, nullable=True) # 修改为 Integer 匹配主表
    operate_type = db.Column(db.String(10), nullable=False)  # add / update
    content_snapshot = db.Column(db.Text, nullable=False)
    status = db.Column(db.Integer, default=0) # 0待审, 1通过, 2驳回
    reject_reason = db.Column(db.String(200), nullable=True)
    create_time = db.Column(db.Integer, default=lambda: int(time.time()))
    audit_time = db.Column(db.Integer, nullable=True)
    auditor_id = db.Column(db.Integer, nullable=True)

    @staticmethod
    def create_audit(applicant_id, operate_type, data_dict, target_id=None):
        audit = SpeciesAudit(
            applicant_id=str(applicant_id),
            operate_type=operate_type,
            target_species_id=target_id,
            content_snapshot=json.dumps(data_dict, ensure_ascii=False),
            create_time=int(time.time()),
            status=0
        )
        db.session.add(audit)
        db.session.commit()
        return audit

    def get_content(self):
        return json.loads(self.content_snapshot) if self.content_snapshot else {}