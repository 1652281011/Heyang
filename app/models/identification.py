# -*- coding: utf-8 -*-
import time
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

    # 关联
    author = db.relationship('User', foreign_keys=[user_id])
    candidates = db.relationship('SpeciesCandidate', backref='post', lazy='dynamic', cascade="all, delete-orphan")

    @property
    def upload_time_str(self):
        """格式化上传时间"""
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.c_time)) if self.c_time else ""

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