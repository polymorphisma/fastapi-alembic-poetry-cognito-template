from fastapi import Request

import base64
import hashlib
import hmac
import random
import re
import string
import time
import uuid
from urllib.parse import urlparse

import boto3
import jwt
from botocore.exceptions import ClientError

from app.settings import settings
from app.utilities.logger import logger


class UtilsService:
    @staticmethod
    def calculate_secret_hash(username: str, client_id: str, client_secret: str):
        message = username + client_id
        dig = hmac.new(
            str(client_secret).encode("utf-8"), msg=message.encode("utf-8"), digestmod=hashlib.sha256
        ).digest()
        return base64.b64encode(dig).decode()

    @staticmethod
    def token_handler(request: Request, method: str = "headers"):
        if method == "headers":
            access_token = request.headers.get("Authorization", "")
        elif method == "cookies":
            access_token = request.cookies.get("accessToken", "")

        return access_token

    @staticmethod
    async def generate_salt(lenght: int = 32):
        salt = uuid.uuid4().hex
        return salt[:lenght]

    @staticmethod
    async def generate_coder_password(password: str, salt: str, lenght: int = 16):
        # Encode the password and salt to bytes
        password_bytes = password.encode("utf-8")
        salt_bytes = salt.encode("utf-8")

        # Concatenate the password and salt bytes
        combined_bytes = password_bytes + salt_bytes

        # Hash the combined bytes
        hashed_password = hashlib.sha512(combined_bytes).hexdigest()
        return hashed_password[:lenght]

    @staticmethod
    async def generate_username(email: str):
        max_lenght = 127
        # Extract the part before the '@' symbol
        username_base = email.split("@")[0]

        # Replace all special characters with ''
        username_base = re.sub(r"\W+", "", username_base)

        if "_" in username_base:
            username_base = username_base.replace("_", "-")

        # Generate a random suffix
        suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
        # Combine the username base and the suffix
        username = f"{username_base}-{suffix}"

        if len(username) > max_lenght:
            username = username[:max_lenght]

        return username

    @staticmethod
    async def is_valid_domain(email: str):
        # regular expression for validating the email
        pattern = r"^[a-zA-Z0-9._%+-]+@adex\.ltd$"

        # regex to check if the email matches the pattern
        if re.match(pattern, email):
            return True
        else:
            return False

    @staticmethod
    def extract_owner_repo(url):
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip("/").split("/")
        if len(path_parts) >= 2:
            owner = path_parts[0]
            repo = path_parts[1]
            return owner, repo.replace(".git", "")

        return None, None

    @staticmethod
    def send_email(sender_mail: str, recipient_mail: str, subject: str, body: str):
        try:
            # Create a new SES resource and specify a region.
            client = boto3.client("ses", region_name=settings.REGION)
            response = client.send_email(
                Destination={
                    "ToAddresses": [
                        recipient_mail,
                    ],
                },
                Message={
                    "Subject": {"Data": subject, "Charset": "UTF-8"},
                    "Body": {"Text": {"Data": body, "Charset": "UTF-8"}},
                },
                Source=sender_mail,
            )
            return response
        # Display an error if something goes wrong.
        except ClientError as e:
            logger.error(e.response["Error"]["Message"])
            return None
