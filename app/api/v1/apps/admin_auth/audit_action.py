# -*- coding: utf-8 -*-
import time
from flask import g, current_app
from flask_restful import Resource
from app.models import db
from app.api.common.response import success, error
from app.api.common.parser import audit_action_parser
from app.models.species_audit import SpeciesAudit
from app.models.species import Species
# 引入权限控制
from app.utils.decorators import admin_required

class AdminAuditAction(Resource):
    
    method_decorators = [admin_required]

    def post(self):
        """
        管理员审核操作接口
        Action: pass(通过) / reject(驳回)
        """
        # 1. 解析参数
        args = audit_action_parser()
        audit_id = args['audit_id']
        action = args['action']
        reject_reason = args.get('reject_reason')

        # 2. 查找审核记录
        audit = SpeciesAudit.query.filter_by(audit_id=audit_id).first()
        if not audit:
            return error(msg='审核记录不存在', resid=404)
        
        # 防止重复审核
        if audit.status != 0:
            return error(msg='该记录已被审核，请勿重复操作')

        try:
            current_time = int(time.time())
            auditor_id = getattr(g.user, 'admin_id', 0) if hasattr(g, 'user') else 0
            
            # ========================
            # 场景 A: 驳回 (Reject)
            # ========================
            if action == 'reject':
                audit.status = 2  # 状态 2 表示已驳回
                audit.reject_reason = reject_reason if reject_reason else '管理员驳回'
                audit.audit_time = current_time
                audit.auditor_id = auditor_id
                
                db.session.commit()
                return success(msg='操作成功：已驳回申请')

            # ========================
            # 场景 B: 通过 (Pass)
            # ========================
            if action == 'pass':
                # 获取 JSON 快照数据
                content = audit.get_content()
                if not content:
                    return error(msg='数据快照为空，无法入库')

                # --- 分支 1: 新增物种 (Add) ---
                if audit.operate_type == 'add':
                    # 再次检查学名是否冲突 (防止审核期间有其他人插入了同名数据)
                    sc_name = content.get('scientific_name')
                    if Species.query.filter_by(scientific_name=sc_name).first():
                        return error(msg=f'入库失败：学名 [{sc_name}] 已存在于数据库中')

                    new_species = Species()
                    
                    # 赋值字段
                    for k, v in content.items():
                        if k != 'species_id' and hasattr(new_species, k):
                            setattr(new_species, k, v)
                    
                    db.session.add(new_species)

                # --- 分支 2: 修改物种 (Update) ---
                elif audit.operate_type == 'update':
                    # 优先使用 target_species_id 查找原数据
                    target_species = Species.query.filter_by(species_id=audit.target_species_id).first()
                    
                    # 如果找不到，尝试用学名兜底查找
                    if not target_species:
                        sc_name = content.get('scientific_name')
                        target_species = Species.query.filter_by(scientific_name=sc_name).first()

                    if not target_species:
                        return error(msg='入库失败：原物种数据已不存在')

                    # 更新字段
                    for k, v in content.items():
                        # 排除主键，更新其他字段
                        if k != 'species_id' and hasattr(target_species, k):
                            setattr(target_species, k, v)

                # 更新审核记录状态
                audit.status = 1  # 状态 1 表示已通过
                audit.audit_time = current_time
                audit.auditor_id = auditor_id

                db.session.commit()
                return success(msg='操作成功：审核通过，数据已生效')

        except Exception as e:
            db.session.rollback()
            current_app.logger.exception(e)
            return error(msg='系统错误: ' + str(e))