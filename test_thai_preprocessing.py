#!/usr/bin/env python3
"""
Test script for Thai text preprocessing functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from TTS.tts.utils.text.thai.text_processor import ThaiTextProcessor, process_thai_text
from TTS.tts.utils.text.thai.cleaners import thai_cleaners, basic_thai_cleaners
from TTS.tts.utils.text.thai.numbers import normalize_numbers
from TTS.tts.utils.text.thai.phonemes import thai_to_phonemes

def test_thai_cleaners():
    """Test Thai text cleaners."""
    print("=== Testing Thai Cleaners ===")
    
    test_cases = [
        "สวัสดีครับทุกคน",
        "กทม เป็นเมืองหลวงของประเทศไทย",
        "รพ สงขลา เปิดให้บริการ 24 ชม",
        "ราคา 150 บาท",
        "วันที่ 15/07/2024",
        "เวลา 14:30 นาที"
    ]
    
    print("Full cleaners:")
    for text in test_cases:
        cleaned = thai_cleaners(text)
        print(f"Input:  {text}")
        print(f"Output: {cleaned}")
        print()
    
    print("Basic cleaners:")
    for text in test_cases:
        cleaned = basic_thai_cleaners(text)
        print(f"Input:  {text}")
        print(f"Output: {cleaned}")
        print()

def test_thai_numbers():
    """Test Thai number normalization."""
    print("=== Testing Thai Number Normalization ===")
    
    test_cases = [
        "๑๒๓",
        "150 บาท",
        "เวลา 14:30",
        "วันที่ 15/07/2024",
        "โทร 081-234-5678",
        "หนึ่งสองสาม"
    ]
    
    for text in test_cases:
        normalized = normalize_numbers(text)
        print(f"Input:  {text}")
        print(f"Output: {normalized}")
        print()

def test_thai_phonemes():
    """Test Thai phoneme conversion."""
    print("=== Testing Thai Phoneme Conversion ===")
    
    test_cases = [
        "กา",
        "ข้าว",
        "น้ำ",
        "สวัสดี",
        "กรุงเทพ"
    ]
    
    for text in test_cases:
        phonemes = thai_to_phonemes(text)
        print(f"Input:  {text}")
        print(f"Output: {phonemes}")
        print()

def test_text_processor():
    """Test the main text processor."""
    print("=== Testing Thai Text Processor ===")
    
    processor = ThaiTextProcessor(
        use_phonemes=True,
        use_cleaners=True,
        use_number_normalization=True
    )
    
    test_cases = [
        "สวัสดีครับ ผมชื่อสมชาย",
        "ราคา 250 บาท",
        "กทม เป็นเมืองหลวง",
        "วันนี้วันที่ 15 กรกฎาคม 2567"
    ]
    
    for text in test_cases:
        processed = processor.preprocess_text(text)
        stats = processor.get_text_statistics(text)
        print(f"Input:  {text}")
        print(f"Output: {processed}")
        print(f"Stats:  {stats}")
        print()

def test_with_metadata():
    """Test with sample data from metadata.csv."""
    print("=== Testing with Metadata Samples ===")
    
    processor = ThaiTextProcessor()
    
    # Sample texts from metadata.csv
    sample_texts = [
        "สวัสดีครับทุกคน ยินดีที่ได้พบกันอีกครั้ง",
        "วันนี้เป็นวันที่สวยงามมาก",
        "ฉันขอบคุณสำหรับความช่วยเหลือของคุณ",
        "เราควรทำงานร่วมกันเพื่ออนาคตที่ดีกว่า"
    ]
    
    for text in sample_texts:
        try:
            processed = processor.preprocess_text(text)
            print(f"Original: {text}")
            print(f"Processed: {processed}")
            print()
        except Exception as e:
            print(f"Error processing '{text}': {e}")
            print()

def main():
    """Run all tests."""
    print("Thai Text Preprocessing Test Suite")
    print("=" * 40)
    
    try:
        test_thai_cleaners()
        print("\n" + "=" * 40 + "\n")
        
        test_thai_numbers()
        print("\n" + "=" * 40 + "\n")
        
        test_thai_phonemes()
        print("\n" + "=" * 40 + "\n")
        
        test_text_processor()
        print("\n" + "=" * 40 + "\n")
        
        test_with_metadata()
        print("\n" + "=" * 40 + "\n")
        
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()