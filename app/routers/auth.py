from fastapi import APIRouter, status, Request, Response
from fastapi.responses import JSONResponse
from fastapi import Depends
from app.db import get_session
# from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
import os
from dotenv import load_dotenv
from app.services.auth import AuthService
from app.utilities.auth import is_authenticated


load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

router = APIRouter(tags=['User'], prefix='/auth')


@router.post('/login', status_code=status.HTTP_200_OK)
async def login(request: Request, response: Response, session: AsyncSession = Depends(get_session)) -> JSONResponse:
    return await AuthService.login(request, response, session)


@router.post('/register', status_code=status.HTTP_201_CREATED)
async def register(request: Request, session: AsyncSession = Depends(get_session)) -> JSONResponse:
    return await AuthService.register(request, session)


@router.post('/confirm-signup', status_code=status.HTTP_202_ACCEPTED)
async def confirm_signup(request: Request, session: AsyncSession = Depends(get_session)) -> JSONResponse:
    return await AuthService.confirm_signup(request, session)


@router.post('/get-token', status_code=status.HTTP_200_OK)
async def get_token(request: Request) -> JSONResponse:
    return await AuthService.get_token(request)


@router.post('/resend-code', status_code=status.HTTP_202_ACCEPTED)
async def resend_code(request: Request) -> JSONResponse:
    return await AuthService.resend_code(request)


@router.post('/reset-password', status_code=status.HTTP_200_OK)
async def reset_password(request: Request, authenticated=Depends(is_authenticated)) -> JSONResponse:
    return await AuthService.reset_password(request, authenticated)


@router.post('/forgot-password', status_code=status.HTTP_200_OK)
async def forgot_password_initial(request: Request) -> JSONResponse:
    return await AuthService.forgot_password_initial(request)


@router.post("/confirm-forgot-password", status_code=status.HTTP_200_OK)
async def confirm_forgot_password(request: Request) -> JSONResponse:
    return await AuthService.confirm_forgot_password(request)
