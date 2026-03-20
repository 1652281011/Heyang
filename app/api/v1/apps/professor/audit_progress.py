from flask import g
from flask_restful import Resource

from app.api.common.fields import professional_audit_result_fields
from app.api.common.response import success
from app.models.professor import ProfessionalInfo
from app.utils.decorators import login_required
from sqlalchemy.orm import joinedload


class MyProfessionalStatusResource(Resource):
    method_decorators = [login_required]

    def get(self):
        target_uid = g.user.id # 从 Token 拿自己的 ID
        
        pro_info = ProfessionalInfo.query.filter_by(user_id=target_uid).options(
            joinedload(ProfessionalInfo.user), joinedload(ProfessionalInfo.auditor)
        ).first()

        if not pro_info: return success(data={"has_applied": False}, msg="未申请")
        return success(data=pro_info, data_fileds=professional_audit_result_fields())