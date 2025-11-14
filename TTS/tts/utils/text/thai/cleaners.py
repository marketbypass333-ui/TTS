"""Thai text cleaners for TTS preprocessing."""

import re
import unicodedata

from .numbers import normalize_numbers
from .phonemes import thai_to_phonemes

# Thai character ranges
THAI_VOWELS = r'[ะ-ฺเ-ๆ]'
THAI_CONSONANTS = r'[ก-ฮ]'
THAI_DIACRITICS = r'[ัิ-ฺ]'
THAI_DIGITS = r'[๐-๙]'
THAI_CHARS = r'[฀-๿]'

# Thai abbreviations and common replacements
THAI_ABBREVIATIONS = {
    r'\bกทม\b': 'กรุงเทพมหานคร',
    r'\bจชต\b': 'จังหวัดชายแดนภาคใต้',
    r'\bรร\b': 'โรงเรียน',
    r'\bรพ\b': 'โรงพยาบาล',
    r'\bมอ\b': 'มหาวิทยาลัย',
    r'\bรรท\b': 'รถไฟ',
    r'\bทบ\b': 'ทหารบก',
    r'\bทร\b': 'ทหารเรือ',
    r'\bทอ\b': 'ทหารอากาศ',
    r'\bตร\b': 'ตำรวจ',
    r'\bอปท\b': 'องค์การปกครองส่วนท้องถิ่น',
    r'\bอบต\b': 'องค์การบริหารส่วนตำบล',
    r'\bอบจ\b': 'องค์การบริหารส่วนจังหวัด',
    r'\bกอช\b': 'กองทุนการออมแห่งชาติ',
    r'\bสปช\b': 'สภาปฏิรูปแห่งชาติ',
    r'\bสนช\b': 'สภานิติบัญญัติแห่งชาติ',
    r'\bสส\b': 'สมาชิกสภาผู้แทนราษฎร',
    r'\bสว\b': 'สมาชิกวุฒิสภา',
}

# Common Thai particles and polite particles
THAI_PARTICLES = {
    'ครับ': 'ครับ',
    'ค่ะ': 'ค่ะ',
    'นะ': 'นะ',
    'เถอะ': 'เถอะ',
    'สิ': 'สิ',
    'หน่อย': 'หน่อย',
    'แล้ว': 'แล้ว',
    'จ้ะ': 'จ้ะ',
    'จ้า': 'จ้า',
}

# Thai honorifics and titles
THAI_TITLES = {
    r'\bดร\b': 'ดอกเตอร์',
    r'\bผศ\b': 'ผู้ช่วยศาสตราจารย์',
    r'\bรศ\b': 'รองศาสตราจารย์',
    r'\bศ\b': 'ศาสตราจารย์',
    r'\bทพ\b': 'ทันตแพทย์',
    r'\bนพ\b': 'แพทย์',
    r'\bพญ\b': 'พยาบาล',
    r'\bรต\b': 'ร้อยตรี',
    r'\bรท\b': 'ร้อยโท',
    r'\bรอ\b': 'ร้อยเอก',
    r'\bพต\b': 'พันตรี',
    r'\bพท\b': 'พันทหาร',
    r'\bพอ\b': 'พันเอก',
}

# Whitespace normalization
_whitespace_re = re.compile(r'\s+')

# Thai character normalization
def normalize_thai_chars(text):
    """Normalize Thai characters and remove zero-width spaces."""
    # Remove zero-width spaces and other invisible characters
    text = re.sub(r'[\u200B\u200C\u200D\uFEFF]', '', text)
    
    # Normalize Unicode characters
    text = unicodedata.normalize('NFC', text)
    
    # Replace multiple spaces with single space
    text = re.sub(_whitespace_re, ' ', text)
    
    return text.strip()

def expand_abbreviations(text):
    """Expand Thai abbreviations to full words."""
    for abbreviation, full_form in THAI_ABBREVIATIONS.items():
        text = re.sub(abbreviation, full_form, text, flags=re.IGNORECASE)
    return text

def expand_titles(text):
    """Expand Thai titles and honorifics."""
    for abbreviation, full_form in THAI_TITLES.items():
        text = re.sub(abbreviation, full_form, text, flags=re.IGNORECASE)
    return text

def clean_thai_punctuation(text):
    """Clean and normalize Thai punctuation."""
    # Replace multiple punctuation with single
    text = re.sub(r'[.]{2,}', '.', text)
    text = re.sub(r'[,]{2,}', ',', text)
    text = re.sub(r'[?]{2,}', '?', text)
    text = re.sub(r'[!]{2,}', '!', text)
    
    # Normalize Thai-specific punctuation
    text = re.sub(r'[\u0E2F\u0E46]', ',', text)  # Thai punctuation marks
    
    # Remove excessive spaces around punctuation
    text = re.sub(r'\s*([.!?,:])\s*', r'\1 ', text)
    text = re.sub(r'\s+([.!?,:])', r'\1', text)
    
    return text.strip()

def validate_thai_text(text):
    """Validate that text contains proper Thai characters."""
    # Check if text contains Thai characters
    if not re.search(THAI_CHARS, text):
        return False
    
    # Check for proper character ordering (consonant + vowel/diacritic)
    # This is a basic check - Thai script is complex
    has_consonant = re.search(THAI_CONSONANTS, text)
    
    return has_consonant is not None

def thai_cleaners(text):
    """
    Complete Thai text cleaning pipeline for TTS.
    
    Args:
        text (str): Raw Thai text input
        
    Returns:
        str: Cleaned and processed Thai text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Basic cleaning
    text = text.strip()
    
    # Normalize Thai characters
    text = normalize_thai_chars(text)
    
    # Expand abbreviations and titles
    text = expand_abbreviations(text)
    text = expand_titles(text)
    
    # Normalize numbers (Thai and Arabic)
    text = normalize_numbers(text)
    
    # Clean punctuation
    text = clean_thai_punctuation(text)
    
    # Final whitespace cleanup
    text = re.sub(_whitespace_re, ' ', text).strip()
    
    return text

def basic_thai_cleaners(text):
    """Basic Thai cleaning without abbreviation expansion."""
    if not text or not isinstance(text, str):
        return ""
    
    text = normalize_thai_chars(text)
    text = normalize_numbers(text)
    text = clean_thai_punctuation(text)
    text = re.sub(_whitespace_re, ' ', text).strip()
    
    return text