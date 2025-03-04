import re
from num2words import num2words
def detect_language(text):
    """Detect if text is primarily Arabic or English based on character presence."""
    arabic_chars = re.search(r'[\u0600-\u06FF]', text)  # Arabic Unicode Range
    return 'ar' if arabic_chars else 'en'

def replace_numbers_with_words(text):
    """Replace numbers in text with words based on detected language (Arabic or English)."""
    lang = detect_language(text)  # Detect language
    return re.sub(r'\d+', lambda x: num2words(int(x.group()), lang=lang), text)

# Test Arabic Sentence
sentence_ar = "لدي 3 تفاحات و 2830 برتقالة."
converted_ar = replace_numbers_with_words(sentence_ar)
print(converted_ar)  
# Output: لدي ثلاث تفاحات وألفان وثمانمائة وثلاثون برتقالة.
# Test English Sentence
sentence_en = "I have 3 apples and 2830 oranges."
converted_en = replace_numbers_with_words(sentence_en)
print(converted_en)  
# Output: I have three apples and two thousand, eight hundred and thirty oranges.