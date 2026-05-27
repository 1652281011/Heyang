# -*- coding: utf-8 -*-
import os
from flask import g, current_app
from flask_restful import Resource
from app.api.common.response import success, error
from app.api.common.parser import species_post_delete_parser
from app.api.common.fields import op_id_fields
from app.models.identification import SpeciesPost, SpeciesVote, SpeciesCandidate
from app.models.users import User
from app.models.base import db
from app.utils.decorators import login_required

class SpeciesPostDelete(Resource):
    # 必须登录
    method_decorators = [login_required]

    def post(self):
        """
        删除帖子接口
        权限：发帖本人 或 管理员(role_type='3')
        """
        args = species_post_delete_parser()
        post_id = args['post_id']
        user = g.user

        try:
            # 1. 查询帖子
            post = SpeciesPost.query.get(post_id)
            if not post:
                return error(resid=404, msg="帖子不存在或已被删除")

            # 2. 权限校验
            # 只有作者本人 或者 role_type 为 '3' (管理员) 的人才有权删除
            if post.user_id != user.id and str(user.role_type) != '3':
                return error(resid=403, msg="权限不足，无法删除他人帖子")

            # 3. 准备物理图片路径（以便后续从磁盘删除）
            # 假设 image_url 存储的是 /static/uploads/xxx.jpg
            relative_path = post.image_url.lstrip('/')
            absolute_path = os.path.join(current_app.root_path, relative_path)

            # 4. 数据库清理
            # A. 手动清理投票记录（如果没设数据库级联）
            SpeciesVote.query.filter_by(post_id=post.id).delete()
            
            # B. 删除帖子（candidates 会根据模型中的 cascade 自动删除）
            db.session.delete(post)

            # C. 作者发帖数 -1
            author = User.query.get(post.user_id)
            if author and author.post_count > 0:
                author.post_count -= 1

            # 5. 提交事务
            db.session.commit()

            # 6. 删除磁盘上的物理图片文件 (可选，建议执行以节省空间)
            if os.path.exists(absolute_path):
                try:
                    os.remove(absolute_path)
                except Exception as e:
                    current_app.logger.error(f"文件删除失败: {absolute_path}, error: {e}")

            return success(msg="帖子已成功删除", data={'id': post_id}, data_fileds=op_id_fields())

        except Exception as e:
            db.session.rollback()
            return error(msg=f"删除失败: {str(e)}")