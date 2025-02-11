from fastapi import APIRouter, status, Request, Depends
from app.db import get_session
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession


from app.services.user import UserService
from app.utilities.auth import is_authenticated
from app.services.utils import UtilsService

router = APIRouter(tags=['User'], prefix='/user')


@router.post('/profile', status_code=status.HTTP_202_ACCEPTED)
async def user_profile(request: Request, _=Depends(is_authenticated), session: AsyncSession = Depends(get_session)):
    return await UserService.user_profile(request, session)


@router.get('/profile', status_code=status.HTTP_200_OK)
async def get_user_profile(request: Request, authenticated=Depends(is_authenticated)):
    UtilsService.token_handler(request)
    return JSONResponse({'MESSAGE': f"Hello {authenticated['username']}", "authenticated": authenticated})
