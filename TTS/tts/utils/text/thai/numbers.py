"""Thai number normalization for TTS preprocessing."""

import re

# Thai digits mapping
THAI_DIGITS = {
    '๐': '0', '๑': '1', '๒': '2', '๓': '3', '๔': '4',
    '๕': '5', '๖': '6', '๗': '7', '๘': '8', '๙': '9'
}

# Thai number words
THAI_NUMBERS = {
    'ศูนย์': '0',
    'หนึ่ง': '1',
    'สอง': '2',
    'สาม': '3',
    'สี่': '4',
    'ห้า': '5',
    'หก': '6',
    'เจ็ด': '7',
    'แปด': '8',
    'เก้า': '9',
    'สิบ': '10',
    'ยี่สิบ': '20',
    'สามสิบ': '30',
    'สี่สิบ': '40',
    'ห้าสิบ': '50',
    'หกสิบ': '60',
    'เจ็ดสิบ': '70',
    'แปดสิบ': '80',
    'เก้าสิบ': '90',
    'ร้อย': '100',
    'พัน': '1000',
    'หมื่น': '10000',
    'แสน': '100000',
    'ล้าน': '1000000'
}

# Thai currency
THAI_CURRENCY = {
    'บาท': 'บาท',
    'สตางค์': 'สตางค์',
    'เหรียญ': 'เหรียญ'
}

# Thai measurement units
THAI_UNITS = {
    'กิโล': 'กิโลกรัม',
    'กรัม': 'กรัม',
    'มิลลิกรัม': 'มิลลิกรัม',
    'ลิตร': 'ลิตร',
    'มิลลิลิตร': 'มิลลิลิตร',
    'เซนติเมตร': 'เซนติเมตร',
    'เมตร': 'เมตร',
    'กิโลเมตร': 'กิโลเมตร',
    'เซนติกรัม': 'เซนติกรัม',
    'มิลลิเมตร': 'มิลลิเมตร'
}

def convert_thai_digits_to_arabic(text):
    """Convert Thai digits to Arabic digits."""
    for thai_digit, arabic_digit in THAI_DIGITS.items():
        text = text.replace(thai_digit, arabic_digit)
    return text

def convert_arabic_to_thai_words(number):
    """Convert Arabic numbers to Thai words."""
    if not isinstance(number, (int, str)):
        return str(number)
    
    try:
        number = int(number)
    except ValueError:
        return str(number)
    
    if number == 0:
        return 'ศูนย์'
    elif number < 0:
        return 'ลบ' + convert_arabic_to_thai_words(abs(number))
    
    thai_words = []
    position = 0
    
    while number > 0:
        digit = number % 10
        if digit > 0:
            if position == 0:
                if digit == 1 and number > 1:
                    thai_words.append('เอ็ด')
                elif digit == 2:
                    thai_words.append('ยี่')
                else:
                    thai_words.append(THAI_NUMBERS.get(str(digit), str(digit)))
            elif position == 1:
                if digit == 1:
                    thai_words.append('สิบ')
                elif digit == 2:
                    thai_words.append('ยี่สิบ')
                else:
                    thai_words.append(THAI_NUMBERS.get(str(digit), str(digit)) + 'สิบ')
            elif position == 2:
                thai_words.append('ร้อย')
                if digit > 1:
                    thai_words.append(THAI_NUMBERS.get(str(digit), str(digit)))
            elif position == 3:
                thai_words.append('พัน')
                if digit > 1:
                    thai_words.append(THAI_NUMBERS.get(str(digit), str(digit)))
            elif position == 4:
                thai_words.append('หมื่น')
                if digit > 1:
                    thai_words.append(THAI_NUMBERS.get(str(digit), str(digit)))
            elif position == 5:
                thai_words.append('แสน')
                if digit > 1:
                    thai_words.append(THAI_NUMBERS.get(str(digit), str(digit)))
            elif position == 6:
                thai_words.append('ล้าน')
                if digit > 1:
                    thai_words.append(THAI_NUMBERS.get(str(digit), str(digit)))
        
        number //= 10
        position += 1
    
    return ''.join(reversed(thai_words))

def normalize_phone_numbers(text):
    """Normalize Thai phone numbers."""
    # Thai mobile phone patterns
    mobile_pattern = r'(\d{3})[-\s]?(\d{3})[-\s]?(\d{4})'
    def replace_mobile(match):
        return match.group(1) + match.group(2) + match.group(3)
    
    text = re.sub(mobile_pattern, replace_mobile, text)
    
    # Landline numbers
    landline_pattern = r'(\d{2})[-\s]?(\d{3})[-\s]?(\d{4})'
    def replace_landline(match):
        return match.group(1) + match.group(2) + match.group(3)
    
    text = re.sub(landline_pattern, replace_landline, text)
    
    return text

def normalize_currency(text):
    """Normalize Thai currency expressions."""
    # Currency with numbers
    currency_pattern = r'(\d+(?:\.\d+)?)\s*(บาท|สตางค์)'
    
    def replace_currency(match):
        amount = match.group(1)
        unit = match.group(2)
        if unit == 'บาท':
            return convert_arabic_to_thai_words(amount.replace('.', '')) + 'บาท'
        elif unit == 'สตางค์':
            return convert_arabic_to_thai_words(amount.replace('.', '')) + 'สตางค์'
        return match.group(0)
    
    text = re.sub(currency_pattern, replace_currency, text)
    return text

def normalize_measurements(text):
    """Normalize Thai measurement units."""
    # Pattern for numbers followed by units
    measurement_pattern = r'(\d+(?:\.\d+)?)\s*(' + '|'.join(THAI_UNITS.keys()) + ')'
    
    def replace_measurement(match):
        number = match.group(1)
        unit = match.group(2)
        if unit in THAI_UNITS:
            return convert_arabic_to_thai_words(number.replace('.', '')) + THAI_UNITS[unit]
        return match.group(0)
    
    text = re.sub(measurement_pattern, replace_measurement, text)
    return text

def normalize_time_expressions(text):
    """Normalize Thai time expressions."""
    # Time patterns (HH:MM)
    time_pattern = r'(\d{1,2}):(\d{2})'
    
    def replace_time(match):
        hour = int(match.group(1))
        minute = int(match.group(2))
        
        # Convert hour to Thai
        if hour == 0:
            hour_thai = 'ศูนย์นาฬิกา'
        elif hour == 1:
            hour_thai = 'หนึ่งนาฬิกา'
        else:
            hour_thai = convert_arabic_to_thai_words(hour) + 'นาฬิกา'
        
        # Convert minute to Thai
        if minute == 0:
            return hour_thai
        else:
            minute_thai = convert_arabic_to_thai_words(minute) + 'นาที'
            return hour_thai + minute_thai
    
    text = re.sub(time_pattern, replace_time, text)
    return text

def normalize_date_expressions(text):
    """Normalize Thai date expressions."""
    # Date patterns (DD/MM/YYYY or DD-MM-YYYY)
    date_pattern = r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})'
    
    def replace_date(match):
        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3))
        
        day_thai = convert_arabic_to_thai_words(day)
        month_names = {
            1: 'มกราคม', 2: 'กุมภาพันธ์', 3: 'มีนาคม', 4: 'เมษายน',
            5: 'พฤษภาคม', 6: 'มิถุนายน', 7: 'กรกฎาคม', 8: 'สิงหาคม',
            9: 'กันยายน', 10: 'ตุลาคม', 11: 'พฤศจิกายน', 12: 'ธันวาคม'
        }
        month_thai = month_names.get(month, str(month))
        
        # Convert year to Thai year (พ.ศ.)
        thai_year = year + 543
        year_thai = convert_arabic_to_thai_words(thai_year)
        
        return f'วันที่ {day_thai} เดือน {month_thai} พุทธศักราช {year_thai}'
    
    text = re.sub(date_pattern, replace_date, text)
    return text

def normalize_numbers(text):
    """
    Complete number normalization for Thai text.
    
    Args:
        text (str): Text containing numbers to normalize
        
    Returns:
        str: Text with normalized numbers
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Convert Thai digits to Arabic
    text = convert_thai_digits_to_arabic(text)
    
    # Normalize phone numbers
    text = normalize_phone_numbers(text)
    
    # Normalize currency
    text = normalize_currency(text)
    
    # Normalize measurements
    text = normalize_measurements(text)
    
    # Normalize time expressions
    text = normalize_time_expressions(text)
    
    # Normalize date expressions
    text = normalize_date_expressions(text)
    
    # Convert standalone numbers to Thai words
    def replace_standalone_numbers(match):
        number = match.group(0)
        try:
            return convert_arabic_to_thai_words(int(number))
        except ValueError:
            return number
    
    # Replace standalone numbers (not part of other words)
    text = re.sub(r'\b\d+\b', replace_standalone_numbers, text)
    
    return text