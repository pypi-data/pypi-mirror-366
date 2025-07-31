import re
from datetime import datetime


def is_valid_chinese_id(id_number):
    pattern = (
        r'^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dX]$'
    )

    if not re.match(pattern, id_number):
        return False, 'Pattern mismatch'

    # Extract components
    area_code = id_number[0:6]
    birth_year = int(id_number[6:10])
    birth_month = int(id_number[10:12])
    birth_day = int(id_number[12:14])
    order_code = id_number[14:17]
    check_digit_char = id_number[17].upper()  # Ensure X is handled consistently

    # 1. Date Validity Check (more robust than regex alone)
    try:
        birth_date = datetime(birth_year, birth_month, birth_day)
        # Check if the date is not in the future
        if birth_date > datetime.now():
            return False, 'Birth date is in the future'
    except ValueError:
        return False, 'Invalid date'

    # 2. Checksum Validation (Crucial for full validity)
    # Weights for the first 17 digits
    weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    # Corresponding check digits
    check_digits = [
        '1',
        '0',
        'X',
        '9',
        '8',
        '7',
        '6',
        '5',
        '4',
        '3',
        '2',
    ]  # Note 'X' for 10

    s = 0
    for i in range(17):
        s += int(id_number[i]) * weights[i]

    calculated_check_digit_index = s % 11
    expected_check_digit = check_digits[calculated_check_digit_index]

    if check_digit_char != expected_check_digit:
        return (
            False,
            f'Checksum mismatch. Expected: {expected_check_digit}, Got: {check_digit_char}',
        )

    # 3. (Optional but recommended) Administrative Division Code check
    # This would require a database or list of valid administrative codes,
    # which is too extensive for a simple regex.
    # if area_code not in valid_area_codes:
    #     return False, "Invalid area code"

    return True, 'Valid ID'
