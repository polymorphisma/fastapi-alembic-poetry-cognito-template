from fastapi import Request
from aws_wrapper.Cognito_wrapper import Cognito_wrapper
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession


from app.services.data_parser import DataParserService
from app.daos.user import UserDao
from app.services.utils import UtilsService
from app.utilities.logger import logger

cognito_obj = Cognito_wrapper()
data_parser_obj = DataParserService()


class UserService:
    @staticmethod
    async def create_response(response: dict) -> JSONResponse:
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return JSONResponse({
                'success': True,
                'data': response,
                'message': 'Login Successful'
            }, status_code=204)

        else:
            return JSONResponse({
                'success': False,
                'message': response
            }, status_code=404)

    @staticmethod
    async def user_profile(request: Request, session: AsyncSession) -> JSONResponse:
        session_dao = UserDao(session)
        # body = await request.json()
        # access_token = body.get("accessToken")
        # access_token = request.cookies.get("accessToken", '')
        try:
            access_token = UtilsService.token_handler(request)
            response = cognito_obj.get_user(access_token=access_token)

            value = data_parser_obj.parse_user_info(response)

            if session_dao.get_by_username("username") is None:
                await session_dao.create(value)

            return await UserService.create_response(response)

        except Exception as exp:
            logger.error(exp)
            return JSONResponse(
                {
                    "success": False,
                    "message": "Erorr: while getting user info."
                },
                status_code=404
            )
