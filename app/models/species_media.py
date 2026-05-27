from app.models import db
from app.models.base import BaseModel

class SpeciesMedia(db.Model, BaseModel):
    __tablename__ = 'species_media'
    __table_args__ = {'comment': '物种多媒体资源表'}

    media_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species_info.species_id'), nullable=False)
    media_type = db.Column(db.String(20), nullable=False)
    file_url = db.Column(db.String(255), nullable=False)
    thumbnail_url = db.Column(db.String(255), default='')
    is_cover = db.Column(db.Integer, default=0)
    title = db.Column(db.String(128), default='')
    media_category = db.Column(db.String(50), default='普通')
    morphology_type = db.Column(db.String(50))
    model_category = db.Column(db.String(50))
    