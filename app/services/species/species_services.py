# app/services/species/species_services.py
from sqlite3 import IntegrityError
import time
from flask import request
from app.models import db
import pandas as pd
from app.models.species import Species
from sqlalchemy import or_, text

# 默认封面图路径
DEFAULT_IMAGE_REL_PATH = "defaults/default_cover.jpg"

class SpeciesService:

    @staticmethod
    def format_dynamic_url(rel_path):
        """
        静态方法：动态获取当前请求的域名/IP并拼接路径
        解决了 FILE_BASE_URL 频繁变更的问题
        """
        if not rel_path:
            return ""
        
        # 移除路径中可能重复的 'static/' 前缀或开头的斜杠
        clean_path = rel_path.replace('static/', '').lstrip('/')
        
        # request.host_url 会自动获取当前请求的协议+IP+端口 
        # 例如 http://10.21.175.212:39012/ 或 http://127.0.0.1:5000/
        return f"{request.host_url}static/{clean_path}"

    @staticmethod
    def get_species_list(page=1, per_page=20, filters=None):
        """
        获取物种列表，并注入动态 URL 的封面图
        """
        query = db.session.query(Species)
        if not filters: filters = {}

        # 搜索过滤逻辑 (keyword, order_name 等)
        keyword = filters.get('keyword')
        if keyword:
            query = query.filter(or_(
                Species.chinese_name.like(f'%{keyword}%'),
                Species.english_name.like(f'%{keyword}%'),
                Species.species_name.like(f'%{keyword}%')
            ))
        if filters.get('order_name'):
            query = query.filter(Species.order_name == filters.get('order_name'))
        if filters.get('family_name'):
            query = query.filter(Species.family_name == filters.get('family_name'))
        if filters.get('chinese_name'):
            query = query.filter(Species.chinese_name.like(f'%{filters.get("chinese_name")}%'))

        pagination = query.order_by(Species.species_id.asc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        items_with_cover = []
        for item in pagination.items:
            data = item.to_dict()
            
            # 使用原生 SQL 查封面路径
            sql = text("""
                SELECT file_url FROM species_media 
                WHERE species_id = :sid AND media_type = 'image' 
                ORDER BY is_cover DESC, sort_order ASC 
                LIMIT 1
            """)
            result = db.session.execute(sql, {"sid": item.species_id}).fetchone()
            
            # --- 调用类内部的静态方法 ---
            rel_path = result[0] if result else DEFAULT_IMAGE_REL_PATH
            data['cover_image'] = SpeciesService.format_dynamic_url(rel_path)
            
            items_with_cover.append(data)

        return {
            "total": pagination.total,
            "items": items_with_cover,
            "pages": pagination.pages,
            "current_page": page
        }

    @staticmethod
    def get_species_detail(species_id, is_expert=False):
        """
        获取物种详细信息，适配最新的分类体系：
        1. 普通媒体：图片、视频
        2. 形态学信息（专家可见）：标本照片、切片、三维模型（器官/骨骼/组织）
        """
        species = db.session.query(Species).get(species_id)
        if not species: 
            return None

        # 1. 更新 SQL 查询，匹配最新的表字段名
        media_sql = text("""
            SELECT 
                media_id, media_type, file_url, thumbnail_url, title, 
                media_category, morphology_type, model_category 
            FROM species_media 
            WHERE species_id = :sid 
            ORDER BY c_time ASC
        """)
        rows = db.session.execute(media_sql, {"sid": species_id}).fetchall()
        
        # 2. 初始化分类容器
        # 普通用户可见
        normal_media = {"images": [], "videos": []}
        
        # 仅专家可见的形态学模块
        morphology_info = {
            "specimen_photos": [], # 对应 morphology_type='标本模型'
            "sections": [],        # 对应 morphology_type='切片'
            "models_3d": {         # 对应 morphology_type='三维模型'
                "organ": [],       # 对应 model_category='器官'
                "skeleton": [],    # 对应 model_category='骨骼'
                "tissue": []       # 对应 model_category='组织'
            }
        }

        for row in rows:
            # 数据解构：注意顺序必须与 SQL SELECT 一致
            m_id, m_type, f_url, t_url, title, m_cat, morph_type, model_cat = row
            
            m_data = {
                "media_id": m_id,
                "file_url": SpeciesService.format_dynamic_url(f_url),
                "thumbnail_url": SpeciesService.format_dynamic_url(t_url) if t_url else "",
                "title": title
            }

            # --- 3. 核心分流逻辑 ---
            
            # A. 普通媒体 (普通 或 封面 类型)
            if m_cat == '普通' or m_cat == '封面':
                if m_type == 'image': 
                    normal_media['images'].append(m_data)
                elif m_type == 'video': 
                    normal_media['videos'].append(m_data)
            
            # B. 形态学信息 (仅限专家且分类为形态学)
            elif m_cat == '形态学' and is_expert:
                if morph_type == '标本模型':
                    morphology_info['specimen_photos'].append(m_data)
                elif morph_type == '切片':
                    morphology_info['sections'].append(m_data)
                elif morph_type == '三维模型':
                    # 处理三维模型的细分分类
                    if model_cat == '器官':
                        morphology_info['models_3d']['organ'].append(m_data)
                    elif model_cat == '骨骼':
                        morphology_info['models_3d']['skeleton'].append(m_data)
                    elif model_cat == '组织':
                        morphology_info['models_3d']['tissue'].append(m_data)

        # 4. 组装返回结果
        res = species.to_dict()
        res['normal_media'] = normal_media
        
        # 权限控制：如果不是专家，整个模块返回 None 或空结构
        # 前端可以根据 morphology_info 是否存在来判断是否显示该选项卡
        res['morphology_info'] = morphology_info if is_expert else None
        
        return res
    
    @staticmethod
    def edit_species(species_id, update_data):
        species = db.session.query(Species).get(species_id)
        if not species:
            return False, "物种不存在"

        # --- 增加查重逻辑 ---
        new_chinese_name = update_data.get('chinese_name')
        if new_chinese_name:
            # 检查是否有【其他记录】占用了这个名字
            existing = db.session.query(Species).filter(
                Species.chinese_name == new_chinese_name,
                Species.species_id != species_id  # 排除当前正在编辑的这一行
            ).first()
            if existing:
                return False, f"修改失败：中文名 '{new_chinese_name}' 已被其他记录(ID:{existing.species_id})使用"
        # ------------------

        try:
            for key, value in update_data.items():
                if hasattr(species, key) and key != 'species_id' and value is not None:
                    setattr(species, key, value)
            
            species.e_time = int(time.time())
        
            # 3. 补充：如果 c_time 原本是 NULL (以前导入漏了)，现在顺便补上
            if species.c_time is None:
                species.c_time = species.e_time
            db.session.commit()
            return True, "更新成功"
        except Exception as e:
            db.session.rollback()
            return False, f"系统错误: {str(e)}"
        
    @staticmethod
    def add_species(data):
        """
        【增】新增物种文字信息
        """
        # 1. 唯一性检查：防止中文名重复
        c_name = data.get('chinese_name')
        exist = db.session.query(Species).filter_by(chinese_name=c_name).first()
        if exist:
            return False, f"添加失败：中文名 '{c_name}' 已存在"

        try:
            # 2. 创建模型实例
            now = int(time.time())
            new_species = Species(**data)
            
            # 3. 注入时间戳
            new_species.c_time = now
            new_species.e_time = now
            
            # 4. 执行保存
            db.session.add(new_species)
            db.session.commit()
            
            return True, new_species.species_id
            
        except Exception as e:
            db.session.rollback()
            return False, f"数据库写入失败: {str(e)}"
        
    @staticmethod
    def batch_import(file_obj):
        filename = file_obj.filename
        try:
            # 1. 读取文件
            if filename.endswith('.csv'):
                df = pd.read_csv(file_obj, encoding='utf-8-sig')
            else:
                df = pd.read_excel(file_obj)

            # 2. 数据预处理
            df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
            df = df.where(pd.notnull(df), None) # 将 NaN 转为 None
            
            # 3. 字段映射表 (Excel列名 : 数据库字段名)
            mapping = {
                "目": "order_name", "科": "family_name", "物种(学名)": "species_name",
                "中文名": "chinese_name", "英文名": "english_name", "命名人": "nomenclator",
                "命名年代": "naming_year", "原始描述中记录模式标本": "type_specimen_record",
                "模式标本采集地点": "type_locality", "纬度": "latitude", "经度": "longitude",
                "模式标本保存地": "repository", "模式标本保存国家": "repository_country",
                "同物异名": "synonyms", "亚种分化": "subspecies", "国内分布": "domestic_distribution",
                "国外分布": "foreign_distribution", "引证文献": "references", "鉴别特征": "diagnostic_features"
            }

            now = int(time.time())
            success_count = 0
            error_reports = [] # 用于存放失败的项目及原因

            # 4. 逐行迭代处理
            for index, row in df.iterrows():
                line_num = index + 2 # Excel行号（含表头）
                item_name = row.get('中文名') or row.get('物种(学名)') or "未知项目"

                try:
                    # A. 必填项逻辑校验（解决你之前的 null 报错）
                    required_map = {
                        "order_name": "目",
                        "family_name": "科",
                        "species_name": "物种(学名)",
                        "chinese_name": "中文名"
                    }
                    
                    missing_fields = []
                    species_data = {}
                    for excel_key, db_key in mapping.items():
                        val = row.get(excel_key)
                        species_data[db_key] = val
                        if db_key in required_map and not val:
                            missing_fields.append(excel_key)

                    if missing_fields:
                        error_reports.append({
                            "line": line_num,
                            "item": item_name,
                            "reason": f"缺失必填项: {', '.join(missing_fields)}"
                        })
                        continue

                    # B. 数据库查重 (针对唯一索引 chinese_name)
                    exist = db.session.query(Species).filter_by(chinese_name=species_data['chinese_name']).first()
                    if exist:
                        error_reports.append({
                            "line": line_num,
                            "item": item_name,
                            "reason": f"数据库已存在相同中文名 (ID: {exist.species_id})"
                        })
                        continue

                    # C. 写入数据
                    species_data['c_time'] = now
                    species_data['e_time'] = now
                    new_sp = Species(**species_data)
                    db.session.add(new_sp)
                    
                    # 每一行尝试 commit 一次，确保即使后面行报错，前面的也保存成功
                    # 或者批量 commit（性能更好），这里采用逐行 commit 方便报错定位
                    db.session.commit()
                    success_count += 1

                except IntegrityError as e:
                    db.session.rollback()
                    error_reports.append({
                        "line": line_num,
                        "item": item_name,
                        "reason": "数据库约束冲突（可能是学名重复或数据超长）"
                    })
                except Exception as e:
                    db.session.rollback()
                    error_reports.append({
                        "line": line_num,
                        "item": item_name,
                        "reason": f"程序异常: {str(e)}"
                    })

            return True, {
                "total": len(df),
                "success": success_count,
                "fail": len(error_reports),
                "error_details": error_reports # 返回详细的错误清单
            }

        except Exception as e:
            return False, f"文件读取失败: {str(e)}"