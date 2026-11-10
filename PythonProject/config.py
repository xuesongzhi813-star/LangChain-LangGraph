from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    #设置读取的环境变量来自于哪里
    model_config = SettingsConfigDict(env_file=".env",extra="ignore")

    model:str
    base_url:str
    deepseek_api_key:str



    #deepseek的思考链
    thinking:str="disabled" #否则无法调用工具
    reasoning_effort:str="high" #思考强度

    token_budget: int=2000




settings = Settings()




