# app/services/species/audit_service.py
import json
import time
from app.models import db
from app.models.species_audit import SpeciesAudit

class AuditQueryService:

    @staticmethod
    def get_list(page=1, per_page=10, applicant_id=None, status=None):
        """
        获取审核列表
        :param applicant_id: 如果传入则只看该专家的，不传则看全部（管理员用）
        """
        query = db.session.query(SpeciesAudit)
        
        if applicant_id:
            query = query.filter(SpeciesAudit.applicant_id == str(applicant_id))
        
        if status is not None:
            query = query.filter(SpeciesAudit.status == status)

        pagination = query.order_by(SpeciesAudit.create_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return {
            "items": pagination.items,
            "total": pagination.total,
            "page": page,
            "per_page": per_page
        }

    @staticmethod
    def get_detail(audit_id, user_id=None, is_admin=False):
        """
        获取审核详情
        """
        audit = db.session.query(SpeciesAudit).get(audit_id)
        if not audit:
            return None, "记录不存在"
        
        # 权限检查：非管理员只能看自己的申请
        if not is_admin and audit.applicant_id != str(user_id):
            return None, "无权查看此记录"

        # 调用模型中的 get_content() 方法将 snapshot 转为字典
        res = {c.name: getattr(audit, c.name) for c in audit.__table__.columns}
        res['content'] = audit.get_content()
        
        return res, "获取成功"
    
    @staticmethod
    def update_expert_audit(user_id, audit_id, new_data):
        """
        专家修改自己尚未通过的申请
        """
        # 1. 查找记录
        audit = db.session.query(SpeciesAudit).get(audit_id)
        
        if not audit:
            return False, "未找到该审核记录"

        # 2. 权限校验：只能修改自己的记录
        if str(audit.applicant_id) != str(user_id):
            return False, "无权修改他人的申请记录"

        # 3. 状态校验：只有【待审核 0】和【已驳回 2】可以修改
        # 已通过(1)的内容已经同步到正式库，不能直接改审核单
        if audit.status == 1:
            return False, "该申请已通过审核并上线，无法修改。如需更正请提交新的修改申请。"

        try:
            # 4. 重新打包 JSON 快照
            # 过滤掉 audit_id 等非业务字段
            snapshot_data = {k: v for k, v in new_data.items() if k != 'audit_id' and v is not None}
            audit.content_snapshot = json.dumps(snapshot_data, ensure_ascii=False)
            
            # 5. 重置状态
            # 如果之前是“已驳回”，修改后状态重新变为“待审核”，提醒管理员再次查看
            audit.status = 0
            audit.reject_reason = None # 清空之前的驳回原因
            audit.create_time = int(time.time()) # 更新提交时间
            
            db.session.commit()
            return True, "修改成功，已重新进入审核队列"
            
        except Exception as e:
            db.session.rollback()
            return False, f"系统错误: {str(e)}"