from app.utilities.logger import logger


class DataParserService:
    def __init__(self) -> None:
        pass

    def parse_user_info(self, response: dict):
        dicts = {}
        for i in response.get("UserAttributes", []):
            key = i.get("Name", "")
            value = i.get("Value", "")
            if key == 'email_verified':
                value = value == 'true'
            dicts[key] = value
        dicts['username'] = response.get("Username", "")
        return dicts
