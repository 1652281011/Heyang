from flask_restful import Resource
from app.api.common.response import success
from app.api.common.parser import post_list_parser
from app.services.community.post_service import PostService

class PostListResource(Resource):
    def get(self):
        args = post_list_parser()
        data = PostService.get_list(
            keyword=args['keyword'],
            page=args['page'],
            per_page=args['per_page']
        )
        return success(data=data)