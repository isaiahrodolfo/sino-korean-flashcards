import pickle
import os
import csv

from helpers.korean_dict import get_anki_fields
from helpers.dedup import dedup

from datastructures.word_entry import WordEntry

## PART 3: Sino-Korean into flashcards format
def create_sino_korean_flashcards(seen_words, word_groups_by_avg_freq, freq_dict):
  # Try to load previous progress
  if os.path.exists("pickle-output/final_sino_korean_dict.pkl"):
    with open("pickle-output/final_sino_korean_dict.pkl", "rb") as f:
      final_sino_korean_dict: dict[str, WordEntry] = pickle.load(f)
  else:
    final_sino_korean_dict: dict[str, WordEntry] = {}
    
  LEN_SEEN_WORDS = len(seen_words)

  # Add each word to Anki list (Sino-Korean word list)
  for index_word, list_of_words in enumerate(word_groups_by_avg_freq):
    for hanja_hangul_word in list_of_words[0]:
      # Skip if already processed
      hanja_word = hanja_hangul_word[0]
      if hanja_word in final_sino_korean_dict:
        # print(f"Skipping already-processed {hanja_word}")
        continue
      
      print(hanja_hangul_word)
      
      hanja_word = hanja_hangul_word[0]
      hangul_word = hanja_hangul_word[1]

      _, _, _, pronunciation, part_of_speech, korean_definitions, english_translations = get_anki_fields(hanja_word, False)

      word_entry = {
        "word": hangul_word,
        "hanja": hanja_word,
        "pronunciation": pronunciation,
        "english_translations": dedup(english_translations),
        "korean_definitions": dedup(korean_definitions),
        "part_of_speech": part_of_speech,
        "frequency": freq_dict.index(hangul_word)
      }

      current_index = index_word + 1
      print(hanja_word + " (" + str(current_index) + " / " + str(LEN_SEEN_WORDS) + ")")
      # ? Add Traditional, Simplified Chinese and Korean versions of hanja, no matter if they differ (but add a "different hanja?" field)

      final_sino_korean_dict[hanja_word] = word_entry

      with open("pickle-output/final_sino_korean_dict.pkl", "wb") as f:
        pickle.dump(final_sino_korean_dict, f)

  # Convert final_sino_korean_dict to csv
  with open("final_sino_korean_dict.csv", "w", newline="", encoding="utf-8-sig") as csvfile:
    fieldnames = ["word", "hanja", "pronunciation", "english_translations", "korean_definitions", "part_of_speech", "frequency"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for entry in final_sino_korean_dict.values():
      writer.writerow({
        "word": entry["word"],
        "hanja": entry["hanja"],
        "pronunciation": entry["pronunciation"],
        "english_translations": "; ".join(entry["english_translations"]),
        "korean_definitions": "; ".join(entry["korean_definitions"]),
        "part_of_speech": entry["part_of_speech"],
        "frequency": entry["frequency"],
      })