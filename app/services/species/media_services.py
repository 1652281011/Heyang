import os
import time
import uuid
from app.models import db
from flask import current_app, request
from sqlalchemy import text

from app.models.species_media import SpeciesMedia


class MediaService:

    @staticmethod
    def add_media(data, file_obj, thumb_obj=None):
        """【增】上传资源：支持 UUID 绑定和可选缩略图"""
        sid = data.get('species_id')
        m_type = data.get('media_type') or 'image'
        shared_uuid = uuid.uuid4().hex

        # 1. 物理保存路径设置 (static/uploads/species/ID/type/)
        rel_dir = f"uploads/species/{sid}/{m_type}"
        abs_dir = os.path.join(current_app.root_path, 'static', rel_dir)
        os.makedirs(abs_dir, exist_ok=True)

        # 2. 保存主文件
        f_ext = os.path.splitext(file_obj.filename)[1]
        f_name = f"{shared_uuid}{f_ext}"
        file_obj.save(os.path.join(abs_dir, f_name))
        file_url = f"{rel_dir}/{f_name}"

        # 3. 保存缩略图 (只有传了才保存)
        thumb_url = ""
        if thumb_obj:
            t_ext = os.path.splitext(thumb_obj.filename)[1]
            t_name = f"{shared_uuid}_thumb{t_ext}"
            thumb_obj.save(os.path.join(abs_dir, t_name))
            thumb_url = f"{rel_dir}/{t_name}"

        # 4. 封面互斥逻辑
        if str(data.get('is_cover')) == '1':
            db.session.execute(text("UPDATE species_media SET is_cover=0 WHERE species_id=:sid"), {"sid": sid})

        # 5. 写入数据库
        now = int(time.time())
        try:
            new_media = SpeciesMedia(
                species_id=sid,
                media_type=m_type,
                file_url=file_url,
                thumbnail_url=thumb_url,
                title=data.get('title') or file_obj.filename,
                media_category=data.get('media_category', '普通'),
                morphology_type=data.get('morphology_type'),
                model_category=data.get('model_category'),
                is_cover=data.get('is_cover', 0),
                c_time=now, e_time=now
            )
            db.session.add(new_media)
            db.session.commit()
            return True, "资源上传成功"
        except Exception as e:
            db.session.rollback()
            return False, f"数据库写入失败: {str(e)}"

    @staticmethod
    def update_media(media_id, update_data):
        """【改】仅修改元数据(标题、分类、排序)"""
        item = db.session.query(SpeciesMedia).get(media_id)
        if not item: return False, "未找到该资源"

        if str(update_data.get('is_cover')) == '1':
            db.session.execute(text("UPDATE species_media SET is_cover=0 WHERE species_id=:sid"), {"sid": item.species_id})

        # 允许修改的字段映射
        fields = ['title', 'media_category', 'morphology_type', 'model_category', 'is_cover', 'sort_order']
        for f in fields:
            if update_data.get(f) is not None:
                setattr(item, f, update_data[f])
        
        item.e_time = int(time.time())
        db.session.commit()
        return True, "修改成功"

    @staticmethod
    def delete_media(media_id):
        """【删】物理删除文件并清理数据库"""
        item = db.session.query(SpeciesMedia).get(media_id)
        if not item: return False, "资源已不存在"

        try:
            # 删除物理磁盘文件
            for path in [item.file_url, item.thumbnail_url]:
                if path:
                    abs_p = os.path.join(current_app.root_path, 'static', path)
                    if os.path.exists(abs_p):
                        os.remove(abs_p)
            
            db.session.delete(item)
            db.session.commit()
            return True, "物理文件及记录已成功删除"
        except Exception as e:
            db.session.rollback()
            return False, f"删除失败: {str(e)}"