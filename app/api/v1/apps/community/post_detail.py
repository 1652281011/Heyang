from flask_restful import Resource
from app.api.common.response import success, error
from app.api.common.parser import post_detail_parser # 引入新解析器
from app.models.community import Post
from app.models import db

class PostDetailResource(Resource):
    def get(self):
        # 1. 从查询参数中获取 post_id
        args = post_detail_parser()
        post_id = args['post_id']
        
        # 2. 数据库查询
        post = Post.query.filter_by(id=post_id, status=1).first()
        if not post:
            return error(msg="帖子内容不存在或已删除")
            
        # 3. 业务逻辑（增加阅读量）
        post.view_count += 1
        db.session.commit()
        
        # 4. 组装返回
        data = post.to_full_dict()
        data['comments'] = [c.to_dict() for c in post.comments.all()]
        return success(data=data)