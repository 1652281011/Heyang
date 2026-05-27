import time

from flask import g
from app.models import db
from flask_restful import Resource

from app.api.common.parser import audit_action_parser
from app.api.common.response import error, success
from app.models.species import Species
from app.models.species_audit import SpeciesAudit
from app.utils.decorators import admin_required


class SpeciesAuditActionResource(Resource):
    method_decorators = [admin_required]

    def post(self):
        """管理员执行审核通过/驳回"""
        args = audit_action_parser()
        audit_id = args['audit_id']
        action = args['action'] # 'pass' 或 'reject'
        
        audit = SpeciesAudit.query.get(audit_id)
        if not audit or audit.status != 0:
            return error(msg='记录不存在或已处理')

        try:
            now = int(time.time())
            
            # 1. 驳回逻辑
            if action == 'reject':
                audit.status = 2
                audit.reject_reason = args.get('reject_reason', '管理员驳回')
                audit.audit_time = now
                audit.auditor_id = g.user.id
                db.session.commit()
                return success(msg='已成功驳回该申请')

            # 2. 通过逻辑
            content = audit.get_content()
            
            if audit.operate_type == 'add':
                # --- 执行新增上线 ---
                # 二次校验防止并发冲突
                if Species.query.filter_by(chinese_name=content.get('chinese_name')).first():
                    return error(msg='通过失败：该中文名在正式库中已存在')
                
                new_sp = Species()
                # 动态填充 20 个字段
                for key, value in content.items():
                    if hasattr(new_sp, key) and key != 'species_id':
                        setattr(new_sp, key, value)
                
                new_sp.c_time = now
                new_sp.e_time = now
                db.session.add(new_sp)

            elif audit.operate_type == 'update':
                # --- 执行修改上线 ---
                target_sp = Species.query.get(audit.target_species_id)
                if not target_sp:
                    return error(msg='通过失败：原数据已丢失')

                # 动态更新字段
                for key, value in content.items():
                    if hasattr(target_sp, key) and key != 'species_id':
                        setattr(target_sp, key, value)
                
                target_sp.e_time = now

            # 更新审核单状态
            audit.status = 1
            audit.audit_time = now
            audit.auditor_id = g.user.id
            
            db.session.commit()
            return success(msg='审核通过，数据已实时上线')

        except Exception as e:
            db.session.rollback()
            return error(msg=f'审核处理异常: {str(e)}')