# -*- coding: utf-8 -*-
import time
from flask import g, current_app
from flask_restful import Resource
from app.models.base import db
from app.models.users import User
from app.models.professor import ProfessionalInfo
from app.api.common.response import success, error
from app.api.common.parser import professional_apply_parser
from app.utils.decorators import login_required
from app.utils.uploader import Uploader

class ProfessionalApplyResource(Resource):
    method_decorators = [login_required]

    def post(self):
        """用户提交专业身份申请"""
        args = professional_apply_parser()
        user = g.user

        # 1. 检查是否已经是专业用户
        if user.role_type == '2':
            return error(msg="您已经是专业用户，无需重复申请")

        # 2. 检查是否有正在审核中的申请
        exist_info = ProfessionalInfo.query.filter_by(user_id=user.id).first()
        if exist_info and exist_info.audit_status == 0:
            return error(msg="您的申请正在审核中，请耐心等待")

        # 3. 上传证明图片
        file_obj = args['certificate']
        config = {
            "pathFormat": "uploads/cert/{yyyy}{mm}{dd}/{time}{rand:6}",
            "maxSize": 10 * 1024 * 1024,  # 提高到 10MB，因为文档可能较大
            "allowFiles": [
                ".png", ".jpg", ".jpeg",  # 图片
                ".pdf", ".doc", ".docx",  # 文档
                ".zip", ".rar"             # 压缩包（可选）
            ],
            "oriName": file_obj.filename
        }
        uploader = Uploader(file_obj, config, current_app.static_folder)
        if uploader.stateInfo != "SUCCESS":
            return error(msg=f"证明文件上传失败: {uploader.stateInfo}")
        
        cert_url = uploader.getFileInfo()['url']

        # 4. 创建或更新申请记录
        if not exist_info:
            exist_info = ProfessionalInfo(user_id=user.id)
        
        exist_info.real_name = args['real_name']
        exist_info.pro_title = args.get('pro_title')
        exist_info.organization = args.get('organization')
        exist_info.expertise_field = args.get('expertise_field')
        exist_info.certificate_file = cert_url
        exist_info.audit_status = 0 # 重置为待审核
        exist_info.c_time = int(time.time())
        exist_info.e_time = int(time.time())

        try:
            db.session.add(exist_info)
            db.session.commit()
            return success(msg="申请提交成功，请等待审核")
        except Exception as e:
            db.session.rollback()
            return error(msg="系统繁忙，提交失败")