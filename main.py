import sys
import pickle
import os
import csv
import time

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
  beginner: list[tuple[str, int]] = field(default_factory=list) # All words with dictionary entries also in 5800 list
  novice: list[tuple[str, int]] = field(default_factory=list)
  advanced: list[tuple[str, int]] = field(default_factory=list)
  avg_freq_beginner: float = field(default_factory=float) # Average frequency of words in 5800 list
  avg_freq_novice: float = field(default_factory=float)
  avg_freq_advanced: float = field(default_factory=float)

word_attributes = [['beginner', 'avg_freq_beginner'], ['novice', 'avg_freq_novice'], ['advanced', 'avg_freq_advanced']]

word_groups_by_avg_freq: list[tuple[list[str], float, str]]

class WordEntry(TypedDict):
  word: str
  hanja: str
  # highlighted_hanja: str
  pronunciation: str
  english_translations: list[str]
  korean_definitions: list[str]
  frequency: int

final_word_list: List[WordEntry]  # Final word list that includes all Anki fields you would need

seen_words = set()  # List of words already associated with a hanja 

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

hanjas, freq_dict = create_lists()

def save_progress_part_1():
  with open("pickle-output/hanja_progress.pkl", "wb") as f:
    pickle.dump(hanja_dict, f)
  
  with open("pickle-output/word_group_frequency_progress.pkl", "wb") as f:
    pickle.dump(word_groups_by_avg_freq, f)

## PART 1: Create database of hanja groups -> words

for hanja in hanjas:
  # Skip if already processed
  if hanja in hanja_dict and any([
      hanja_dict[hanja].avg_freq_advanced  # Checks if the advanced frequency was calculated (last step in completing a hanja entry)
  ]):
    print(f"Skipping already-processed {hanja}")
    continue

  # Process each word corresponding to the current hanja
  words = get_words(hanja)
  
  for word in (w for w in words if w != hanja): # Go through each non-self hanja in word
    print(word)
    print(get_hangul(word))

    # Ignore words not in 5800 list or seen words list (or already assigned to a different hanja)
    if word in seen_words:
      print("already seen")
      continue
    if get_hangul(word) not in freq_dict:
      print("too rare")
      seen_words.add(word)
      continue

    freq = freq_dict.index(get_hangul(word))
    if freq == None:
      print("no freq error")

    match get_word_grade(word):
      case "초급":
        if word not in hanja_dict[hanja].beginner:
          hanja_dict[hanja].beginner.append((word, freq))
      case "중급":
        if word not in hanja_dict[hanja].novice:
          hanja_dict[hanja].novice.append((word, freq))
      case "고급":
        if word not in hanja_dict[hanja].advanced:
          hanja_dict[hanja].advanced.append((word, freq))
      case "unknown":
        print("unknown grade")
        if word not in hanja_dict[hanja].advanced: # If grade is unknown, add to advanced category
          hanja_dict[hanja].advanced.append((word, freq))
      case _:
        print("save progress and try again later")
        sys.exit()

    seen_words.add(word)

  print(hanja_dict)

  # TODO: Rearrange words, if one group is too small, etc.
  if (len(getattr(hanja_dict[hanja], word_attributes[0][0])) <= 2 and 
      len(getattr(hanja_dict[hanja], word_attributes[1][0])) <= 2 and 
      len(getattr(hanja_dict[hanja], word_attributes[2][0])) <= 2):
    # (b, n, a)
    # (<=2, <=2, <=2) - put all together (in novice category)
    hanja_dict[hanja].novice = getattr(hanja_dict[hanja], word_attributes[0][0]) + getattr(hanja_dict[hanja], word_attributes[1][0]) + getattr(hanja_dict[hanja], word_attributes[2][0])
    setattr(hanja_dict[hanja], word_attributes[0][0], [])  # empty out beginner word list
    setattr(hanja_dict[hanja], word_attributes[2][0], [])  # empty out advanced word list
    print("(<=2, <=2, <=2)")
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
  if len(getattr(hanja_dict[hanja], word_attributes[2][0])) <= 2:
    # (X, X, <=2) - combine n & a (in novice category)
    hanja_dict[hanja].novice = getattr(hanja_dict[hanja], word_attributes[1][0]) + getattr(hanja_dict[hanja], word_attributes[2][0])
    setattr(hanja_dict[hanja], word_attributes[2][0], [])  # empty out advanced word list
    print("(X, X, <=2)")

  print(hanja_dict)

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
  
  print(hanja_dict)
  print(word_groups_by_avg_freq)

  # Save progress for this hanja
  save_progress_part_1()
  print("progress saved for hanja " + hanja)

# Sort groups of words by frequency 
word_groups_by_avg_freq.sort(key=lambda x: x[2])

# (Save progress after sorting all words)
save_progress_part_1()

## PART 2: Into flashcards format

# Try to load previous progress
if os.path.exists("pickle-output/final_word_list.pkl"):
  with open("pickle-output/final_word_list.pkl", "rb") as f:
    final_word_list = pickle.load(f)
else:
  final_word_list = defaultdict(HanjaWords)

# Add each word to Anki list (final word list)
for list_of_words in word_groups_by_avg_freq:
  for hanja_word in list_of_words[0]:
    print(hanja_word)
    word_entry = defaultdict(WordEntry)

    _, word, _, pronunciation, part_of_speech, korean_definitions, english_translations = get_anki_fields(word)

    word_entry = {
      "word": word,
      "hanja": hanja_word,
      "pronunciation": pronunciation,
      "english_translations": english_translations,
      "korean_definitions": korean_definitions,
      "frequency": freq_dict.index(get_hangul(word))
    }
    # ? Add Traditional, Simplified Chinese and Korean versions of hanja, no matter if they differ (but add a "different hanja?" field)

    final_word_list.append(word_entry)

    with open("pickle-output/final_word_list.pkl", "wb") as f:
      pickle.dump(final_word_list, f)

# Convert final_word_list to csv

with open("final_word_list.csv", "w", newline="", encoding="utf-8-sig") as csvfile:
  fieldnames = ["word", "hanja", "pronunciation", "english_translations", "korean_definitions", "frequency"]
  writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

  writer.writeheader()
  for entry in final_word_list:
    writer.writerow({
      "word": entry["word"],
      "hanja": entry["hanja"],
      "pronunciation": entry["pronunciation"],
      "english_translations": "; ".join(entry["english_translations"]),
      "korean_definitions": "; ".join(entry["korean_definitions"]),
      "frequency": entry["frequency"],
    })