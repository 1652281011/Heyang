# -*- coding: utf-8 -*-
import time

from flask import request
from .base import db, BaseModel

class SpeciesPost(db.Model, BaseModel):
    """物种鉴定帖子模型"""
    __tablename__ = 'species_posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # 地理位置
    location_lat = db.Column(db.Float)
    location_lng = db.Column(db.Float)
    location_address = db.Column(db.String(255))
    
    # 统计与状态
    participant_count = db.Column(db.Integer, default=1) # 默认发帖人算1个
    status = db.Column(db.Integer, default=0) # 0:待鉴定, 1:已确认
    
    # 结果确认
    final_species_id = db.Column(db.Integer)
    final_species_name = db.Column(db.String(100))
    confirmed_by = db.Column(db.Integer, db.ForeignKey('user_info.id'))
    expert_opinion = db.Column(db.Text, comment='专家参考意见')

    # 关联
    author = db.relationship('User', foreign_keys=[user_id])
    candidates = db.relationship('SpeciesCandidate', backref='post_ref', 
                                 cascade="all, delete-orphan", passive_deletes=True)
    expert = db.relationship('User', foreign_keys=[confirmed_by], backref='confirmed_species_posts')


    @property
    def format_time(self):
        # 确保 c_time 是整数时间戳
        if self.c_time:
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.c_time))
        return None # 如果数据库 c_time 是空的，就会返回 null
    @property
    def format_e_time(self):
        """格式化最后修改/确认时间"""
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.e_time)) if self.e_time else ""

    @property
    def expert_professional_data(self):
        # 只有 status=1 且关联到了专家，且专家有认证信息时才返回
        if self.status == 1 and self.expert:
            pro = self.expert.pro_info # 注意：User模型里定义的字段是 pro_info
            if pro:
                return {
                    "real_name": pro.real_name,
                    "pro_title": pro.pro_title,
                    "organization": pro.organization,
                    "expertise_field": pro.expertise_field
                }
        return None
    @property
    def full_image_url(self):
        """
        将相对路径拼接为完整的 URL
        例如: /static/uploads/xxx.webp -> http://127.0.0.1:39012/static/uploads/xxx.webp
        """
        if not self.image_url:
            return ""

        if self.image_url.startswith('http'):
            return self.image_url

        base_url = request.host_url.rstrip('/') 
        
        # 确保拼接时路径开头有 /
        path = self.image_url if self.image_url.startswith('/') else '/' + self.image_url
        
        return base_url + path

    @property
    def upload_time_str(self):
        """格式化上传时间"""
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.c_time)) if self.c_time else ""
    
    def get_user_vote_id(self, user_id):
        """获取某用户在该贴投过的标签ID"""
        if not user_id: return 0
        vote = SpeciesVote.query.filter_by(user_id=user_id, post_id=self.id).first()
        return vote.candidate_id if vote else 0

    @classmethod
    def get_ident_list(cls, page=1, per_page=10, status=None):
        query = cls.query
        if status is not None:
            query = query.filter_by(status=status)
        pagination = query.order_by(cls.c_time.desc()).paginate(page=page, per_page=per_page)
        return pagination.items, pagination.total

class SpeciesCandidate(db.Model, BaseModel):
    """物种标签建议"""
    __tablename__ = 'species_candidates'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('species_posts.id'), nullable=False)
    species_name = db.Column(db.String(100), nullable=False)
    confidence = db.Column(db.Float, default=0.0)
    vote_count = db.Column(db.Integer, default=0)

class SpeciesVote(db.Model, BaseModel):
    """投票防重表"""
    __tablename__ = 'species_votes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('species_posts.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('species_candidates.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='_user_post_vote_uc'),)