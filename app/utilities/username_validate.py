# import re


def validate_username(username: str) -> bool:
    """
    Validates the username based on the given rules.

    Rules:
    - Maximum length of 127 characters
    - Should not contain any special characters

    Parameters:
    username (str): The username to validate

    Returns:
    bool: True if the username is valid, False otherwise
    """
    # Check for maximum length
    if len(username) > 127:
        return False

    # # Check for special characters
    # if re.search(r'[^a-zA-Z0-9]', username):
    #     return False

    return True
