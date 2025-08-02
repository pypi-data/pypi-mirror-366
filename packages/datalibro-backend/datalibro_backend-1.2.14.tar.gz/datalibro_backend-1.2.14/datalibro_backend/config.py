import os
import json

class FeishuConfig:
    """Feishu API配置管理类"""
    
    def __init__(self):
        self._app_id = None
        self._app_secret = None
        self._load_config()
    
    def _load_config(self):
        """加载配置，优先级：环境变量 > 配置文件 > 默认值"""
        # 首先尝试从环境变量读取
        self._app_id = os.getenv('FEISHU_APP_ID')
        self._app_secret = os.getenv('FEISHU_APP_SECRET')
        
        # 如果环境变量没有设置，尝试从配置文件读取
        if not self._app_id or not self._app_secret:
            config_file = os.path.join(os.path.dirname(__file__), 'feishu_config.json')
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        self._app_id = config.get('app_id')
                        self._app_secret = config.get('app_secret')
                except Exception as e:
                    print(f"读取配置文件失败: {e}")
        
        # 如果都没有设置，使用默认值（为了向后兼容）
        if not self._app_id:
            self._app_id = 'fake_app_id'
        if not self._app_secret:
            self._app_secret = 'fake_app_secret'
    
    @property
    def app_id(self):
        """获取app_id"""
        return self._app_id
    
    @property
    def app_secret(self):
        """获取app_secret"""
        return self._app_secret
    
    def get_auth_payload(self):
        """获取认证payload"""
        return {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

# 创建全局配置实例
feishu_config = FeishuConfig() 