from dataclasses import dataclass


@dataclass
class BaseParams:
    idempotency_key: str
