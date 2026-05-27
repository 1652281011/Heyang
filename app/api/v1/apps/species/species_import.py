from flask_restful import Resource

from app.api.common.fields import get_import_result_fields
from app.api.common.parser import species_import_parser
from app.api.common.response import error, success
from app.services.species.species_services import SpeciesService
from app.utils.decorators import admin_required


class SpeciesImportResource(Resource):
    """
    物种数据批量上传
    """
    # 仅限管理员操作
    method_decorators = [admin_required]

    def post(self):
        # 1. 解析文件
        args = species_import_parser()
        file_obj = args['file']

        # 2. 执行导入业务
        status, result = SpeciesService.batch_import(file_obj)

        if not status:
            # 文件本身解析失败（如格式不支持）
            return error(resid=100, msg=result)

        # 3. 统计结果并返回
        msg = f"导入完成：成功{result['success']}条"
        if result['fail'] > 0:
            msg += f"，失败{result['fail']}条，请查看详情"

        return success(
            msg=msg,
            data=result,
            data_fileds=get_import_result_fields()
        )