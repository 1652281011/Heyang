from flask_restful import Resource

from app.api.common.fields import get_species_detail_fields
from app.api.common.parser import species_edit_parser
from app.api.common.response import error, success
from app.services.species.species_services import SpeciesService
from app.utils.decorators import admin_required


class SpeciesEditResource(Resource):
    """
    管理员编辑物种文字信息
    """
    # 权限：只有一般管理员(8)和高级管理员(9)可以操作
    method_decorators = [admin_required]

    def put(self):
        # 1. 解析前端传来的修改内容
        args = species_edit_parser()
        sid = args.get('species_id')

        # 2. 调用服务层执行更新
        res, msg = SpeciesService.edit_species(sid, args)

        if not res:
            return error(resid=100, msg=msg)

        # 3. 更新成功后，查询最新数据并返回 (用于前端刷新显示)
        # 这里的 is_expert=True 确保管理员能看到形态学等所有模块
        new_info = SpeciesService.get_species_detail(sid, is_expert=True)

        return success(
            msg=u'物种资料修改成功',
            data=new_info,
            data_fileds=get_species_detail_fields()
        )