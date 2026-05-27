from flask_restful import Resource
from app.api.common.response import success
from app.api.common.parser import species_search_parser
from app.api.common.fields import get_species_list_fields
from app.models.species import Species
from app.services.species.species_services import SpeciesService

class GetSpeciesList(Resource):
    
    def get(self):
        """获取物种列表接口"""
        args = species_search_parser()
        
        page = args.get('page')
        per_page = args.get('per_page')

        filters = {
            'keyword': args.get('keyword'),
            'order_name': args.get('order_name'),
            'family_name': args.get('family_name')
        }

        # 调用 Service 层获取结果
        result = SpeciesService.get_species_list(
            page=page,
            per_page=per_page,
            filters=filters
        )

        formatted_data = {
            'species_list': result['items'], # 数据库记录列表
            'pagination': {
                'total': result['total'],
                'page': result['current_page'],
                'per_page': per_page,
                'pages': result['pages']
            }
        }
        
        # 将构造好的字典传给 success
        return success(
            msg=u'获取列表成功', 
            data=formatted_data, 
            data_fileds=get_species_list_fields()
        )