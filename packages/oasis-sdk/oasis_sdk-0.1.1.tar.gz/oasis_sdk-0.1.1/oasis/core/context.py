import secrets, time, uuid
from dataclasses import dataclass, field, replace

from .enums import Provider, ClientType
from ..utils import get_user_ip  

@dataclass(frozen=True, slots=True)
class RequestContext:
    """요청 단위 불변 메타데이터"""

    user_id: str
    workspace_code: str
    tenant_code: str
    provider: Provider
    client_type: ClientType
    plugin_name: str | None = None
    user_ip: str | None = None
    audit_state: bool = True
    root_id: str | None = None
    req_id: str = field(default_factory=lambda: secrets.token_hex(8))

    def __post_init__(self):
        if self.root_id is None:
            object.__setattr__(self, "root_id", self._make_root_id())
        if self.user_ip is None:
            object.__setattr__(self, "user_ip", get_user_ip())
        if self.plugin_name is None:
            object.__setattr__(self, "plugin_name", "default-plugin")

    @property
    def headers(self) -> dict[str, str]:
        return {
            "X-USER-ID": self.user_id,
            "X-USER-IP": self.user_ip,
            "X-WORKSPACE-CODE": self.workspace_code,
            "X-TENANT-CODE": self.tenant_code,
            "X-ROOT-ID": self.root_id,
            "X-REQ-ID": self.req_id,
            "X-PROVIDER": self.provider.value,        
            "X-CLIENT-TYPE": self.client_type.value,
            "X-AUDIT-STATE": str(self.audit_state).lower(),
            "X-PLUGIN-NAME": self.plugin_name,
        }

    def next(self) -> "RequestContext":
        """root_id는 고정하고 새 req_id만 부여"""
        return replace(self, req_id=secrets.token_hex(8))

    def _make_root_id(self) -> str:
        base = (
            f"{self.user_id}:{self.workspace_code}:{self.tenant_code}:"
            f"{int(time.time() * 1e6)}"
        )
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, base))
