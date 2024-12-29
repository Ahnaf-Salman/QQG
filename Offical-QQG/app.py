from flask import Flask, render_template, request
import requests
import random
import re

app = Flask(__name__)

surah_verses = {
    1: 7, 2: 286, 3: 200, 4: 176, 5: 120, 6: 165, 7: 206, 8: 75, 9: 129, 10: 109,
    11: 123, 12: 111, 13: 43, 14: 52, 15: 99, 16: 128, 17: 111, 18: 110, 19: 98, 20: 135,
    21: 112, 22: 78, 23: 118, 24: 64, 25: 77, 26: 227, 27: 93, 28: 88, 29: 69, 30: 60,
    31: 34, 32: 30, 33: 73, 34: 54, 35: 45, 36: 83, 37: 182, 38: 88, 39: 75, 40: 85,
    41: 54, 42: 53, 43: 89, 44: 59, 45: 37, 46: 35, 47: 38, 48: 29, 49: 18, 50: 45,
    51: 60, 52: 49, 53: 62, 54: 55, 55: 78, 56: 96, 57: 29, 58: 22, 59: 24, 60: 13,
    61: 14, 62: 11, 63: 11, 64: 18, 65: 12, 66: 12, 67: 30, 68: 52, 69: 52, 70: 44,
    71: 28, 72: 28, 73: 20, 74: 56, 75: 40, 76: 31, 77: 50, 78: 40, 79: 46, 80: 42,
    81: 29, 82: 19, 83: 36, 84: 25, 85: 22, 86: 17, 87: 19, 88: 26, 89: 30, 90: 20,
    91: 15, 92: 21, 93: 11, 94: 8, 95: 8, 96: 19, 97: 5, 98: 8, 99: 8, 100: 11,
    101: 11, 102: 8, 103: 3, 104: 9, 105: 5, 106: 4, 107: 7, 108: 3, 109: 6, 110: 3,
    111: 5, 112: 4, 113: 5, 114: 6
}

used_verses = set()

def get_unused_verse():
    global used_verses
    
    total_possible_verses = sum(1 for surah, total_verses in surah_verses.items() 
                              for verse in range(1, total_verses + 1))
    
    if len(used_verses) >= total_possible_verses:
        used_verses.clear()
    
    while True:
        surah_number = random.randint(1, 114)
        verse_number = random.randint(1, surah_verses[surah_number])
        
        verse_key = f"{surah_number}:{verse_number}"
        if verse_key not in used_verses:
            used_verses.add(verse_key)
            return surah_number, verse_number

def get_quran_verse():
    surah_number, ayah_number = get_unused_verse()

    base_url = "https://api.quran.com/api/v4"
    
    verse_url = f"{base_url}/verses/by_key/{surah_number}:{ayah_number}"
    params = {
        "language": "en",
        "words": True,
        "translations": "131",
        "fields": "text_uthmani,verse_key"
    }
    
    response = requests.get(verse_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        verse_data = data.get('verse', {})
        
        arabic_verse = verse_data.get('text_uthmani', 'No verse found in Arabic')
        
        translations = verse_data.get('translations', [])
        translation = translations[0].get('text', 'No translation available') if translations else 'No translation available'
        
        translation = re.sub(r'<sup.*?</sup>', '', translation)
        translation = re.sub(r'\[.*?\]', '', translation)
        translation = re.sub(r'\s+', ' ', translation).strip()
        
        surah_url = f"{base_url}/chapters/{surah_number}"
        surah_response = requests.get(surah_url)
        surah_data = surah_response.json() if surah_response.status_code == 200 else {}
        surah_name = surah_data.get('chapter', {}).get('name_simple', 'No surah name found')
        
        return arabic_verse, surah_name, ayah_number, translation
    else:
        return 'No verse found', 'N/A', 'N/A', 'Translation not available'


@app.route('/')
def home():
    arabic_verse, surah_name, ayah_number, translation = get_quran_verse()
    return render_template('quote_template.html', arabic_verse=arabic_verse, 
                           surah_name=surah_name, ayah_number=ayah_number,
                           translation=translation)


if __name__ == '__main__':
    app.run(debug=True)
