# app/models/species.py
import base64
import random
from time import time
from flask import current_app, g
from itsdangerous import URLSafeTimedSerializer as Serializer, SignatureExpired, BadSignature
from app.models import db
from app.api.common.fields import get_species_list_fields
from app.utils.common import md5_str, time_to_str

class Species(db.Model):
    __tablename__ = 'species_info'
    __table_args__ = {'comment': '物种基本信息表'}

    species_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, comment='物种ID')
    chinese_name = db.Column(db.String(100, collation='utf8mb4_unicode_ci'), nullable=True, unique=True, comment='物种中文名')
    english_name = db.Column(db.String(100, collation='utf8mb4_unicode_ci'), nullable=True, comment='物种英文名')
    species = db.Column(db.String(300, collation='utf8mb4_unicode_ci'), nullable=False, comment='种')
    order_name = db.Column(db.String(50, collation='utf8mb4_unicode_ci'), nullable=False, comment='目')
    family = db.Column(db.String(50, collation='utf8mb4_unicode_ci'), nullable=False, comment='科')
    collection_province = db.Column(db.String(100, collation='utf8mb4_unicode_ci'), nullable=True, comment='模式标本采集地点中文名')
    scientific_name = db.Column(db.String(100, collation='utf8mb4_unicode_ci'), nullable=True, unique=True, comment='物种学名')
    grade = db.Column(db.String(100, collation='utf8mb4_unicode_ci'), nullable=True, comment='保护级别')
    description = db.Column(db.String(500, collation='utf8mb4_unicode_ci'), nullable=True, comment='物种描述')
    distribution = db.Column(db.String(500, collation='utf8mb4_unicode_ci'), nullable=True, comment='地理分布')
    epidemic = db.Column(db.String(50, collation='utf8mb4_unicode_ci'), nullable=True, comment='疫源记录')
    sequense = db.Column(db.String(100, collation='utf8mb4_unicode_ci'), nullable=True, comment='分子靶标序列')

    @staticmethod
    def get_species_list(page=1, per_page=20, keyword=None, species=None, order_name=None, family=None):
        """
        获取物种列表，支持多条件筛选
        """
        query = Species.query

        # 1. 关键词通用搜索 (如果传了 keyword)
        if keyword:
            query = query.filter(
                db.or_(
                    Species.chinese_name.like(f'%{keyword}%'),
                    Species.english_name.like(f'%{keyword}%'),
                    Species.scientific_name.like(f'%{keyword}%')
                )
            )

        # 2. 针对“种”的筛选
        if species:
            query = query.filter(Species.species.like(f'%{species}%'))

        # 3. 针对“目”的筛选
        if order_name:
            query = query.filter(Species.order_name.like(f'%{order_name}%'))

        # 4. 针对“科”的筛选
        if family:
            query = query.filter(Species.family.like(f'%{family}%'))

        # 排序：默认按物种ID排序
        query = query.order_by(Species.species_id.asc())

        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return pagination.items, pagination.total

    # === 序列化方法 ===
    def to_dict(self):
        """返回该物种的所有信息"""
        res = {
            "species_id": self.species_id,
            "chinese_name": self.chinese_name,
            "english_name": self.english_name,
            "species": self.species,
            "order_name": self.order_name,
            "family": self.family,
            "collection_province": self.collection_province,
            "scientific_name": self.scientific_name,
            "grade": self.grade,
            "description": self.description,
            "distribution": self.distribution,
            "epidemic": self.epidemic,
            "sequense": self.sequense
        }
        return res