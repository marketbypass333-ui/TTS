"""Thai phoneme mapping and phonetic transcription for TTS."""

import re
from typing import List, Dict, Tuple

# Thai consonants mapping to IPA
THAI_CONSONANTS_IPA = {
    'ก': 'k',
    'ข': 'kʰ',
    'ฃ': 'kʰ',
    'ค': 'kʰ',
    'ฅ': 'kʰ',
    'ฆ': 'kʰ',
    'ง': 'ŋ',
    'จ': 'tɕ',
    'ฉ': 'tɕʰ',
    'ช': 'tɕʰ',
    'ซ': 's',
    'ฌ': 'tɕʰ',
    'ญ': 'j',
    'ฎ': 'd',
    'ฏ': 't',
    'ฐ': 'tʰ',
    'ฑ': 'tʰ',
    'ฒ': 'tʰ',
    'ณ': 'n',
    'ด': 'd',
    'ต': 't',
    'ถ': 'tʰ',
    'ท': 'tʰ',
    'ธ': 'tʰ',
    'น': 'n',
    'บ': 'b',
    'ป': 'p',
    'ผ': 'pʰ',
    'ฝ': 'f',
    'พ': 'pʰ',
    'ฟ': 'f',
    'ภ': 'pʰ',
    'ม': 'm',
    'ย': 'j',
    'ร': 'r',
    'ฤ': 'rɯ',
    'ล': 'l',
    'ฦ': 'lɯ',
    'ว': 'w',
    'ศ': 's',
    'ษ': 's',
    'ส': 's',
    'ห': 'h',
    'ฬ': 'l',
    'อ': 'ʔ',
    'ฮ': 'h'
}

# Thai vowels mapping
THAI_VOWELS_IPA = {
    'ะ': 'a',
    'า': 'aː',
    'ิ': 'i',
    'ี': 'iː',
    'ึ': 'ɯ',
    'ื': 'ɯː',
    'ุ': 'u',
    'ู': 'uː',
    'เ': 'e',
    'แ': 'ɛ',
    'โ': 'o',
    'ใ': 'aj',
    'ไ': 'aj',
    'ๅ': 'ɯː',
    'ฤ': 'rɯ'
}

# Thai tone markers
THAI_TONES = {
    '่': '˩',  # low tone
    '้': '˥',  # high tone
    '๊': '˥',  # high tone
    '๋': '˧'   # mid tone
}

# Thai final consonants mapping
THAI_FINAL_CONSONANTS = {
    'ก': 'k',
    'ข': 'k',
    'ค': 'k',
    'ฆ': 'k',
    'ง': 'ŋ',
    'จ': 't',
    'ช': 't',
    'ซ': 't',
    'ฌ': 't',
    'ญ': 'n',
    'ฎ': 't',
    'ฏ': 't',
    'ฐ': 't',
    'ฑ': 't',
    'ฒ': 't',
    'ณ': 'n',
    'ด': 't',
    'ต': 't',
    'ถ': 't',
    'ท': 't',
    'ธ': 't',
    'น': 'n',
    'บ': 'p',
    'ป': 'p',
    'ผ': 'p',
    'พ': 'p',
    'ฟ': 'p',
    'ภ': 'p',
    'ม': 'm',
    'ย': 'j',
    'ร': 'n',
    'ฤ': 'n',
    'ล': 'n',
    'ฦ': 'n',
    'ว': 'w',
    'ศ': 't',
    'ษ': 't',
    'ส': 't',
    'ห': 'h',
    'ฬ': 'n',
    'อ': 'ʔ',
    'ฮ': 'h'
}

# Thai vowel combinations
THAI_VOWEL_COMBINATIONS = {
    'เอะ': 'e',
    'เอ': 'eː',
    'แอะ': 'ɛ',
    'แอ': 'ɛː',
    'โอะ': 'o',
    'โอ': 'oː',
    'อะ': 'a',
    'อา': 'aː',
    'เอาะ': 'ɔ',
    'ออ': 'ɔː',
    'เออะ': 'ɤ',
    'เออ': 'ɤː',
    'เอียะ': 'ia',
    'เอีย': 'iaː',
    'เอือะ': 'ɯa',
    'เอือ': 'ɯaː',
    'อัวะ': 'ua',
    'อัว': 'uaː'
}

class ThaiPhonemeMapper:
    """Map Thai text to phonetic transcription."""
    
    def __init__(self):
        self.consonants = THAI_CONSONANTS_IPA
        self.vowels = THAI_VOWELS_IPA
        self.tones = THAI_TONES
        self.final_consonants = THAI_FINAL_CONSONANTS
        self.vowel_combinations = THAI_VOWEL_COMBINATIONS
    
    def is_thai_consonant(self, char: str) -> bool:
        """Check if character is a Thai consonant."""
        return 'ก' <= char <= 'ฮ'
    
    def is_thai_vowel(self, char: str) -> bool:
        """Check if character is a Thai vowel."""
        return ('ะ' <= char <= 'ู') or char in ['เ', 'แ', 'โ', 'ใ', 'ไ']
    
    def is_thai_tone(self, char: str) -> bool:
        """Check if character is a Thai tone marker."""
        return char in self.tones
    
    def split_syllable(self, text: str) -> List[str]:
        """Split Thai text into syllables."""
        syllables = []
        current_syllable = ''
        
        for char in text:
            if self.is_thai_consonant(char):
                if current_syllable and self.is_thai_consonant(current_syllable[-1]):
                    # New syllable starts
                    syllables.append(current_syllable)
                    current_syllable = char
                else:
                    current_syllable += char
            elif self.is_thai_vowel(char) or self.is_thai_tone(char):
                current_syllable += char
            else:
                if current_syllable:
                    syllables.append(current_syllable)
                    current_syllable = ''
                syllables.append(char)
        
        if current_syllable:
            syllables.append(current_syllable)
        
        return syllables
    
    def consonant_to_ipa(self, consonant: str, final: bool = False) -> str:
        """Convert Thai consonant to IPA."""
        if final and consonant in self.final_consonants:
            return self.final_consonants[consonant]
        elif consonant in self.consonants:
            return self.consonants[consonant]
        else:
            return consonant
    
    def vowel_to_ipa(self, vowel: str) -> str:
        """Convert Thai vowel to IPA."""
        if vowel in self.vowel_combinations:
            return self.vowel_combinations[vowel]
        elif vowel in self.vowels:
            return self.vowels[vowel]
        else:
            return vowel
    
    def tone_to_ipa(self, tone: str) -> str:
        """Convert Thai tone marker to IPA."""
        return self.tones.get(tone, '')
    
    def syllable_to_phonemes(self, syllable: str) -> str:
        """Convert a Thai syllable to phonemes."""
        if not syllable:
            return ''
        
        phonemes = []
        tone = ''
        
        # Extract tone
        for char in syllable:
            if self.is_thai_tone(char):
                tone = self.tone_to_ipa(char)
                syllable = syllable.replace(char, '')
        
        # Find initial consonant
        initial_consonant = ''
        for char in syllable:
            if self.is_thai_consonant(char):
                initial_consonant = char
                break
        
        if initial_consonant:
            phonemes.append(self.consonant_to_ipa(initial_consonant))
        
        # Find vowel
        vowel_part = syllable.replace(initial_consonant, '')
        if vowel_part:
            # Check for vowel combinations first
            found_vowel = False
            for combo, ipa in self.vowel_combinations.items():
                if combo in vowel_part:
                    phonemes.append(ipa)
                    vowel_part = vowel_part.replace(combo, '')
                    found_vowel = True
                    break
            
            if not found_vowel:
                # Process individual vowels
                for char in vowel_part:
                    if self.is_thai_vowel(char):
                        phonemes.append(self.vowel_to_ipa(char))
        
        # Find final consonant
        if vowel_part:
            for char in reversed(vowel_part):
                if self.is_thai_consonant(char):
                    phonemes.append(self.consonant_to_ipa(char, final=True))
                    break
        
        # Add tone
        if tone:
            phonemes.append(tone)
        
        return ''.join(phonemes)
    
    def text_to_phonemes(self, text: str) -> str:
        """Convert Thai text to phonemes."""
        if not text:
            return ''
        
        syllables = self.split_syllable(text)
        phonemes = []
        
        for syllable in syllables:
            if self.is_thai_consonant(syllable[0]) if syllable else False:
                phonemes.append(self.syllable_to_phonemes(syllable))
            else:
                phonemes.append(syllable)
        
        return ' '.join(phonemes)

def thai_to_phonemes(text: str) -> str:
    """
    Convert Thai text to phonetic transcription.
    
    Args:
        text (str): Thai text to convert
        
    Returns:
        str: Phonetic transcription
    """
    mapper = ThaiPhonemeMapper()
    return mapper.text_to_phonemes(text)