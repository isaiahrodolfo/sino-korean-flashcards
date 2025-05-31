import sys
import pickle
import os
import json

from collections import defaultdict

from helpers.get_words import get_words
from helpers.korean_dict import get_hangul, get_word_grade

from collections import defaultdict

from statistics import mean

from datastructures.hanja_words import HanjaWords

word_attributes = [['beginner', 'avg_freq_beginner'], ['novice', 'avg_freq_novice'], ['advanced', 'avg_freq_advanced']]
word_groups_by_avg_freq: list[tuple[list[tuple[str, str]], float, str]]
  
def load_previous_progress():
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

  return hanja_dict, word_groups_by_avg_freq, seen_words, seen_frequencies

def save_progress(hanja_dict, word_groups_by_avg_freq, seen_words, seen_frequencies):
  with open("pickle-output/hanja_progress.pkl", "wb") as f:
    pickle.dump(hanja_dict, f)
  
  with open("pickle-output/word_group_frequency_progress.pkl", "wb") as f:
    pickle.dump(word_groups_by_avg_freq, f)

  with open("pickle-output/seen_words.pkl", "wb") as f:
    pickle.dump(seen_words, f)

  with open("pickle-output/seen_frequencies.pkl", "wb") as f:
    pickle.dump(seen_frequencies, f)

## PART 1: Create database of hanja groups -> words
def create_word_database(hanjas, freq_dict):
  hanja_dict, word_groups_by_avg_freq, seen_words, seen_frequencies = load_previous_progress()

  LEN_HANJAS = len(hanjas)

  print("Starting...")

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
    save_progress(hanja_dict, word_groups_by_avg_freq, seen_words, seen_frequencies)

    current_index = index_hanja + 1
    print("progress saved for hanja " + hanja + " " + "(" + str(current_index) + " / " + str(LEN_HANJAS) + ")")

    # Show progress of hanja dict
    with open("output/hanja_dict_progress.json", "w", encoding="utf-8") as file:
        json.dump({k: v.__dict__ for k, v in hanja_dict.items()}, file, ensure_ascii=False, indent=2)

  # Sort groups of words by frequency 
  word_groups_by_avg_freq.sort(key=lambda x: x[2])

  # (Save progress after sorting all words)
  save_progress(hanja_dict, word_groups_by_avg_freq, seen_words, seen_frequencies)

  return hanja_dict, word_groups_by_avg_freq, seen_words, seen_frequencies