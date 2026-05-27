from flask import g
from flask_restful import Resource

from app.api.common.parser import species_audit_update_parser
from app.api.common.response import error, success
from app.services.species.audit_service import AuditQueryService
from app.utils.decorators import expert_required


class ExpertModifyAuditResource(Resource):
    """
    专家修改个人申请接口
    """
    method_decorators = [expert_required]

    def put(self):
        # 1. 解析参数
        args = species_audit_update_parser()
        audit_id = args.get('audit_id')

        # 2. 调用服务层
        # g.user.id 是拦截器解析 Token 后存入的用户 ID
        status, msg = AuditQueryService.update_expert_audit(
            user_id=g.user.id,
            audit_id=audit_id,
            new_data=args
        )

        if not status:
            return error(resid=100, msg=msg)

        return success(msg=msg)