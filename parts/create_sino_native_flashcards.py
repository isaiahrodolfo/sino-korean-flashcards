import pickle
import os
import csv

from helpers.korean_dict import get_anki_fields
from helpers.dedup import dedup

from datastructures.word_entry import WordEntry

# Try to load previous progress
if os.path.exists("pickle-output/final_sino_native_dict.pkl"):
  with open("pickle-output/final_sino_native_dict.pkl", "rb") as f:
    final_sino_native_list: list[WordEntry] = pickle.load(f)
else:
  final_sino_native_list: list[WordEntry] = []

def create_sino_native_flashcards(freq_dict, unseen_freqs, word_groups_by_avg_freq):

  u_index, w_index = 0, 0
  hangul, hanja = "", ""
  is_native_word = False
  num_total_groups = len(unseen_freqs) + len(word_groups_by_avg_freq)

  # Continually add smaller frequency number between the lowest of sino and native lists
  while u_index < len(unseen_freqs) or w_index < len(word_groups_by_avg_freq): 

    # Prevent out of range error by assigning frequency to maximum when list completed
    if u_index >= len(unseen_freqs):
      unseen_freq = 9999999999999
    else:
      unseen_freq = unseen_freqs[u_index]

    if w_index >= len(word_groups_by_avg_freq): 
      word_group_freq = 9999999999999
    else:
      word_group_freq = word_groups_by_avg_freq[w_index][2]

    print(unseen_freq, word_group_freq)

    # Note: unseen_freqs:             list[freq]
    # Note: word_groups_by_avg_freq:  list[tuple[list[tuple[str, str]], str, freq]]
    if unseen_freq <= word_group_freq:
      # Add word from unseen_freqs[u_index], then increase u_index
      is_native_word = True
      hangul = freq_dict[u_index]
      add_word_to_final_list(hangul, "", is_native_word, freq_dict)
      u_index += 1
    else:
      # Add EACH word from word_groups_by_avg_freq[w_index], then increase w_index
      is_native_word = False
      for hanja_hangul_word in word_groups_by_avg_freq[w_index][0]:
        print("hanja_hangul_word: " + str(hanja_hangul_word))
        hanja = hanja_hangul_word[0]
        hangul = hanja_hangul_word[1]
        add_word_to_final_list(hangul, hanja, is_native_word, freq_dict)
      w_index += 1

    current_index = u_index + w_index - 1
    print(hangul + " (Group " + str(current_index) + " / " + str(num_total_groups) + ")")

  print(final_sino_native_list)  ## TESTING
  
  write_to_csv(final_sino_native_list)

def add_word_to_final_list(hangul, hanja, is_native_word, freq_dict):

  if is_native_word:
    word_to_look_up = hangul
  else:
    word_to_look_up = hanja

  _, _, _, pronunciation, part_of_speech, korean_definitions, english_translations = get_anki_fields(word_to_look_up, is_native_word)

  word_entry = {
    "word": hangul,
    "hanja": hanja,
    "pronunciation": pronunciation,
    "english_translations": dedup(english_translations),
    "korean_definitions": dedup(korean_definitions),
    "part_of_speech": part_of_speech,
    "frequency": freq_dict.index(hangul)
  }

  print(hangul, hanja, dedup(english_translations))

  final_sino_native_list.append(word_entry)

  with open("pickle-output/final_sino_native_dict.pkl", "wb") as f:
      pickle.dump(final_sino_native_list, f)

def write_to_csv(final_sino_native_list):
    # Convert final_sino_native_list to csv
  with open("flashcards-output/final_sino_native_list.csv", "w", newline="", encoding="utf-8-sig") as csvfile:
    fieldnames = ["word", "hanja", "pronunciation", "english_translations", "korean_definitions", "part_of_speech", "frequency"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for entry in final_sino_native_list:
      writer.writerow({
        "word": entry["word"],
        "hanja": entry["hanja"],
        "pronunciation": entry["pronunciation"],
        "english_translations": "; ".join(entry.get("english_translations") or []),
        "korean_definitions": " ".join(entry.get("korean_definitions") or []),
        "part_of_speech": entry["part_of_speech"],
        "frequency": entry["frequency"],
      })