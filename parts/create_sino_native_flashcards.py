import pickle
import os
import csv

from helpers.korean_dict import get_anki_fields
from helpers.dedup import dedup
from helpers.get_unseen_frequencies import get_unseen_frequencies

from datastructures.word_entry import WordEntry

def save_progress(u_index, w_index):
  with open("pickle-output/sino_native_indexes.pkl", "wb") as f:
    pickle.dump((u_index, w_index), f)
  with open("pickle-output/final_sino_native_dict.pkl", "wb") as f:
    pickle.dump(final_sino_native_list, f)

seen = set()

if os.path.exists("pickle-output/final_sino_native_dict.pkl"):
  with open("pickle-output/final_sino_native_dict.pkl", "rb") as f:
    entries: list[WordEntry] = pickle.load(f)

    # dedup
    final_sino_native_list = []
    for entry in entries:
        key = (entry["word"], entry["hanja"])
        if key not in seen:
            seen.add(key)
            final_sino_native_list.append(entry)

    with open("pickle-output/final_sino_native_dict.pkl", "wb") as f:
        pickle.dump(final_sino_native_list, f)

else:
  final_sino_native_list: list[WordEntry] = []
if os.path.exists("pickle-output/sino_native_indexes.pkl"):
  with open("pickle-output/sino_native_indexes.pkl", "rb") as f:
    u_w_indexes = pickle.load(f)
else:
  u_w_indexes = (0, 0)
print("u_w_indexes = " + str(u_w_indexes))

def create_sino_native_flashcards(freq_dict, word_groups_by_avg_freq, seen_frequencies):

  # Load or compute unseen frequencies
  if os.path.exists("pickle-output/unseen_freqs.pkl"):
    with open("pickle-output/unseen_freqs.pkl", "rb") as f:
      print("load unseen freqs")
      unseen_freqs: list[int] = pickle.load(f)
  else:
    unseen_freqs = get_unseen_frequencies(freq_dict, seen_frequencies)
    with open("pickle-output/unseen_freqs.pkl", "wb") as f:
      print("compute unseen freqs")
      pickle.dump(unseen_freqs, f)
  print(unseen_freqs)

  if os.path.exists("pickle-output/w_word_index.pkl"):  ## DELETE THIS IF YOU WANT TO START AT PART 4
    with open("pickle-output/w_word_index.pkl", "rb") as f:
      w_word_index: int = pickle.load(f)
  else:
    w_word_index = 0

  u, w = u_w_indexes
  u_index = u
  w_index = w
  w_word_index = 0

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
      print("native word next")
      is_native_word = True
      hangul = freq_dict[unseen_freqs[u_index]]
      add_word_to_final_list(hangul, "", is_native_word, freq_dict, seen)
      save_progress(u_index, w_index)
      u_index += 1
      print(hangul + " (Group " + str(u_index + w_index - 1) + " / " + str(num_total_groups) + ")")
    else:
      # Add EACH word from word_groups_by_avg_freq[w_index], then increase w_index
      print("sino word next")
      is_native_word = False
      for hanja_hangul_word in word_groups_by_avg_freq[w_index][0]:
        print("hanja_hangul_word: " + str(word_groups_by_avg_freq[w_index][0][w_word_index]))
        hanja = hanja_hangul_word[0]
        hangul = hanja_hangul_word[1]
        add_word_to_final_list(hangul, hanja, is_native_word, freq_dict, seen)
        save_progress(u_index, w_index)
        print(hangul + " (Group " + str(max(u_index + w_index - 1, 0)) + " / " + str(num_total_groups) + ")")
        w_word_index += 1
      w_index += 1
      w_word_index = 0  # Reset starting location

    save_progress(u_index, w_index)
    print("save u_index, w_index positions")

    # current_index = u_index + w_index - 1
    # print(hangul + " (Group " + str(current_index) + " / " + str(num_total_groups) + ")")

  print(final_sino_native_list)  ## TESTING

  save_progress(u_index, w_index)
  
  write_to_csv(final_sino_native_list)

def add_word_to_final_list(hangul, hanja, is_native_word, freq_dict, seen):

  if (hangul, hanja) in seen:
    return  # skip duplicates

  if is_native_word:
    word_to_look_up = hangul
  else:
    word_to_look_up = hanja

  _, _, _, pronunciation, part_of_speech, korean_definitions, english_translations = get_anki_fields(word_to_look_up, is_native_word)

  # Do not add pronunciation rules if same as word
  if pronunciation == hangul:
    pronunciation = ""

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

def save_progress(u, w):
  with open("pickle-output/sino_native_indexes.pkl", "wb") as f:
    pickle.dump((u, w), f)