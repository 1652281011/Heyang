from flask import g
from flask_restful import Resource
from app.api.common.response import success, error
from app.api.common.parser import audit_action_parser # 复用之前的 parser
from app.utils.decorators import admin_required
from app.models import db
from app.models.species_audit import SpeciesAudit
from app.models.species import Species
import time

class SpeciesAuditActionResource(Resource):
    
    method_decorators = [admin_required]
    
    def post(self):
        """管理员审核操作"""
        args = audit_action_parser()
        audit_id = args['audit_id']
        action = args['action'] # pass / reject
        
        # 1. 获取审核记录
        audit = SpeciesAudit.query.filter_by(audit_id=audit_id).first()
        if not audit:
            return error(msg='审核记录不存在')
        
        if audit.status != 0:
            return error(msg='该记录已被审核')

        try:
            current_time = int(time.time())
            
            # === 驳回逻辑 ===
            if action == 'reject':
                audit.status = 2
                audit.reject_reason = args.get('reject_reason', '管理员驳回')
                audit.audit_time = current_time
                audit.auditor_id = getattr(g.user, 'admin_id', 0)
                db.session.commit()
                return success(msg='已驳回')

            # === 通过逻辑 ===
            content = audit.get_content() # 获取 JSON 快照
            
            if audit.operate_type == 'add':
                # --- 新增 ---
                # 二次检查学名冲突 (防止审核期间别人插了一条)
                sc_name = content.get('scientific_name')
                if Species.query.filter_by(scientific_name=sc_name).first():
                    return error(msg='通过失败：该物种学名已存在于数据库中')
                
                new_species = Species()
                # 自动生成ID (如果没有)
                new_species.species_id = "SP" + str(int(time.time()))
                
                for k, v in content.items():
                    # species_id 不从 content 取，防止冲突，使用上面生成的
                    if k != 'species_id' and hasattr(new_species, k):
                        setattr(new_species, k, v)
                
                db.session.add(new_species)
                
            elif audit.operate_type == 'update':
                # --- 修改 ---
                # 使用审核表中记录的 target_species_id 定位，这是最准确的
                target_species = Species.query.filter_by(species_id=audit.target_species_id).first()
                
                # 如果万一ID找不到了（极少情况），尝试用学名再找一次
                if not target_species:
                    sc_name = content.get('scientific_name')
                    target_species = Species.query.filter_by(scientific_name=sc_name).first()

                if not target_species:
                    return error(msg='通过失败：原物种数据已丢失，无法更新')
                
                # 更新字段
                for k, v in content.items():
                    # 排除 species_id 和 scientific_name (通常学名作为Key不建议修改，或者你可以允许修改)
                    # 这里假设允许修改其他信息，但保留原ID
                    if k != 'species_id' and hasattr(target_species, k):
                        setattr(target_species, k, v)
            
            # 更新审核单状态
            audit.status = 1
            audit.audit_time = current_time
            audit.auditor_id = getattr(g.user, 'admin_id', 0)
            
            db.session.commit()
            return success(msg='审核通过，数据已生效')

        except Exception as e:
            db.session.rollback()
            return error(msg='系统错误: ' + str(e))