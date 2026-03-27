

from flask_restful import Resource

from app.api.common.response import success
from app.models.identification import SpeciesPost


class SpeciesPostList(Resource):
    def get(self):
        from app.api.common.parser import species_post_search_parser
        from app.api.common.fields import get_ident_list_fields
        
        args = species_post_search_parser()
        query = SpeciesPost.query
        
        # 0: 待鉴定, 1: 已确认
        if args.get('status') is not None:
            query = query.filter_by(status=args['status'])
            
        pagination = query.order_by(SpeciesPost.c_time.desc()).paginate(
            page=args['page'], per_page=args['per_page']
        )
        
        data = {
            'species_list': pagination.items,
            'pagination': {
                'total': pagination.total,
                'page': args['page'],
                'per_page': args['per_page'],
                'pages': pagination.pages
            }
        }
        return success(msg='获取成功', data=data, data_fileds=get_ident_list_fields())