######################## TELEGRAM BOT TOKEN ########################
BOT_TOKEN = ""

######################## ELEVEN_API_KEY ########################
ELEVEN_API_KEY=""

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

