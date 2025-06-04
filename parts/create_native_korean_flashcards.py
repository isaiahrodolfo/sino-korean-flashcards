import pickle
import os
import csv

from helpers.korean_dict import get_anki_fields
from helpers.dedup import dedup
from helpers.get_unseen_frequencies import get_unseen_frequencies

from datastructures.word_entry import WordEntry

## PART 2: Native Korean words into flashcards format
def create_native_korean_flashcards(freq_dict, seen_frequencies):

  # Try to load previous progress
  if os.path.exists("pickle-output/final_native_korean_dict.pkl"):
    with open("pickle-output/final_native_korean_dict.pkl", "rb") as f:
      final_native_korean_dict: dict[str, WordEntry] = pickle.load(f)
  else:
    final_native_korean_dict: dict[str, WordEntry] = {}

  # Load or compute unseen frequencies
  if os.path.exists("pickle-output/unseen_freqs.pkl"):
    with open("pickle-output/unseen_freqs.pkl", "rb") as f:
      unseen_freqs: list[int] = pickle.load(f)
  else:
    unseen_freqs = get_unseen_frequencies(freq_dict, seen_frequencies)
    with open("pickle-output/unseen_freqs.pkl", "wb") as f:
      pickle.dump(unseen_freqs, f)
  print(unseen_freqs)

  LEN_UNSEEN_FREQUENCIES = len(unseen_freqs)

  # Add each word to Anki list (Sino-Korean word list)
  for index, frequency in enumerate(unseen_freqs):
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

    print(word, dedup(english_translations))

    current_index = index + 1
    print(word + " (" + str(current_index) + " / " + str(LEN_UNSEEN_FREQUENCIES) + ")")

    final_native_korean_dict[word] = word_entry

    with open("pickle-output/final_native_korean_dict.pkl", "wb") as f:
        pickle.dump(final_native_korean_dict, f)

  # Convert final_native_korean_dict to csv
  with open("flashcards-output/final_native_korean_dict.csv", "w", newline="", encoding="utf-8-sig") as csvfile:
    fieldnames = ["word", "hanja", "pronunciation", "english_translations", "korean_definitions", "part_of_speech", "frequency"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for entry in final_native_korean_dict.values():
      writer.writerow({
        "word": entry["word"],
        "hanja": entry["hanja"],
        "pronunciation": entry["pronunciation"],
        "english_translations": "; ".join(entry["english_translations"]),
        "korean_definitions": " ".join(entry["korean_definitions"]),
        "part_of_speech": entry["part_of_speech"],
        "frequency": entry["frequency"],
      })

  with open("pickle-output/unseen_freqs.pkl", "wb") as f:
    pickle.dump(unseen_freqs, f)
  print("save unseen freqs")
