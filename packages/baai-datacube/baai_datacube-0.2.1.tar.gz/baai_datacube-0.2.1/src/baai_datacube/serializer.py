from pydantic import BaseModel, Field


class ReqSignCreate(BaseModel):
    paths: list[str] = Field(default_factory=list)

class RespSignCreage(BaseModel):
    path: str
    endpoint: str


class JSONResponse(BaseModel):
    code:  int
    message: str
    data: RespSignCreage


class MetaData(BaseModel):
    video_id: int = Field(alias="videoId")
    obj_key: str = Field(alias="objKey")

    def get_storage_path(self) -> str:
        return f"ks3://baai-video-clips/{self.obj_key}"
