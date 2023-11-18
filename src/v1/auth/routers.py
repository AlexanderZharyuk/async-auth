from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/", summary="Авторизоваться в сервисе")
async def mock_route() -> None:
    """
    Mock route.
    """
    return None
