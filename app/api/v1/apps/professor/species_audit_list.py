from flask import g, request
from flask_restful import Resource

from app.api.common.fields import get_audit_list_fields
from app.api.common.response import success
from app.services.species.audit_service import AuditQueryService
from app.utils.decorators import expert_required


class ExpertAuditList(Resource):
    method_decorators = [expert_required]

    def get(self):
        """专家查看自己提交的申请列表"""
        page = int(request.args.get('page', 1))
        
        # 传入 g.user.id 进行过滤
        res = AuditQueryService.get_list(page=page, applicant_id=g.user.id)
        
        data = {
            'audit_list': res['items'],
            'pagination': {
                'total': res['total'], 'page': page, 'per_page': res['per_page']
            }
        }
        return success(data=data, data_fileds=get_audit_list_fields())