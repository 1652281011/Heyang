# -*- coding: utf-8 -*-
import os
import uuid
from flask import current_app, request
from flask_restful import Resource
from app.api.common.response import success, error
from app.api.common.parser import species_ident_preview_parser
from app.api.common.fields import ai_preview_fields
from app.utils.ai_engine import ai_engine

class SpeciesAIPreview(Resource):
    def post(self):
        file = request.files.get('image')
        if not file:
            return error(msg='请上传图片')

        # 1. 获取上传文件夹路径
        # 如果你没在 config 里配，这里会报错，所以给个默认值防止崩溃
        upload_dir = current_app.config.get('UPLOAD_FOLDER')
        if not upload_dir:
            # 兜底方案：如果配置里没写，直接用项目下的 static/uploads
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')

        # 确保物理目录存在
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # 2. 生成文件名并保存
        ext = os.path.splitext(file.filename)[1] # 获取后缀
        filename = str(uuid.uuid4()) + ext
        full_path = os.path.join(upload_dir, filename)
        
        file.save(full_path) # 保存到物理路径

        # 3. 调用 AI 引擎 (注意：file.save 之后指针可能在末尾，重置一下)
        file.seek(0)
        suggestions = ai_engine.predict(file)

        # 4. 构造前端访问图片的 URL
        # 注意：这里返回的是相对路径，供前端预览和下一步发帖使用
        image_url = f"/static/uploads/{filename}"

        return success(
            msg='AI识别成功',
            data={
                'suggestions': suggestions,
                'image_url': image_url  # 关键：把这个 URL 返回给前端
            },
            data_fileds=ai_preview_fields()
        )