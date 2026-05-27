from flask_restful import Resource

from app.api.common.parser import species_add_parser
from app.api.common.response import error, success
from app.services.species.species_services import SpeciesService
from app.utils.decorators import admin_required


class SpeciesAddResource(Resource):
    """
    管理员新增物种信息接口
    """
    method_decorators = [admin_required]

    def post(self):
        # 1. 解析 JSON 参数
        args = species_add_parser()
        
        # 2. 调用 Service 执行入库
        res, result = SpeciesService.add_species(args)
        
        if not res:
            # 这里的 result 是错误信息字符串
            return error(resid=100, msg=result)

        # 3. 返回成功及新增的 ID
        return success(
            msg='物种信息录入成功',
            data={'species_id': result}
        )