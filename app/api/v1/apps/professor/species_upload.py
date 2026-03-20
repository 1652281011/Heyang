from flask import g
from flask_restful import Resource
from app.api.common.response import success, error
from app.api.common.parser import species_upload_parser
from app.utils.decorators import professor_required
from app.models.species_audit import SpeciesAudit
from app.models.species import Species

class SpeciesUploadResource(Resource):
    
    method_decorators = [professor_required]  # 仅教授可用
    
    def post(self):
        """
        教授提交物种数据
        逻辑：如果是 update，必须通过 scientific_name 找到原物种
        """
        args = species_upload_parser()
        op_type = args['operate_type']
        scientific_name = args['scientific_name'] 
        
        target_species_id = None

        if op_type == 'update':
            # 1. 根据学名查找是否存在
            target_species = Species.query.filter_by(scientific_name=scientific_name).first()
            
            if not target_species:
                return error(msg=f'未找到学名为 [{scientific_name}] 的物种，无法修改。请检查拼写或选择“新增”。')
            
            # 2. 记录目标ID，方便管理员审核时直接定位
            target_species_id = target_species.species_id


        elif op_type == 'add':
            # 1. 检查学名是否已存在，防止重复添加
            exists = Species.query.filter_by(scientific_name=scientific_name).first()
            if exists:
                return error(msg=f'学名为 [{scientific_name}] 的物种已存在，请勿重复添加。')

            target_species_id = None

        data_snapshot = {
            "species_id": target_species_id if target_species_id else None,
            "scientific_name": scientific_name,
            "chinese_name": args['chinese_name'],
            "english_name": args['english_name'],
            "species": args['species'],
            "order_name": args['order_name'],
            "family": args['family'],
            "description": args['description']
        }

        try:
            audit = SpeciesAudit.create_audit(
                applicant_id=g.user.professor_id,
                operate_type=op_type,
                target_id=target_species_id,
                data_dict=data_snapshot
            )
            return success(msg='提交成功，数据已进入审核队列')
            
        except Exception as e:
            return error(msg='提交失败: ' + str(e))