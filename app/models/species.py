# app/models/species.py
import datetime
import time
from app.models import db
from app.models.base import BaseModel

class Species(db.Model, BaseModel):
    __tablename__ = 'species_info'
    __table_args__ = {'comment': '哺乳动物物种基本信息表'}

    species_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, comment='物种ID')
    
    # 基础分类
    order_name = db.Column(db.String(100, collation='utf8mb4_unicode_ci'), nullable=False, comment='目')
    family_name = db.Column(db.String(100, collation='utf8mb4_unicode_ci'), nullable=False, comment='科')
    species_name = db.Column(db.String(200, collation='utf8mb4_unicode_ci'), nullable=False, comment='物种(学名)')
    chinese_name = db.Column(db.String(100, collation='utf8mb4_unicode_ci'), nullable=True, unique=True, comment='中文名')
    english_name = db.Column(db.String(150, collation='utf8mb4_unicode_ci'), nullable=True, comment='英文名')
    
    # 命名与标本
    nomenclator = db.Column(db.String(200, collation='utf8mb4_unicode_ci'), nullable=True, comment='命名人')
    naming_year = db.Column(db.String(50, collation='utf8mb4_unicode_ci'), nullable=True, comment='命名年代')
    type_specimen_record = db.Column(db.Text(collation='utf8mb4_unicode_ci'), nullable=True, comment='原始描述中记录模式标本')
    type_locality = db.Column(db.Text(collation='utf8mb4_unicode_ci'), nullable=True, comment='模式标本采集地点')
    latitude = db.Column(db.String(50, collation='utf8mb4_unicode_ci'), nullable=True, comment='纬度')
    longitude = db.Column(db.String(50, collation='utf8mb4_unicode_ci'), nullable=True, comment='经度')
    repository = db.Column(db.String(255, collation='utf8mb4_unicode_ci'), nullable=True, comment='模式标本保存地')
    repository_country = db.Column(db.String(100, collation='utf8mb4_unicode_ci'), nullable=True, comment='模式标本保存国家')
    
    # 特征与分布
    synonyms = db.Column(db.Text(collation='utf8mb4_unicode_ci'), nullable=True, comment='同物异名')
    subspecies = db.Column(db.Text(collation='utf8mb4_unicode_ci'), nullable=True, comment='亚种分化')
    domestic_distribution = db.Column(db.Text(collation='utf8mb4_unicode_ci'), nullable=True, comment='国内分布')
    foreign_distribution = db.Column(db.Text(collation='utf8mb4_unicode_ci'), nullable=True, comment='国外分布')
    references = db.Column(db.Text(collation='utf8mb4_unicode_ci'), nullable=True, comment='引证文献')
    diagnostic_features = db.Column(db.Text(collation='utf8mb4_unicode_ci'), nullable=True, comment='鉴别特征')

    c_time = db.Column(db.Integer, default=lambda: int(time.time()), comment='创建时间')
    e_time = db.Column(db.Integer, default=lambda: int(time.time()), onupdate=lambda: int(time.time()), comment='更新时间')

    @property
    def c_time_format(self):
        # 这里的 self.c_time 继承自 BaseModel
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.c_time)) if self.c_time else ""

    @property
    def e_time_format(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.e_time)) if self.e_time else ""

    def to_dict(self):
        """
        将模型对象转换为字典
        """
        # 1. 动态获取所有数据库列的值
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        
        # 2. 用格式化后的字符串覆盖原本的整数时间戳
        # 这样返回给前端的 c_time 就是 "2026-04-22 00:16:54"
        data['c_time'] = self.c_time_format
        data['e_time'] = self.e_time_format
        
        return data