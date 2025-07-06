import os
from dotenv import load_dotenv

import requests
import xml.etree.ElementTree as ET

from helpers.network.safe_get import safe_get

load_dotenv()
API_KEY = os.getenv("KRDICT_API_KEY")

def get_hangul(hanja):
  base_url = "https://krdict.korean.go.kr/api/search"
  params = {
    'key': API_KEY,
    'type_search': 'search',
    'q': hanja,
    'sort': 'dict'
  }
  
  response = safe_get(base_url, params)
  if response.status_code != 200:
    print(f"Error: {response.status_code}")
    return ""

  root = ET.fromstring(response.content)
  
  # Get field
  for item in root.findall('.//item'):
    origin = item.find('origin').text
    if origin == hanja: # Make sure origin of word matches the dictionary entry
      return item.find('word').text, response.content

def get_word_grade(hanja):
  base_url = "https://krdict.korean.go.kr/api/search"
  params = {
    'key': API_KEY,
    'type_search': 'search',
    'q': hanja,
    'start': 1,
    'sort': 'dict',
    'method': 'exact'
  }
  
  response = requests.get(base_url, params=params)
  if response.status_code != 200:
    print(f"Error: {response.status_code}")
    return ""

  root = ET.fromstring(response.content)
  
  # Get field
  for item in root.findall('.//item'):
    origin = item.find('origin')
    grade = item.find('word_grade')

    if origin is not None and origin.text == hanja:  # Make sure origin of word matches the dictionary entry
      if grade is not None and grade.text is not None:
        return grade.text
      else:
        return "unknown"  # default grade
      
def get_anki_fields(hanja, is_native_korean: bool):
  base_url = "https://krdict.korean.go.kr/api/search"

  # Get word, grade, pronunciation, part of speech, Korean definition
  params = {
    'key': API_KEY,
    'type_search': 'search',
    'q': hanja,
    'start': 1,
    'sort': 'dict',
    'method': 'exact',
  }
  
  response = requests.get(base_url, params=params)
  if response.status_code != 200:
    print(f"Error: {response.status_code}")
    return ""

  root = ET.fromstring(response.content)

  with open("output/example-default.txt", "w") as file:
    file.write(response.content.decode("utf-8"))

  korean_definitions = []
  origin_text, word_text, grade_text, pronunciation_text, part_of_speech_text = "", "", "", "", ""
  
  for item in root.findall('.//item'):
    if is_native_korean is False:
      origin = item.find('origin')
    word = item.find('word')
    grade = item.find('word_grade')
    pronunciation = item.find('pronunciation')
    part_of_speech = item.find('pos')
    
    if (is_native_korean is True) or (origin is not None and origin.text == hanja):  # Make sure origin of word matches the dictionary entry
      if is_native_korean is False:
        origin_text = origin.text
      word_text = word.text if word is not None and word.text is not None else None
      grade_text = grade.text if grade is not None and grade.text is not None else None
      pronunciation_text = pronunciation.text if pronunciation is not None and pronunciation.text is not None else None
      part_of_speech_text = part_of_speech.text if part_of_speech is not None and part_of_speech.text is not None else None
      break  # Stop after first match
      
  for sense in root.findall(".//sense"):
    definition = sense.find("definition")
    if definition is not None:
      korean_definitions.append(definition.text.strip())

  # Get English translation
  params = {
    'key': API_KEY,
    'type_search': 'search',
    'q': hanja,
    'start': 1,
    'sort': 'dict',
    'method': 'exact',
    'translated': 'y',
    'trans_lang': 1,
  }
  
  response = requests.get(base_url, params=params)
  if response.status_code != 200:
    print(f"Error: {response.status_code}")
    return ""
  
  root = ET.fromstring(response.content)

  with open("output/example-advanced.txt", "w") as file:
    file.write(response.content.decode("utf-8"))

  english_translations = []

  for sense in root.findall(".//sense"):
    for sense in root.findall(".//translation"):
      trans_word = sense.find("trans_word")
      if trans_word is not None and trans_word.text is not None:
        english_translations.append(trans_word.text.strip())

  return origin_text, word_text, grade_text, pronunciation_text, part_of_speech_text, korean_definitions, english_translations

# print(get_anki_fields("是認"))  ## TESTING