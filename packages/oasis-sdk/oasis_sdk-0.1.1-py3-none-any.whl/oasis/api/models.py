import httpx
from pydantic import BaseModel
from ..base import DEFAULT_PROXY_URL
from ..utils import get_from_env


class ModelInfo(BaseModel):
    """프록시 서버가 반환하는 모델 메타 정보"""
    provider_type: str
    provider_code: str
    actual_model_name: str
    model_name: str
    model_version: str
    model_type: str

def get_model_info(tenant_code: str, model_id: str, proxy_url: str | None = None) -> ModelInfo:
    proxy_url = proxy_url or get_from_env('OASIS_PROXY_URL', DEFAULT_PROXY_URL)
    endpoint = f"{proxy_url}/model-info?model_id={model_id}"

    headers = {
        "X-Tenant-CODE": tenant_code,
        "Accept": "application/json",
    }

    with httpx.Client(timeout=5.0) as client:
        resp = client.get(endpoint, headers=headers)
        resp.raise_for_status()
        response = resp.json()

        return ModelInfo(**response)