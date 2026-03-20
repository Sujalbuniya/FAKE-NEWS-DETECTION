from langdetect import detect
from googletrans import Translator

# Translator object banayein
translator = Translator()

def detect_language(text):
    """
    Detect input text ki language
    Returns: language code (e.g., 'hi', 'es', 'en') ya 'unknown'
    """
    try:
        lang = detect(text)
        return lang
    except:
        return 'unknown'

def translate_to_english(text):
    """
    Agar text Hindi/Spanish etc. hai toh English mein translate karo
    Returns: (translated_text, original_language)
    """
    try:
        # Pehle language detect karo
        lang = detect_language(text)
        
        # Agar English nahi hai toh translate karo
        if lang != 'en' and lang != 'unknown':
            print(f"🌐 {lang} language detected. Translating to English...")
            translated = translator.translate(text, dest='en')
            return translated.text, lang
        else:
            # Already English hai
            return text, 'en'
            
    except Exception as e:
        print(f"❌ Translation error: {e}")
        return text, 'unknown'

# Test ke liye code
if __name__ == "__main__":
    print("="*50)
    print("🌐 TRANSLATOR TEST")
    print("="*50)
    
    # Test 1: Hindi text
    hindi_text = "भारत ने विश्व कप जीत लिया"
    print(f"\n📝 Original: {hindi_text}")
    translated, lang = translate_to_english(hindi_text)
    print(f"🔍 Detected: {lang}")
    print(f"✅ Translated: {translated}")
    
    # Test 2: Spanish text
    spanish_text = "India ganó la copa del mundo"
    print(f"\n📝 Original: {spanish_text}")
    translated, lang = translate_to_english(spanish_text)
    print(f"🔍 Detected: {lang}")
    print(f"✅ Translated: {translated}")
    
    # Test 3: English text
    english_text = "India won the world cup"
    print(f"\n📝 Original: {english_text}")
    translated, lang = translate_to_english(english_text)
    print(f"🔍 Detected: {lang}")
    print(f"✅ Translated: {translated}")
    
    print("\n" + "="*50)
    print("✅ TEST COMPLETE")
    print("="*50)