from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ActivityServerConfig:
    discord_api_base: str = "https://discord.com/api/v10"
    administrator_permission: int = 0x0000000000000008
    root_dir: Path = Path(__file__).resolve().parents[2]

    @property
    def client_dist(self) -> Path:
        return self.root_dir / "activity" / "client" / "dist"


activity_server_config = ActivityServerConfig()
