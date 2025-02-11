import math


def get_entropy(password: str) -> float:
    """
    Calculate the entropy of a given password.

    Entropy is a measure of the unpredictability or randomness of the password. 
    Higher entropy means the password is harder to guess.

    Args:
        password (str): The password string for which entropy is to be calculated.

    Returns:
        float: The calculated entropy of the password.
    """
    base = get_base(password)
    length = adjust_length_for_common_patterns(password)
    # calculate log2(base^length)
    return log_pow(float(base), length, 2)


def get_base(password: str) -> int:
    """
    Determine the base of the password.

    The base is calculated by identifying the different character sets used in the password 
    (e.g., lowercase letters, uppercase letters, digits, special characters).

    Args:
        password (str): The password string for which the base is to be calculated.

    Returns:
        int: The base value representing the number of unique characters used in the password.
    """
    base = 0
    special_char_sets = {
        'lowercase': "abcdefghijklmnopqrstuvwxyz",
        'uppercase': "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        'digits': "0123456789",
        'replace': "!@$&*",
        'separator': "_-., ",
        'other_special': """\"#%'()+/:;<=>?[\\]^{|}~"""
    }
    used_sets = {key: False for key in special_char_sets}
    additional_chars = set()

    for c in password:
        found = False
        for key, chars in special_char_sets.items():
            if c in chars:
                used_sets[key] = True
                found = True
                break
        if not found:
            additional_chars.add(c)
    base = sum(len(chars) for key, chars in special_char_sets.items() if used_sets[key])
    base += len(additional_chars)
    return base


def adjust_length_for_common_patterns(password: str) -> int:
    """
    Adjust the length of the password for common patterns.

    This function reduces the length of the password if common sequences 
    or repeated characters are found, which decreases the effective entropy.

    Args:
        password (str): The password string for which the length is to be adjusted.

    Returns:
        int: The adjusted length of the password.
    """
    sequences = [
        "0123456789", "qwertyuiop", "asdfghjkl", "zxcvbnm",
        "abcdefghijklmnopqrstuvwxyz"
    ]
    length = len(password)
    same_char_count = 1
    for i in range(1, length):
        if password[i] == password[i-1]:
            same_char_count += 1
        else:
            if same_char_count > 2:
                length -= same_char_count - 2
            same_char_count = 1
    if same_char_count > 2:
        length -= same_char_count - 2

    lower_password = password.lower()
    for seq in sequences:
        if seq in lower_password or seq[::-1] in lower_password:
            length -= len(seq) - 2
            break

    return length


def log_x(base: int, n: int) -> float:
    """
    Calculate the logarithm of a number with a given base.

    Args:
        base (int): The base of the logarithm.
        n (int): The number for which the logarithm is to be calculated.

    Returns:
        float: The logarithm of the number with the specified base.
    """
    if base == 0:
        return 0
    return math.log2(n) / math.log2(base)


def log_pow(exp_base: float, pow: int, log_base: int) -> float:
    """
    Calculate the logarithm of a power without leaving log space for each multiplication step.

    Args:
        exp_base (float): The base of the exponentiation.
        pow (int): The exponent.
        log_base (int): The base of the logarithm.

    Returns:
        float: The calculated logarithm of the power.
    """
    total = 0.0
    for _ in range(pow):
        total += log_x(log_base, exp_base)
    return total


def validate(password: str, entropy_value: int = 52) -> bool:
    """
    Validate a password based on its entropy.

    Args:
        password (str): The password string to validate.
        entropy_value (int, optional): The minimum entropy value required for the password to be considered valid. Defaults to 52.

    Returns:
        bool: True if the password entropy is less than the specified value, False otherwise.
    """
    try:
        entropy = get_entropy(password)

    except Exception:
        raise ValueError("Problem while geting entropy result.")

    return entropy > entropy_value


if __name__ == "__main__":
    print(validate("newP@sswordB1h", 52))
