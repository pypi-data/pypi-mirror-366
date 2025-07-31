from dataclasses import dataclass


@dataclass
class FlespiError:
    code: int
    reason: str
    id: int | None = None
    selector: str | None = None


class FlespiException(Exception):
    def __init__(self, status_code: int, errors: list[dict]):
        self.status_code = status_code
        self.errors = [FlespiError(**error) for error in errors]
