from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    hostname: str
    port: int
    username: str
    private_key_path: Optional[str] = None  # Optional SSH private key path
