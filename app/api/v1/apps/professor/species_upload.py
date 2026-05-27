# app/api/v1/apps/expert/species_upload.py
from flask import g
from flask_restful import Resource
from app.api.common.response import success, error
from app.api.common.parser import species_upload_parser # 请确保 parser 包含下方所有 Key
from app.utils.decorators import expert_required
from app.models.species_audit import SpeciesAudit
from app.models.species import Species

class SpeciesUploadResource(Resource):
    method_decorators = [expert_required]

    def post(self):
        """专家提交物种数据申请"""
        args = species_upload_parser()
        op_type = args['operate_type']
        s_name = args['species_name']  # 学名
        c_name = args['chinese_name']  # 中文名
        
        target_id = None

        if op_type == 'update':
            # 优先按学名找，找不到按中文名找
            target = Species.query.filter((Species.species_name == s_name) | (Species.chinese_name == c_name)).first()
            if not target:
                return error(msg=f'未找到物种[{c_name}]，请检查名称或选择“新增”模式')
            target_id = target.species_id

        elif op_type == 'add':
            # 检查是否已存在
            if Species.query.filter((Species.species_name == s_name) | (Species.chinese_name == c_name)).first():
                return error(msg='该物种已存在于正式库中，请勿重复添加')

        # 构建完整的 20 个业务字段快照
        data_snapshot = {
            "order_name": args.get('order_name'),
            "family_name": args.get('family_name'),
            "species_name": s_name,
            "chinese_name": c_name,
            "english_name": args.get('english_name'),
            "nomenclator": args.get('nomenclator'),
            "naming_year": args.get('naming_year'),
            "type_specimen_record": args.get('type_specimen_record'),
            "type_locality": args.get('type_locality'),
            "latitude": args.get('latitude'),
            "longitude": args.get('longitude'),
            "repository": args.get('repository'),
            "repository_country": args.get('repository_country'),
            "synonyms": args.get('synonyms'),
            "subspecies": args.get('subspecies'),
            "domestic_distribution": args.get('domestic_distribution'),
            "foreign_distribution": args.get('foreign_distribution'),
            "references": args.get('references'),
            "diagnostic_features": args.get('diagnostic_features')
        }

        try:
            # 这里的 g.user.id 对应你的申请人 ID
            SpeciesAudit.create_audit(
                applicant_id=g.user.id, 
                operate_type=op_type,
                target_id=target_id,
                data_dict=data_snapshot
            )
            return success(msg='申请已提交，请等待管理员审核')
        except Exception as e:
            return error(msg=f'提交失败: {str(e)}')