import base64
from flask import current_app
import requests


class BaiduSpeciesAI:
    """封装百度物种识别逻辑"""

    def _get_access_token(self):
        """获取百度授权Token"""
        api_key = current_app.config.get("BAIDU_AI_API_KEY")
        secret_key = current_app.config.get("BAIDU_AI_SECRET_KEY")
        
        url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}"
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                return res.json().get("access_token")
        except Exception as e:
            current_app.logger.error(f"Token获取失败: {e}")
        return None

    def predict(self, image_file):
        token = self._get_access_token()
        if not token: 
            return {"error": "Token获取失败"}

        image_file.seek(0)
        img_data = image_file.read()
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        
        api_url = f"https://aip.baidubce.com/rest/2.0/image-classify/v1/animal?access_token={token}"
        params = {"image": img_base64}
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        
        try:
            res = requests.post(api_url, data=params, headers=headers, timeout=10)
            data = res.json()
            
            # 如果百度返回了错误码，直接把错误信息抛出
            if "error_code" in data:
                return {"error": f"百度API报错({data['error_code']}): {data['error_msg']}"}

            raw_results = data.get("result", [])
            suggestions = []
            for item in raw_results[:5]:
                # 兼容性处理：优先取 keyword，取不到则取 name
                species_name = item.get("keyword") or item.get("name")
                
                # 兼容性处理：百度分值字段可能是 score 或 probability
                conf = item.get("score") or item.get("probability") or 0
                
                suggestions.append({
                    "name": species_name,     # 确保这里的 Key 叫 name，对应 fields.py
                    "confidence": float(conf)
                })
            return suggestions
        except Exception as e:
            return {"error": str(e)}
        
ai_engine = BaiduSpeciesAI()