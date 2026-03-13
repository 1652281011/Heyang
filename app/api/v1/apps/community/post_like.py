from flask_restful import Resource
from app.api.common.response import success, error
from app.api.common.parser import post_interact_parser
from app.services.community.interact_service import InteractService

class LikeResource(Resource):
    def post(self):
        args = post_interact_parser()
        ok, res = InteractService.toggle_like(args['post_id'], args['user_id'])
        return success(data=res) if ok else error(msg=res)