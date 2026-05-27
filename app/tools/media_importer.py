import os
import sys
import shutil
import time
from unittest.mock import MagicMock

# ==========================================
# 1. 彻底解决环境依赖问题 (屏蔽缺失的 Flask 插件)
# ==========================================
# 只要运行报 No module named 'xxx'，就往这个列表里加
ignored_modules = [
    "flask_socketio", 
    "flask_mail", 
    "flask_login", 
    "flask_migrate", 
    "flask_wtf", 
    "flask_cors"
]
for mod in ignored_modules:
    sys.modules[mod] = MagicMock()

# ==========================================
# 2. 自动处理项目路径
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
# 假设脚本在 app/tools/ 目录下，向上走两级到达项目根目录
project_root = os.path.abspath(os.path.join(current_dir, '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 确保在导入 app 之前已经屏蔽了所有冲突模块
from app import create_app
from app.models import db
from app.models.species import Species
from sqlalchemy import text

app = create_app()

def start_import(raw_data_path):
    with app.app_context():
        if not os.path.exists(raw_data_path):
            print(f"错误：路径不存在: {raw_data_path}")
            return

        folders = [f for f in os.listdir(raw_data_path) if not f.startswith('.')]
        print(f"开始处理，共发现 {len(folders)} 个物种文件夹...")

        for chinese_name in folders:
            species_dir = os.path.join(raw_data_path, chinese_name)
            if not os.path.isdir(species_dir): continue

            # 查询数据库中是否存在该物种
            species = db.session.query(Species).filter(Species.chinese_name == chinese_name).first()
            if not species:
                print(f"[-] 跳过：[{chinese_name}] 数据库无记录。")
                continue
            
            sid = species.species_id
            print(f"\n[+] 正在处理: {chinese_name} (ID: {sid})")

            for m_type in ['image', 'video', 'model']:
                src_path = os.path.join(species_dir, m_type)
                if not os.path.exists(src_path): continue

                # 使用 os.walk 支持无限层级的子文件夹遍历
                for root, dirs, files in os.walk(src_path):
                    for filename in files:
                        fn_lower = filename.lower()
                        # 过滤隐藏文件和封面标识文件（封面图会通过关联逻辑入库）
                        if fn_lower.startswith('.') or "_thumb" in fn_lower or "封面" in fn_lower:
                            continue

                        # 计算相对路径，用于支持子目录结构
                        rel_sub_path = os.path.relpath(root, src_path)
                        url_sub_path = "" if rel_sub_path == "." else f"/{rel_sub_path.replace(os.sep, '/')}"
                        
                        rel_dir = f"uploads/species/{sid}/{m_type}{url_sub_path}"
                        abs_dir = os.path.join(app.root_path, 'static', rel_dir)
                        os.makedirs(abs_dir, exist_ok=True)

                        src_file = os.path.join(root, filename)
                        dest_file = os.path.join(abs_dir, filename)
                        
                        try:
                            shutil.copy(src_file, dest_file)
                        except Exception as e:
                            print(f"    [!] 拷贝失败: {filename}, {e}")
                            continue

                        db_file_url = f"{rel_dir}/{filename}"

                        # 检查重复入库
                        check_sql = text("SELECT media_id FROM species_media WHERE file_url = :url")
                        if db.session.execute(check_sql, {"url": db_file_url}).fetchone():
                            print(f"    [.] 已存在: {filename}")
                            continue

                        # ==========================================
                        # 智能多维度分类逻辑
                        # ==========================================
                        feature_str = (rel_sub_path + "_" + filename).lower()
                        
                        is_cover = 1 if "cover" in fn_lower else 0
                        media_category = "普通"
                        morphology_type = None
                        model_category = None

                        if is_cover == 0:
                            # 规则1：如果是三维模型，【无条件】属于形态学
                            if m_type == "model":
                                media_category = "形态学"
                                morphology_type = "三维模型" 
                                
                                # 细化形态学子类（如有特殊命名）
                                if "标本" in feature_str:
                                    morphology_type = "标本模型"
                                elif "切片" in feature_str:
                                    morphology_type = "切片"
                                    
                                # 识别器官/骨骼/组织
                                if "器官" in feature_str:
                                    model_category = "器官"
                                elif "骨骼" in feature_str:
                                    model_category = "骨骼"
                                elif "组织" in feature_str:
                                    model_category = "组织"
                                    
                            # 规则2：如果是图片或视频，通过关键词判断
                            else:
                                if any(k in feature_str for k in ["形态学", "标本", "切片", "三维模型"]):
                                    media_category = "形态学"
                                    if "标本" in feature_str:
                                        morphology_type = "标本模型"
                                    elif "切片" in feature_str:
                                        morphology_type = "切片"
                                    elif "三维模型" in feature_str:
                                        morphology_type = "三维模型"
                        else:
                            # 明确标记为封面大图
                            media_category = "封面" 

                        # ==========================================
                        # 自动关联缩略图/封面逻辑 (仅限视频和模型)
                        # ==========================================
                        thumb_url = ""
                        if m_type in ['video', 'model']:
                            base_name = os.path.splitext(filename)[0]
                            found_thumb = None
                            img_exts = ['.jpg', '.png', '.jpeg', '.JPG', '.PNG']
                            
                            for f in os.listdir(root):
                                f_lower = f.lower()
                                if not any(f_lower.endswith(ext) for ext in img_exts):
                                    continue
                                if base_name in f and ("thumb" in f_lower or "封面" in f_lower):
                                    found_thumb = f
                                    break
                            
                            if found_thumb:
                                try:
                                    shutil.copy(os.path.join(root, found_thumb), os.path.join(abs_dir, found_thumb))
                                    thumb_url = f"{rel_dir}/{found_thumb}"
                                    print(f"    [√] 关联封面图: {found_thumb}")
                                except:
                                    pass

                        # ==========================================
                        # 原生 SQL 执行入库
                        # ==========================================
                        insert_sql = text("""
                            INSERT INTO species_media 
                            (species_id, media_type, file_url, thumbnail_url, is_cover, title, 
                             media_category, morphology_type, model_category, c_time, e_time) 
                            VALUES 
                            (:sid, :m_type, :url, :thumb, :cover, :title, 
                             :media_cat, :morph_type, :model_cat, :now, :now)
                        """)
                        
                        now_ts = int(time.time())
                        db.session.execute(insert_sql, {
                            "sid": sid, "m_type": m_type, "url": db_file_url,
                            "thumb": thumb_url,
                            "cover": is_cover,
                            "title": f"{chinese_name}的{m_type}资源",
                            "media_cat": media_category,
                            "morph_type": morphology_type,
                            "model_cat": model_category,
                            "now": now_ts
                        })
                        
                        # 实时反馈分类结果
                        cat_path = f"[{media_category}]"
                        if morphology_type: cat_path += f"->[{morphology_type}]"
                        if model_category: cat_path += f"->[{model_category}]"
                        print(f"    -> [入库成功] {cat_path}: {filename}")
        
        db.session.commit()
        print("\n>>> 恭喜！所有媒体资源已处理完毕并同步至数据库。")

if __name__ == '__main__':
    # 请确保此路径正确
    raw_data_path = r'E:\species_try' 
    start_import(raw_data_path)