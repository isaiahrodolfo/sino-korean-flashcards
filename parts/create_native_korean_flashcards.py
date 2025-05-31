import pickle
import os
import csv

from helpers.korean_dict import get_anki_fields
from helpers.dedup import dedup

from datastructures.word_entry import WordEntry

## PART 2: Native Korean words into flashcards format
def create_native_korean_flashcards(freq_dict, seen_frequencies):

  # Try to load previous progress
  if os.path.exists("pickle-output/final_native_korean_dict.pkl"):
    with open("pickle-output/final_native_korean_dict.pkl", "rb") as f:
      final_native_korean_dict: dict[str, WordEntry] = pickle.load(f)
  else:
    final_native_korean_dict: dict[str, WordEntry] = {}

  # Get all frequencies
  all_freqs = set(range(len(freq_dict)))
  print(all_freqs)
  # Take the difference of the sets
  unseen = all_freqs - seen_frequencies
  print(unseen)
  # Convert back to sorted list
  unseen_list = sorted(unseen)
  print(unseen_list)

  LEN_UNSEEN_FREQUENCIES = len(unseen_list)

  # Add each word to Anki list (Sino-Korean word list)
  for index, frequency in enumerate(unseen_list):
    # Skip if already processed
    word = freq_dict[frequency]
    if word in final_native_korean_dict:
      # print(f"Skipping already-processed {word}")
      continue

    _, _, _, pronunciation, part_of_speech, korean_definitions, english_translations = get_anki_fields(word, True)

    word_entry = {
      "word": word,
      "hanja": "",
      "pronunciation": pronunciation,
      "english_translations": dedup(english_translations),
      "korean_definitions": dedup(korean_definitions),
      "part_of_speech": part_of_speech,
      "frequency": frequency
    }

    print(word_entry)

    current_index = index + 1
    print(word + " (" + str(current_index) + " / " + str(LEN_UNSEEN_FREQUENCIES) + ")")

    final_native_korean_dict[word] = word_entry

    with open("pickle-output/final_native_korean_dict.pkl", "wb") as f:
        pickle.dump(final_native_korean_dict, f)

  # Convert final_native_korean_dict to csv
  with open("final_native_korean_dict.csv", "w", newline="", encoding="utf-8-sig") as csvfile:
    fieldnames = ["word", "hanja", "pronunciation", "english_translations", "korean_definitions", "part_of_speech", "frequency"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for entry in final_native_korean_dict.values():
      writer.writerow({
        "word": entry["word"],
        "hanja": entry["hanja"],
        "pronunciation": entry["pronunciation"],
        "english_translations": "; ".join(entry["english_translations"]),
        "korean_definitions": "; ".join(entry["korean_definitions"]),
        "part_of_speech": entry["part_of_speech"],
        "frequency": entry["frequency"],
      })
