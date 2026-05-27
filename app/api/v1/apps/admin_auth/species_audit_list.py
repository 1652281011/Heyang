from flask import request
from flask_restful import Resource

from app.api.common.fields import get_audit_list_fields
from app.api.common.response import success
from app.services.species.audit_service import AuditQueryService
from app.utils.decorators import admin_required


class AdminAuditList(Resource):
    method_decorators = [admin_required]

    def get(self):
        """管理员查看所有专家的物种申请"""
        args = request.args
        page = int(args.get('page', 1))
        status = args.get('status') # 可选：0-待审, 1-通过, 2-驳回

        res = AuditQueryService.get_list(page=page, status=status)
        
        data = {
            'audit_list': res['items'],
            'pagination': {
                'total': res['total'], 'page': page, 'per_page': res['per_page']
            }
        }
        return success(data=data, data_fileds=get_audit_list_fields())