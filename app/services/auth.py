from fastapi import Request, Response
from fastapi.responses import JSONResponse
from app.services.utils import UtilsService
from aws_wrapper.Cognito_wrapper import Cognito_wrapper
from app.utilities.username_validate import validate_username
from sqlalchemy.ext.asyncio import AsyncSession

from app.daos.user import UserDao

from app.utilities.logger import logger
from app.services.data_parser import DataParserService
from app.utilities.auth import validate_password

import os
from dotenv import load_dotenv

load_dotenv()

data_parser_obj = DataParserService()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


cognito_obj = Cognito_wrapper()


class AuthService:
    @staticmethod
    async def create_response(response: dict, message: str = "Login Successful.") -> JSONResponse:
        if not isinstance(message, str):
            message = str(message)

        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return JSONResponse({"success": True, "data": response, "message": message})

        else:
            return JSONResponse({"success": False, "message": response.get("message", "")}, status_code=404)

    @staticmethod
    async def _check_success(response: dict) -> bool:
        return response["ResponseMetadata"]["HTTPStatusCode"] == 200

    @staticmethod
    async def login(request: Request, response: Response, session: AsyncSession) -> JSONResponse:
        body = await request.json()

        email = body.get("email", "")
        password = body.get("password", "")
        user_session_dao = UserDao(session)

        secret_hash = UtilsService.calculate_secret_hash(email, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        user_value = cognito_obj.initiate_auth(
            username=email, password=password, client_id=CLIENT_ID, secret_hash=secret_hash
        )
        if await AuthService._check_success(user_value):
            return_value = {"success": True, "data": user_value, "message": "Login Successful"}
        else:
            return_value = {"success": False, "message": user_value.get("message", "")}

        if return_value['success']:
            user_info = await user_session_dao.get_by_email(email)
            required_keys = ['username', 'email', 'email_verified']

            if isinstance(user_info, type(None)):
                return JSONResponse({
                    "success": False,
                    "message": "User not found."
                }, status_code=404)

            user_info = user_info.__dict__
            user_info = {x: user_info[x] for x in user_info if x in required_keys}

            return_value['data']['user_data'] = user_info

        return return_value

    @staticmethod
    async def register(request: Request, session: AsyncSession) -> JSONResponse:
        user_session_dao = UserDao(session)

        body = await request.json()

        password = body.get("password", "")
        name = body.get("name", "")
        email = body.get("email", "")

        # domain validation for @adex.ltd
        if not await UtilsService.is_valid_domain(email=email):
            return JSONResponse(
                {
                    "success": False,
                    "message": f"The email '{email}' does not belong to the allowed domain.",
                },
                status_code=401
            )

        username = await UtilsService.generate_username(email)

        # DEPRECATED
        # if not validate_username(username):
        #     return JSONResponse(
        #         {
        #             "success": False,
        #             "message": "Invalid username: must be 127 characters or fewer.",
        #         },
        #         status_code=404
        #     )

        is_valid, password_validate_message = validate_password(password)
        if not is_valid:
            return JSONResponse(
                {
                    "success": False,
                    "message": str(password_validate_message)
                },
                status_code=400
            )

        # DEPRECATED since we generate our own username validation not required.
        # user_exists = await user_session_dao.get_by_username(username)

        # # TODO we need to handle if user already exists but if email is not verified then what to do?
        # if user_exists is not None:
        #     return JSONResponse(
        #         {
        #             "success": False,
        #             "message": "Error: The provided username is already associated with an existing account.",
        #         },
        #         status_code=404
        #     )

        user_exists = await user_session_dao.get_by_email(email)
        # TODO we need to handle if user already exists but if email is not verified then what to do?
        if user_exists is not None:
            return JSONResponse(
                {
                    "success": False,
                    "message": "Error: The provided email address is already associated with an existing account.",
                },
                status_code=400
            )

        secret_hash = UtilsService.calculate_secret_hash(username, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        response = cognito_obj.sign_up(
            username=username, password=password, client_id=CLIENT_ID, secret_hash=secret_hash, name=name, email=email
        )

        if not await AuthService._check_success(response):
            return await AuthService.create_response(response)

        user_info = {"username": username, "password": password, "name": name, "email": email}

        # await user_session_dao.create_temp_user(user_info)
        user_info["sub"] = response.get("UserSub", "")

        del user_info["password"]
        await user_session_dao.create(user_info)

        return await AuthService.create_response(response, message="Registration successful. Please check your email for OTP.")

    @staticmethod
    async def confirm_signup(request: Request, session: AsyncSession) -> JSONResponse:
        user_session_dao = UserDao(session)
        body = await request.json()
        email = body.get("email", "")
        confirmation_code = body.get("code", "")

        user_info = await user_session_dao.get_by_email(email=email)
        try:
            username = user_info.username
        except Exception as exp:
            logger.error(exp)
            return JSONResponse(
                {
                    "success": False,
                    "message": "User with provided email not found."
                },
                status_code=404
            )

        secret_hash = UtilsService.calculate_secret_hash(username, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        response = cognito_obj.confirm_sign_up(
            client_id=CLIENT_ID, secret_hash=secret_hash, username=username, confirmation_code=confirmation_code
        )

        # user_data = await user_session_dao.get_by_username(username)
        salt = await UtilsService.generate_salt()
        if not await AuthService._check_success(response):
            return await AuthService.create_response(response)

        await user_session_dao.update_email_verified(username)
        await user_session_dao.update_salt(username=username, salt=salt)
        # await user_session_dao.delete_temp_by_id(user_data.id)
        return await AuthService.create_response(response, message="Your account has been confirmed successfully. You can now log in.")

    @staticmethod
    async def get_token(request: Request) -> JSONResponse:
        body = await request.json()
        refresh_token = body.get("refreshToken", "")
        username = body.get("username", "")
        auth_method = "REFRESH_TOKEN_AUTH"

        secret_hash = UtilsService.calculate_secret_hash(username, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        response = cognito_obj.initiate_auth(
            client_id=CLIENT_ID, secret_hash=secret_hash, refresh_token=refresh_token, auth_flow=auth_method
        )
        return await AuthService.create_response(response, message="Token generated successfully.")

    @staticmethod
    async def resend_code(request: Request) -> JSONResponse:
        body = await request.json()
        email = body.get("email", "")

        if email == "":
            return JSONResponse(
                {
                    "success": False,
                    "message": "email not provided."
                },
                status_code=404
            )

        secret_hash = UtilsService.calculate_secret_hash(email, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        response = cognito_obj.resend_confirmation_code(client_id=CLIENT_ID, secret_hash=secret_hash, username=email)
        return await AuthService.create_response(response, message="Token generated successfully. Check your mail for the OTP code.")

    @staticmethod
    async def reset_password(request: Request, authenticated: dict) -> JSONResponse:
        body = await request.json()

        old_password = body.get("old_password")
        new_password = body.get("new_password")
        access_token = UtilsService.token_handler(request)

        username = authenticated.get("username", "")
        if username == '':
            return JSONResponse(
                {
                    "success": False,
                    "message": "User not found."
                },
                status_code=404
            )
        is_valid, password_validate_message = validate_password(new_password)
        if not is_valid:
            return JSONResponse(
                {
                    "success": False,
                    "message": str(password_validate_message)
                },
                status_code=404
            )

        response = cognito_obj.reset_password(o_password=old_password, n_password=new_password, access_token=access_token)
        return await AuthService.create_response(response, message="Password changed successfully. Now you can login using new password.")

    @staticmethod
    async def forgot_password_initial(request: Request) -> JSONResponse:
        body = await request.json()
        username = body.get("username", "")

        secret_hash = UtilsService.calculate_secret_hash(username, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        response = cognito_obj.forgot_password_initial(client_id=CLIENT_ID, secret_hash=secret_hash, username=username)

        return await AuthService.create_response(response, message="Password reset request received. Please check your email for OTP Code.")

    @staticmethod
    async def confirm_forgot_password(request: Request) -> JSONResponse:
        body = await request.json()
        username = body.get("username", "")
        code = body.get("code", "")
        password = body.get("password", "")

        if not validate_username(username):
            return JSONResponse({
                "success": False,
                "message": "Invalid username: must be 127 characters or fewer and contain only alphanumeric characters."
            })

        is_valid, password_validate_message = validate_password(password)
        if not is_valid:
            return JSONResponse({
                "success": False,
                "message": password_validate_message
            })

        secret_hash = UtilsService.calculate_secret_hash(username, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        # TODO
        # need to implement logic to handle passowrd change on the coder.
        response = cognito_obj.confirm_forgot_password(client_id=CLIENT_ID, secret_hash=secret_hash, username=username, code=code, password=password)

        return await AuthService.create_response(response, message="Password has been reset successfully. You can now log in with your new password.")
