######################## TELEGRAM BOT TOKEN ########################
BOT_TOKEN = "7012939808:AAH9QNLi05Sm4FfqTjv7JF-QBJpkimHhVak"

######################## FEEDBACK MAPS ########################
feedback_map = {
    'very long' : 'Very long, Make answer shorter',
    'very short': 'Very short, Make answer very detailed in more lines',
    'inaccurate': 'You are not correct',
    'irrelevant': 'Irrelevant, Please focus on my question or write an answer related to my question'
}

######################## ARABIC PRINTING SUPPORT ########################
import arabic_reshaper
from bidi.algorithm import get_display

def print_ar(text):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    print(bidi_text)

######################## TRANSLATION LAYER ########################
from deep_translator import GoogleTranslator

def translate_ar_to_en(text: str) -> str:
    return GoogleTranslator(source='ar', target='en').translate(text)

def translate_en_to_ar(text: str) -> str:
    return GoogleTranslator(source='en', target='ar').translate(text)
