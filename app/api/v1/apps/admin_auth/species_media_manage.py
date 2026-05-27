from flask import request
from flask_restful import Resource

from app.api.common.parser import media_manage_parser
from app.api.common.response import error, success
from app.services.species.media_services import MediaService
from app.utils.decorators import admin_required


class MediaManageApi(Resource):
    # 强制管理员权限
    method_decorators = [admin_required]

    def post(self):
        """
        【增】上传新媒体文件
        Postman 使用 Body -> form-data
        """
        # 1. 使用解析器获取所有参数（含文件）
        args = media_manage_parser().parse_args()
        
        file = args.get('file')
        if not file:
            return error(resid=400, msg='请上传主文件(file)')

        # 2. 调用服务执行物理保存和入库
        res, msg = MediaService.add_media(
            data=args, 
            file_obj=file, 
            thumb_obj=args.get('thumbnail_file')
        )
        
        if not res:
            return error(resid=100, msg=msg)
            
        return success(msg=msg)

    def put(self):
        """
        【改】修改媒体属性 (分类、标题等)
        Postman 使用 Body -> raw -> JSON
        """
        args = media_manage_parser().parse_args()
        mid = args.get('media_id')
        
        if not mid:
            return error(resid=400, msg='缺少参数 media_id')

        res, msg = MediaService.update_media(mid, args)
        
        if not res:
            return error(resid=100, msg=msg)
            
        return success(msg=msg)

    def delete(self):
        """
        【删】永久删除媒体
        URL 示例: /v1/admin/species/media?media_id=10
        """
        # DELETE 通常从 URL 参数拿 ID
        mid = request.args.get('media_id', type=int)
        
        if not mid:
            return error(resid=400, msg='缺少参数 media_id')

        res, msg = MediaService.delete_media(mid)
        
        if not res:
            return error(resid=100, msg=msg)
            
        return success(msg=msg)