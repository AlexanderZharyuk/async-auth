from fastapi import APIRouter

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("/", summary="Получить все роли")
async def mock_route() -> None:
    """
    Mock route.
    """
    return None
