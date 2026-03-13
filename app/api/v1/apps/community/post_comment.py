from flask_restful import Resource
from app.api.common.response import success, error
from app.api.common.parser import post_interact_parser
from app.services.community.interact_service import InteractService

class CommentResource(Resource):
    def post(self):
        args = post_interact_parser()
        if not args['content']: return error(msg="内容必填")
        ok, res = InteractService.add_comment(args['post_id'], args['user_id'], args['content'])
        return success(data=res) if ok else error(msg=res)