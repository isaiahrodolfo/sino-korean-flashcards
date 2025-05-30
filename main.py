import sys
import pickle
import os
import csv
import json

from collections import defaultdict

from helpers.create_lists import create_lists
from helpers.get_words import get_words
from helpers.korean_dict import get_hangul, get_word_grade, get_anki_fields

from dataclasses import dataclass, field
from collections import defaultdict
from typing import TypedDict, List

from statistics import mean

# Data structures
@dataclass
class HanjaWords:
  beginner: list[tuple[tuple[str, str], int]] = field(default_factory=list) # All words with dictionary entries also in 5800 list
  novice: list[tuple[tuple[str, str], int]] = field(default_factory=list)
  advanced: list[tuple[tuple[str, str], int]] = field(default_factory=list)
  avg_freq_beginner: float = field(default_factory=float) # Average frequency of words in 5800 list
  avg_freq_novice: float = field(default_factory=float)
  avg_freq_advanced: float = field(default_factory=float)

word_attributes = [['beginner', 'avg_freq_beginner'], ['novice', 'avg_freq_novice'], ['advanced', 'avg_freq_advanced']]

word_groups_by_avg_freq: list[tuple[list[tuple[str, str]], float, str]]

class WordEntry(TypedDict):
  word: str
  hanja: str
  # highlighted_hanja: str
  pronunciation: str
  english_translations: list[str]
  korean_definitions: list[str]
  frequency: int

# final_native_korean_dict: list[WordEntry]  # Final word list that includes all Anki fields you would need
# final_sino_korean_dict: list[WordEntry]  # Final word list that includes all Anki fields you would need

# seen_words = set()  # List of words already associated with a hanja 
# seen_frequencies = set()  # List of frequencies already seen

# Try to load previous progress
if os.path.exists("pickle-output/hanja_progress.pkl"):
  with open("pickle-output/hanja_progress.pkl", "rb") as f:
    hanja_dict = pickle.load(f)
else:
  hanja_dict = defaultdict(HanjaWords)

if os.path.exists("pickle-output/word_group_frequency_progress.pkl"):
  with open("pickle-output/word_group_frequency_progress.pkl", "rb") as f:
    word_groups_by_avg_freq = pickle.load(f)
else:
  word_groups_by_avg_freq = []
  
if os.path.exists("pickle-output/seen_words.pkl"):
  with open("pickle-output/seen_words.pkl", "rb") as f:
    seen_words = pickle.load(f)
else:
  seen_words = set()

if os.path.exists("pickle-output/seen_frequencies.pkl"):
  with open("pickle-output/seen_frequencies.pkl", "rb") as f:
    seen_frequencies = pickle.load(f)
else:
  seen_frequencies = set()

hanjas, freq_dict = create_lists()
LEN_HANJAS = len(hanjas)

def save_progress_part_1():
  with open("pickle-output/hanja_progress.pkl", "wb") as f:
    pickle.dump(hanja_dict, f)
  
  with open("pickle-output/word_group_frequency_progress.pkl", "wb") as f:
    pickle.dump(word_groups_by_avg_freq, f)

  with open("pickle-output/seen_words.pkl", "wb") as f:
    pickle.dump(seen_words, f)

  with open("pickle-output/seen_frequencies.pkl", "wb") as f:
    pickle.dump(seen_frequencies, f)

print("Starting...")

## PART 1: Create database of hanja groups -> words

for index_hanja, hanja in enumerate(hanjas):
  # Skip if already processed
  if hanja in hanja_dict and any([
      hanja_dict[hanja].avg_freq_advanced  # Checks if the advanced frequency was calculated (last step in completing a hanja entry)
  ]):
    # print(f"Skipping already-processed {hanja}")
    continue

  # Process each word corresponding to the current hanja
  words = get_words(hanja)
  
  for word in (w for w in words if w != hanja): # Go through each non-self hanja in word
    print(word)

    if "-" in word: # ignore words with a dash (these are prefixes or suffixes)
      print("skipped")
      continue

    get_hangul_result = get_hangul(word)
    if get_hangul_result is not None:
      hangul_word, _ = get_hangul(word)
    else: 
      hangul_word = None
      continue  # ignore hanja with no recognizable pronunciation
    print(hangul_word)

    # Ignore words not in 5800 list or seen words list (or already assigned to a different hanja)
    if word in seen_words:
      print("already seen")
      continue
    if hangul_word not in freq_dict:
      print("too rare")
      seen_words.add(word)
      continue

    freq = freq_dict.index(hangul_word)
    if freq == None:
      print("no freq error")

    match get_word_grade(word):
      case "초급":
        if word not in hanja_dict[hanja].beginner:
          hanja_dict[hanja].beginner.append(((word, hangul_word), freq))  # add both the hanja and hangul versions together
      case "중급":
        if word not in hanja_dict[hanja].novice:
          hanja_dict[hanja].novice.append(((word, hangul_word), freq))
      case "고급":
        if word not in hanja_dict[hanja].advanced:
          hanja_dict[hanja].advanced.append(((word, hangul_word), freq))
      case "unknown":
        print("unknown grade")
        if word not in hanja_dict[hanja].advanced: # If grade is unknown, add to advanced category
          hanja_dict[hanja].advanced.append(((word, hangul_word), freq))
      case _:
        print("save progress and try again later")
        sys.exit()

    seen_words.add(word)
    seen_frequencies.add(freq)

  # print(hanja_dict)  ## TESTING

  # Rearrange words, if one group is too small, etc.
  if (len(getattr(hanja_dict[hanja], word_attributes[0][0])) <= 2 and 
      len(getattr(hanja_dict[hanja], word_attributes[1][0])) <= 2 and 
      len(getattr(hanja_dict[hanja], word_attributes[2][0])) <= 2):
    # (b, n, a)
    # (<=2, <=2, <=2) - put all together (in novice category)
    hanja_dict[hanja].novice = getattr(hanja_dict[hanja], word_attributes[0][0]) + getattr(hanja_dict[hanja], word_attributes[1][0]) + getattr(hanja_dict[hanja], word_attributes[2][0])
    setattr(hanja_dict[hanja], word_attributes[0][0], [])  # empty out beginner word list
    setattr(hanja_dict[hanja], word_attributes[2][0], [])  # empty out advanced word list
    print("(<=2, <=2, <=2)")
  else:
    if len(getattr(hanja_dict[hanja], word_attributes[1][0])) <= 2:
      # (X, <=2, X) - combine b & n (in beginner category) OR
      hanja_dict[hanja].beginner = getattr(hanja_dict[hanja], word_attributes[0][0]) + getattr(hanja_dict[hanja], word_attributes[1][0])
      setattr(hanja_dict[hanja], word_attributes[1][0], [])  # empty out novice word list
      print("(X, <=2, X)")
    if len(getattr(hanja_dict[hanja], word_attributes[0][0])) <= 2:
      # (<=2, X, X) - combine b & n (in novice category)
      hanja_dict[hanja].novice = getattr(hanja_dict[hanja], word_attributes[0][0]) + getattr(hanja_dict[hanja], word_attributes[1][0])
      setattr(hanja_dict[hanja], word_attributes[0][0], [])  # empty out beginner word list
      print("(<=2, X, X)")
    # if len(getattr(hanja_dict[hanja], word_attributes[2][0])) <= 2:
    #   # (X, X, <=2) - combine n & a (in novice category)
    #   hanja_dict[hanja].novice = getattr(hanja_dict[hanja], word_attributes[1][0]) + getattr(hanja_dict[hanja], word_attributes[2][0])
    #   setattr(hanja_dict[hanja], word_attributes[2][0], [])  # empty out advanced word list
    #   print("(X, X, <=2)")

  # print(hanja_dict)  # TESTING

  # Calculate average frequencies
  print("calculate avg freqs")
  for grade in word_attributes:
    grade_words = getattr(hanja_dict[hanja], grade[0])
    # If no words in category, set to -1
    if len(grade_words) == 0:
      setattr(hanja_dict[hanja], grade[1], -1)
      continue

    avg_freq = mean([freq for _, freq in grade_words])

    # Add to local list
    setattr(hanja_dict[hanja], grade[1], avg_freq)
    # Add to master list
    word_groups_by_avg_freq.append([[word for word, _ in grade_words], hanja, avg_freq])
  
  # print(hanja_dict)  # TESTING
  # print(word_groups_by_avg_freq)  # TESTING

  # Save progress for this hanja
  save_progress_part_1()

  current_index = index_hanja + 1
  print("progress saved for hanja " + hanja + " " + "(" + str(current_index) + " / " + str(LEN_HANJAS) + ")")

  # Show progress of hanja dict
  with open("output/hanja_dict_progress.json", "w", encoding="utf-8") as file:
      json.dump({k: v.__dict__ for k, v in hanja_dict.items()}, file, ensure_ascii=False, indent=2)

# Sort groups of words by frequency 
word_groups_by_avg_freq.sort(key=lambda x: x[2])

# (Save progress after sorting all words)
save_progress_part_1()

## PART 2: Native Korean words into flashcards format

## This function helps to deduplicate translations/definitions taken from the dictionary, etc.
def dedup(seq: list[str]) -> list[str]:
    seen = set()
    return [x for x in seq if not (x in seen or seen.add(x))]

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
    print(f"Skipping already-processed {word}")
    continue

  _, _, _, pronunciation, part_of_speech, korean_definitions, english_translations = get_anki_fields(word, True)

  word_entry = {
    "word": word,
    "hanja": "",
    "pronunciation": pronunciation,
    "english_translations": dedup(english_translations),
    "korean_definitions": dedup(korean_definitions),
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
  fieldnames = ["word", "hanja", "pronunciation", "english_translations", "korean_definitions", "frequency"]
  writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

  writer.writeheader()
  for entry in final_native_korean_dict.values():
    writer.writerow({
      "word": entry["word"],
      "hanja": entry["hanja"],
      "pronunciation": entry["pronunciation"],
      "english_translations": "; ".join(entry["english_translations"]),
      "korean_definitions": "; ".join(entry["korean_definitions"]),
      "frequency": entry["frequency"],
    })

## PART 3: Sino-Korean into flashcards format

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
  fieldnames = ["word", "hanja", "pronunciation", "english_translations", "korean_definitions", "frequency"]
  writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

  writer.writeheader()
  for entry in final_sino_korean_dict.values():
    writer.writerow({
      "word": entry["word"],
      "hanja": entry["hanja"],
      "pronunciation": entry["pronunciation"],
      "english_translations": "; ".join(entry["english_translations"]),
      "korean_definitions": "; ".join(entry["korean_definitions"]),
      "frequency": entry["frequency"],
    })