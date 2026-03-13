from flask_restful import Resource
from app.api.common.response import success
from app.api.common.parser import species_search_parser
from app.api.common.fields import get_species_list_fields
from app.models.species import Species

class GetSpeciesList(Resource):
    
    def get(self):
        """获取物种列表接口"""
        args = species_search_parser()
        
        page = args.get('page')
        per_page = args.get('per_page')

        items, total = Species.get_species_list(
            page=page,
            per_page=per_page,
            keyword=args.get('keyword'),
            species=args.get('species'),
            order_name=args.get('order_name'),
            family=args.get('family')
        )

        data = {
            'species_list': items,
            'pagination': {
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
        }
        
        return success(
            msg='获取成功', 
            data=data, 
            data_fileds=get_species_list_fields()
        )