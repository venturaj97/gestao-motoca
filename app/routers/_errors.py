from fastapi import HTTPException


def raise_mapped_error(
    error: ValueError,
    mapping: dict[str, tuple[int, str]],
    default_status: int = 400,
    default_detail: str = "Erro desconhecido",
) -> None:
    status_code, detail = mapping.get(str(error), (default_status, default_detail))
    raise HTTPException(status_code=status_code, detail=detail)
