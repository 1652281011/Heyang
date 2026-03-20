# -*- coding: utf-8 -*-
from flask import g, request
from flask_restful import Resource
from app.api.common import error_code
from app.api.common.response import success, error
from app.api.common.parser import post_detail_parser
from app.api.common.fields import post_detail_fields
from app.models.community import Post, Like
from app.models import db

class PostDetailResource(Resource):
    def get(self):
        """
        获取帖子详情接口
        """
        # 1. 参数解析
        args = post_detail_parser()
        post_id = args.get('post_id')
        
        # 2. 查询帖子并验证状态
        post = Post.query.filter_by(id=post_id, status=1).first()
        if not post:
            return error(error_code.POST_NOT_EXISTS, msg=u"帖子内容不存在或已删除")

        # 3. 业务逻辑：增加阅读量
        try:
            post.view_count += 1
            db.session.commit()
        except Exception:
            db.session.rollback() # 仅增加阅读量失败不影响主流程显示

        # 4. 判断当前登录用户是否已点赞 (社交回显)
        # 即使未登录也允许查看详情，只需判断 g.user 是否存在
        post.is_liked = False
        if g.user:
            exist_like = Like.query.filter_by(post_id=post.id, user_id=g.user.id).first()
            post.is_liked = True if exist_like else False

        # 5. 准备返回。由于使用了 marshal 且 fields 中定义了嵌套属性，
        # 我们可以直接传 post 对象，marshal 会自动提取关联的 images 和 comments。
        return success(
            msg=u"请求成功",
            data=post, 
            data_fileds=post_detail_fields()
        )