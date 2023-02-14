from dataclasses import dataclass


@dataclass(frozen=True)
class _Settings:
    undefined: str = ''
    suffix: str = '.lgst'
    encoding = 'utf-8'
    divider: str = ':'


settings = _Settings()
