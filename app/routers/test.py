from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse

router = APIRouter(tags=['Test'], prefix='/test')


@router.get('/', status_code=status.HTTP_202_ACCEPTED)
async def user_profile(request: Request):
    return JSONResponse({"success": True, "message": "Api is working."})


@router.get('/error', status_code=status.HTTP_403_FORBIDDEN)
async def error_endpoint(request: Request):
    raise ValueError("testing for the error.")
