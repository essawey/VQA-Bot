# ######################## TRANSLATION LAYER ########################

# Import for the translation task
from deep_translator import GoogleTranslator
from pprint import pprint

# Import for the language detection task
from mediapipe.tasks import python
from mediapipe.tasks.python import text

# Dictionary to store the translations
translations = {}

def fromEN(UserLanguage: str, text: str) -> str:
    translation_key = (UserLanguage, text)
    if translation_key in translations:
        return translations[translation_key]
    else:
        translation = GoogleTranslator(source='en', target=UserLanguage).translate(text)
        translations[translation_key] = translation
        return translation

def ToEN(UserLanguage: str, text: str) -> str:

    for (lang, english_text), translation in translations.items():
        if lang == UserLanguage and translation == text:
            return english_text
    else:
        return GoogleTranslator(source=UserLanguage, target='en').translate(text)


def UserLanguage(userText: str) -> str:

    # Create a LanguageDetector object
    base_options = python.BaseOptions(model_asset_path="language_detector.tflite")
    options = text.LanguageDetectorOptions(base_options=base_options)
    detector = text.LanguageDetector.create_from_options(options)

    # Get the language detection result for the input text
    detection_result = detector.detect(userText)

    return detection_result.detections[0].language_code


# # Get the supported languages
# from pprint import pprint
# pprint(GoogleTranslator().get_supported_languages(as_dict=True))
