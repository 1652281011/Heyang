from flask import g, request
from flask_restful import Resource

from app.api.common.fields import get_audit_detail_fields
from app.api.common.response import error, success
from app.services.species.audit_service import AuditQueryService
from app.utils.decorators import login_required


class SpeciesAuditDetail(Resource):
    method_decorators = [login_required]

    def get(self):
        """获取单条审核记录详情"""
        audit_id = request.args.get('audit_id')
        

        is_admin = str(g.user.role_type) in ['8', '9']
        
        data, msg = AuditQueryService.get_detail(
            audit_id=audit_id, 
            user_id=g.user.id, 
            is_admin=is_admin
        )

        if not data:
            return error(resid=403, msg=msg)

        return success(data=data, data_fileds=get_audit_detail_fields())