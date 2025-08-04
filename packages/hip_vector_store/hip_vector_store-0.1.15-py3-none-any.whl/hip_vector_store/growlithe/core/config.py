from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    AWS_DEFAULT_REGION: str
    AWS_DEFAULT_REGION = "ap-southeast-2"
    DATABRICKS_CLUSTER_HOST: Optional[str] = Field(
        default=None,
        env="DATABRICKS_HOST",
    )
    DATABRICKS_PAT_TOKEN: Optional[str] = Field(
        default=None,
        env="DATABRICKS_TOKEN",
    )
    DATABRICKS_SQL_CLUSTER_PATH: Optional[str] = Field(
        default=None,
        env="DATABRICKS_SQL_PATH",
    )
    PIPELINE_TYPE: Optional[str] = Field(
        default="TRIGGERED",
        env="PIPELINE_TYPE",
    )
    UNITY_CATALOG: Optional[str] = Field(
        default=None,
        env="UNITY_CATALOG",
    )
    VECTOR_SEARCH_PREFIX: str
    VECTOR_SEARCH_PREFIX = "growlithe"
    VS_ENDPOINT_TYPE: str
    VS_ENDPOINT_TYPE = "STANDARD"


load_dotenv()
settings = Settings()
