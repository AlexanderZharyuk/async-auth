from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", summary="Получить всех пользователей")
async def mock_route() -> None:
    """
    Mock route.
    """
    return None
