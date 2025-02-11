import boto3
import os
import boto3.exceptions
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import hmac
import hashlib
import base64

load_dotenv()


AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
REGION = os.getenv("REGION")


CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

if AWS_ACCESS_KEY_ID != '' and AWS_SECRET_ACCESS_KEY != '':
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=REGION
    )
else:
    session = boto3.Session()

cognito_client = session.client('cognito-idp')


class CognitoError(Exception):
    """Custome exception for Cognito-related errors."""


class Cognito_wrapper():
    def __init__(self) -> None:
        pass

    def _secret_hash(self, username: str, client_id: str, client_secret: str):
        message = username + client_id
        dig = hmac.new(
            str(client_secret).encode("utf-8"), msg=message.encode("utf-8"), digestmod=hashlib.sha256
        ).digest()
        return base64.b64encode(dig).decode()

    def _generate_error(self, exp: str = None):
        response = {
            'ResponseMetadata': {
                'HTTPStatusCode': 400
            },
            'message': str(exp),
            "success": False
        }

        return response

    def create_user_pool(self, user_pool_name: str):
        response = cognito_client.create_user_pool(
            PoolName=user_pool_name
        )
        return response

    def delete_user_pool(self, user_pool_id: str):
        dicts = {
            'UserPoolId': user_pool_id
        }
        response = cognito_client.delete_user_pool(
            **dicts
        )
        return response

    def create_group(self, user_pool_id: str, group_name: str, description: str = '', role_arn: str = '', precedence: int = None) -> dict:
        dicts = {
            'GroupName': group_name,
            'UserPoolId': user_pool_id,
            'Description': description,
            'RoleArn': role_arn,
            'Precedence': precedence
        }

        response = cognito_client.create_group(
            **dicts
        )

        return response

    def delete_group(self, user_pool_id: str, group_name: str):
        dicts = {
            'GroupName': group_name,
            'UserPoolId': user_pool_id
        }

        respones = cognito_client.delete_group(
            **dicts
        )

        return respones

    def create_user(self, user_pool_id: str, username: str, password: str = None) -> dict:
        dicts = {
            'UserPoolId': user_pool_id,
            'Username': username,
        }

        if password is not None:
            dicts['TemporaryPassword'] = password

        response = cognito_client.admin_create_user(
            **dicts
        )

        return response

    def delete_user(self, user_pool_id: str, username: str) -> dict:
        dicts = {
            'UserPoolId': user_pool_id,
            'Username': username
        }

        response = cognito_client.admin_delete_user(
            **dicts
        )

        return response

    def add_user_to_group(self, user_pool_id: str, username: str, group_name: str):
        dicts = {
            'UserPoolId': user_pool_id,
            'Username': username,
            'GroupName': group_name
        }

        response = cognito_client.admin_add_user_to_group(
            **dicts
        )

        return response

    def remove_user_from_group(self, user_pool_id: str, username: str, group_name: str) -> dict:
        dicts = {
            'UserPoolId': user_pool_id,
            'Username': username,
            'GroupName': group_name
        }

        response = cognito_client.admin_remove_user_from_group(
            **dicts
        )

        return response

    def disable_user(self, user_pool_id: str, username: str) -> dict:
        dicts = {
            'UserPoolId': user_pool_id,
            'Username': username
        }

        response = cognito_client.admin_disable_user(
            **dicts
        )

        return response

    def enable_user(self, user_pool_id: str, username: str) -> dict:
        dicts = {
            'UserPoolId': user_pool_id,
            'Username': username
        }

        response = cognito_client.admin_enable_user(
            **dicts
        )

        return response

    def initiate_auth(self, client_id: str, secret_hash: str, username: str = '', password: str = '', refresh_token: str = '', auth_flow: str = 'USER_PASSWORD_AUTH') -> dict:
        dicts = {
            'AuthFlow': auth_flow,
            'ClientId': client_id
        }

        if auth_flow == 'USER_PASSWORD_AUTH':
            dicts['AuthParameters'] = {
                'USERNAME': username,
                'PASSWORD': password,
                'SECRET_HASH': secret_hash
            }

        if auth_flow == 'REFRESH_TOKEN_AUTH':
            dicts['AuthParameters'] = {
                'REFRESH_TOKEN': refresh_token,
                'SECRET_HASH': secret_hash
            }
        try:
            response = cognito_client.initiate_auth(
                **dicts
            )

        except ClientError as e:
            response = self._generate_error(f"Error: {e.response['Error']['Message']}")

        except Exception as exp:
            response = self._generate_error(exp)

        return response

    def sign_up(self, username: str, password: str, client_id: str, secret_hash: str, email: str = '', name: str = '') -> dict:
        dicts = {
            'ClientId': client_id,
            'SecretHash': secret_hash,
            'Username': username,
            'Password': password,
        }

        if name != '':
            if 'UserAttributes' not in dicts:
                dicts['UserAttributes'] = []

            dicts['UserAttributes'].append(
                    {
                        'Name': 'name',
                        'Value': name
                    }
                )

        if email != '':
            if 'UserAttributes' not in dicts:
                dicts['UserAttributes'] = []

            dicts['UserAttributes'].append(
                    {
                        'Name': 'email',
                        'Value': email
                    }
                )
        try:
            response = cognito_client.sign_up(
                **dicts
            )

        except ClientError as e:
            response = self._generate_error(f"Error: {e.response['Error']['Message']}")

        except Exception as exp:
            response = self._generate_error(exp)

        return response

    def confirm_sign_up(self, client_id: str, secret_hash: str, username: str, confirmation_code: str) -> dict:
        dicts = {
            'ClientId': client_id,
            'Username': username,
            'SecretHash': secret_hash,
            'ConfirmationCode': confirmation_code
        }

        try:
            response = cognito_client.confirm_sign_up(
                **dicts
            )
        except Exception as exp:
            response = self._generate_error(exp)

        return response

    def resend_confirmation_code(self, client_id: str, secret_hash: str, username: str) -> dict:
        dicts = {
            'ClientId': client_id,
            'Username': username,
            'SecretHash': secret_hash,
        }

        try:
            response = cognito_client.resend_confirmation_code(
                **dicts
            )
        except Exception as exp:
            response = self._generate_error(exp)

        return response

    def get_user(self, access_token: str):
        dicts = {
            'AccessToken': access_token
        }
        try:
            response = cognito_client.get_user(
                **dicts
            )

        except Exception as exp:
            response = self._generate_error(exp)

        return response

    def list_user(self, user_pool_id: str):
        dicts = {
            'UserPoolId': user_pool_id
        }
        try:
            response = cognito_client.list_users(
                **dicts
            )

        except Exception as exp:
            response = self._generate_error(exp)

        return response

    def reset_password(self, o_password: str, n_password: str, access_token: str) -> dict:
        dicts = {
            'PreviousPassword': o_password,
            'ProposedPassword': n_password,
            'AccessToken': access_token,
        }

        try:
            response = cognito_client.change_password(
                **dicts
            )
        except Exception as exp:
            response = self._generate_error(exp)

        return response

    def forgot_password_initial(self, client_id: str, secret_hash: str, username: str) -> dict:
        dicts = {
            'ClientId': client_id,
            'Username': username,
            'SecretHash': secret_hash,
        }

        try:
            response = cognito_client.forgot_password(
                **dicts
            )
        except Exception as exp:
            response = self._generate_error(exp)

        return response

    def confirm_forgot_password(self, client_id: str, secret_hash: str, username: str, code: str, password: str) -> dict:
        dicts = {
            "ClientId": client_id,
            "SecretHash": secret_hash,
            "Username": username,
            "ConfirmationCode": code,
            "Password": password,
        }

        try:
            response = cognito_client.confirm_forgot_password(
                **dicts
            )
        except Exception as exp:
            response = self._generate_error(exp)

        return response


if __name__ == '__main__':
    # user_pool_name = 'testing-user-pool-polymorphisma'
    user_pool_id = os.getenv('USER_POOL_ID')
    username = 'meshrawan'
    password = 'test@passwaoraAd1'

    # group_name = 'test-user-pool-polymorphisma-admin'
    # rolearn = 'arn:aws:iam::426857564226:role/Developer_AdministratorAccess'

    value = ''
    cognito_obj = Cognito_wrapper()

    # # delete
    # value = cognito_obj.list_user(user_pool_id=user_pool_id)
    # users = value.get("Users")

    # for user in users:
    #     username = user.get("Username")

    #     value = cognito_obj.delete_user(user_pool_id=user_pool_id, username=username)
    #     print(username)
    #     print(value)

    # cognito_obj.create_user(user_pool_id, username, password)
    # value = cognito_obj.delete_user(user_pool_id, username)

    # value = cognito_obj.create_group(user_pool_id, group_name, description='', role_arn=rolearn, precedence=0)
    # value = cognito_obj.delete_group(user_pool_id, group_name)

    # value = cognito_obj.add_user_to_group(user_pool_id, username, group_name)
    # value = cognito_obj.remove_user_from_group(user_pool_id, username, group_name)

    # value = cognito_obj.create_user_pool(user_pool_name)
    # value = cognito_obj.delete_user_pool(user_pool_id)

    # value = cognito_obj.disable_user(user_pool_id, username)
    # value = cognito_obj.enable_user(user_pool_id, username)

    # json_dumps = json.dumps(value, indent=4, sort_keys=True, default=str)
    # with open(f"{user_pool_name}deleteUser.json", "w", encoding="utf-8") as wf:
    #     wf.write(json_dumps)
