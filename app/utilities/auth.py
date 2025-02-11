import os
from dotenv import load_dotenv
from fastapi import HTTPException, Request, Depends
import requests
import re
import jwt
from jwt.algorithms import RSAAlgorithm
import json
from datetime import datetime, timezone

# from app.utilities.logger import logger
from aws_wrapper.Cognito_wrapper import Cognito_wrapper
from app.daos.user import UserDao

from app.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.utils import UtilsService
# from app.utilities._entropy import validate as entropy_validate

load_dotenv()

region = os.getenv("REGION")
user_pool_id = os.getenv("USER_POOL_ID")
keys_url = "https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json".format(region, user_pool_id)
issuer = "https://cognito-idp.{}.amazonaws.com/{}".format(region, user_pool_id)


def request_method(url: str) -> requests.Response:
    """
    Make a GET request to the specified URL.

    Args:
        url (str): The URL to make the request to.

    Returns:
        requests.Response: The response object.
    """
    return requests.request("GET", url)


def verify_signature(access_token: str) -> dict:
    """
    Verify the signature of the JWT access token.

    Args:
        access_token (str): The JWT access token.

    Returns:
        dict: A dictionary containing the verified token information, including username and expiration.
    """
    key_response = request_method(keys_url)

    if key_response.status_code != 200:
        return {"error": f"Failed to fetch JWK. Status code: {key_response.status_code}", "verified": False}

    key_response = key_response.json()
    unverified_token_header = jwt.get_unverified_header(access_token)

    jwk_value = next((x for x in key_response["keys"] if x["kid"] == unverified_token_header["kid"]), None)

    if jwk_value is None:
        return {"error": "Local id and public id Didn't matched", "verified": False}

    public_key = RSAAlgorithm.from_jwk(json.dumps(jwk_value))

    decoded_token = jwt.decode(access_token, public_key, algorithms=[jwk_value["alg"]], issuer=issuer)

    username = decoded_token.get("username", None)
    exp = decoded_token.get("exp", None)

    return {"username": username, "exp": exp, "verified": True}


def return_email(value: list) -> str:
    """
    Extract the email address from the user attributes.

    Args:
        value (list): The list of user attributes.

    Returns:
        str: The email address of the user.
    """
    email_attribute = next((i["Value"] for i in value if i["Name"] == "email"), None)
    return email_attribute


def token_expired(exp: int) -> bool:
    """
    Check if the token has expired.

    Args:
        exp (int): The expiration timestamp of the token.

    Returns:
        bool: True if the token has expired, False otherwise.
    """
    dt = datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = utc_time.timestamp()
    return exp < utc_timestamp


async def is_authenticated(request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    """
    Authenticate the user based on the provided JWT access token.

    Args:
        request (Request): The FastAPI request object.

    Returns:
        dict: A dictionary containing the authenticated user information, including username, email, and expiration.
    """
    # body = await request.json()
    # access_token = body.get("access_token", None)

    # access_token = request.cookies.get("accessToken", None)
    access_token = UtilsService.token_handler(request)

    # raise exception if access token not provided.
    if access_token is None:
        raise HTTPException(status_code=401, detail="Access Token missing")

    # verify the signature of the access_token
    try:
        signature_value = verify_signature(access_token)
    except Exception as exp:
        raise HTTPException(status_code=401, detail=f"{exp}")

    # if siggature not verified raise exception
    if not signature_value["verified"]:
        raise HTTPException(status_code=401, detail=signature_value["error"])

    # if token expired raise exception
    if token_expired(signature_value["exp"]):
        raise HTTPException(status_code=401, detail="Token Expired.")

    # get the user info using cognito sdk for python to validate the user
    cognito_obj = Cognito_wrapper()
    try:
        user_info = cognito_obj.get_user(access_token)
    except Exception as exp:
        raise HTTPException(status_code=401, detail=f"Couldn't get user info from token. {exp}")

    # if signature username and the userinfo username not mached raise exception
    if signature_value["username"] != user_info["Username"]:
        raise HTTPException(status_code=401, detail="User Detail not matched.")

    # Get user Id by username
    user_session_dao = UserDao(session)
    user = await user_session_dao.get_by_username(signature_value["username"])

    authenticated_user = {
        "user_id": user.id,
        "username": signature_value["username"],
        "email": return_email(user_info.get("UserAttributes", [])),
        "exp": signature_value["exp"],
        "accessToken": access_token,
    }

    return authenticated_user


def validate_password(password):
    # Check for minimum length
    if len(password) < 8:
        return False, "Password must contain at least 8 characters."
    # Check for lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain a lower case letter."
    # Check for uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain an upper case letter."
    # Check for number
    if not re.search(r'\d', password):
        return False, "Password must contain a number."
    # Check for special character or space
    if not re.search(r'[\W_ ]', password):
        return False, "Password must contain a special character or a space."
    # Check for leading or trailing spaces
    if password.startswith(' ') or password.endswith(' '):
        return False, "Password must not contain a leading or trailing space."

    # if not entropy_validate(password):
    #     return False, "The password you have entered is not strong enough."
    return True, "Password is valid"
