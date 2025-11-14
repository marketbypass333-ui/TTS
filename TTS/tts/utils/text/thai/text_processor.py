"""Main Thai text processor for TTS."""

import re
from typing import List, Dict, Optional

from .cleaners import thai_cleaners, basic_thai_cleaners, validate_thai_text
from .numbers import normalize_numbers
from .phonemes import thai_to_phonemes

class ThaiTextProcessor:
    """Main processor for Thai text in TTS pipeline."""
    
    def __init__(self, 
                 use_phonemes: bool = True,
                 use_cleaners: bool = True,
                 use_number_normalization: bool = True):
        """
        Initialize Thai text processor.
        
        Args:
            use_phonemes: Convert text to phonetic transcription
            use_cleaners: Apply text cleaning
            use_number_normalization: Normalize numbers to words
        """
        self.use_phonemes = use_phonemes
        self.use_cleaners = use_cleaners
        self.use_number_normalization = use_number_normalization
        
        # Thai character ranges
        self.thai_chars = r'[฀-๿]'
        self.thai_consonants = r'[ก-ฮ]'
        self.thai_vowels = r'[ะ-ฺเ-ๆ]'
    
    def is_thai_text(self, text: str) -> bool:
        """Check if text contains Thai characters."""
        return bool(re.search(self.thai_chars, text))
    
    def validate_input(self, text: str) -> bool:
        """Validate input text."""
        if not text or not isinstance(text, str):
            return False
        
        if not text.strip():
            return False
        
        # If text contains Thai characters, validate Thai structure
        if self.is_thai_text(text):
            return validate_thai_text(text)
        
        return True
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for TTS.
        
        Args:
            text: Input text
            
        Returns:
            Processed text ready for TTS
        """
        if not self.validate_input(text):
            raise ValueError("Invalid input text")
        
        # Step 1: Text cleaning
        if self.use_cleaners:
            text = thai_cleaners(text)
        else:
            text = basic_thai_cleaners(text)
        
        # Step 2: Number normalization
        if self.use_number_normalization:
            text = normalize_numbers(text)
        
        # Step 3: Phoneme conversion
        if self.use_phonemes and self.is_thai_text(text):
            text = thai_to_phonemes(text)
        
        return text.strip()
    
    def split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Thai sentence ending patterns
        sentence_endings = r'[.!?]\s*'
        sentences = re.split(sentence_endings, text)
        
        # Clean up sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def extract_thai_words(self, text: str) -> List[str]:
        """Extract individual Thai words from text."""
        # Simple word segmentation based on spaces and Thai word boundaries
        words = re.findall(r'[^\s]+', text)
        return words
    
    def get_text_statistics(self, text: str) -> Dict:
        """Get statistics about the text."""
        stats = {
            'total_chars': len(text),
            'thai_chars': len(re.findall(self.thai_chars, text)),
            'thai_consonants': len(re.findall(self.thai_consonants, text)),
            'thai_vowels': len(re.findall(self.thai_vowels, text)),
            'words': len(self.extract_thai_words(text)),
            'sentences': len(self.split_sentences(text)),
            'has_thai': self.is_thai_text(text)
        }
        
        return stats
    
    def process_batch(self, texts: List[str]) -> List[str]:
        """Process multiple texts in batch."""
        processed_texts = []
        
        for text in texts:
            try:
                processed_text = self.preprocess_text(text)
                processed_texts.append(processed_text)
            except Exception as e:
                # Log error and skip this text
                print(f"Error processing text: {text[:50]}... Error: {str(e)}")
                processed_texts.append("")
        
        return processed_texts
    
    def get_supported_features(self) -> Dict:
        """Get supported features of this processor."""
        return {
            'language': 'thai',
            'phoneme_support': self.use_phonemes,
            'cleaning_support': self.use_cleaners,
            'number_normalization': self.use_number_normalization,
            'batch_processing': True,
            'sentence_splitting': True
        }

# Convenience functions
def process_thai_text(text: str, 
                   use_phonemes: bool = True,
                   use_cleaners: bool = True,
                   use_number_normalization: bool = True) -> str:
    """
    Process Thai text for TTS.
    
    Args:
        text: Input Thai text
        use_phonemes: Convert to phonetic transcription
        use_cleaners: Apply text cleaning
        use_number_normalization: Normalize numbers
        
    Returns:
        Processed text ready for TTS
    """
    processor = ThaiTextProcessor(
        use_phonemes=use_phonemes,
        use_cleaners=use_cleaners,
        use_number_normalization=use_number_normalization
    )
    return processor.preprocess_text(text)

def thai_text_to_phonemes(text: str) -> str:
    """
    Convert Thai text directly to phonemes.
    
    Args:
        text: Input Thai text
        
    Returns:
        Phonetic transcription
    """
    processor = ThaiTextProcessor(use_phonemes=True, use_cleaners=False, use_number_normalization=False)
    return processor.preprocess_text(text)