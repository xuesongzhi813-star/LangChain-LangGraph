from pydantic_settings import BaseSettings, SettingsConfigDict

'''
通过Settings对象读取环境变量中的配置信息
'''

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", #.env文件位置
        env_file_encoding="utf-8"  #.env文件内容数据格式
    )

    database_url: str

settings = Settings()