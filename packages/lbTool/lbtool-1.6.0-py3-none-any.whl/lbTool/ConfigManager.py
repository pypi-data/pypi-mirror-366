import os
from warnings import deprecated

import yaml

@deprecated("使用Config类代替")
class ConfigManager:
    """
    配置管理类
    """
    # yaml_file = os.path.normpath(os.path.join(os.getcwd(), "config/config.yml"))

    @staticmethod
    def getvalue(config_name, default_value=""):
        """
        获取配置值
        :param config_name: 配置名称
        :param default_value: 默认值
        :return:
        """
        # 获取配置文件地址
        from lbTool.Config import get_app_base_path
        config_dir_path = get_app_base_path(os.getcwd())
        yaml_file = os.path.normpath(os.path.join(config_dir_path, "config", "config.yml"))
        try:
            with open(yaml_file, 'r', encoding='utf-8') as file:
                config_data = yaml.load(file.read(), Loader=yaml.FullLoader)

                # 将配置名称按点拆分成多个部分
                keys = config_name.split('.')

                # 逐级访问嵌套的键
                value = config_data
                for key in keys:
                    value = value.get(key, None)
                    if value is None:
                        break

                return value if value is not None else default_value
        except (FileNotFoundError, KeyError):
            return default_value
