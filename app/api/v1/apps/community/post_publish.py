from flask_restful import Resource
from app.api.common.response import success, error
from app.api.common.parser import post_publish_parser
from app.services.community.post_service import PostService
from app.utils.decorators import login_required

class PostPublishResource(Resource):
    #method_decorators = [login_required]
    def post(self):
        args = post_publish_parser()
        ok, res = PostService.create_post(args)
        return success(data={"id": res}) if ok else error(msg=res)