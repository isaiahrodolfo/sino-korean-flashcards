import sys
import pickle
import os
import json

from collections import defaultdict

from helpers.get_words import get_words
from helpers.korean_dict import get_hangul

from collections import defaultdict

from statistics import mean

from datastructures.hanja_words import HanjaWords

GROUP_SIZE = 3
HANJA_FREQUENCY_DISPLACEMENT = -500  # Show hanja much earlier by artificially lowering its frequency rankings

word_attributes = [['beginner', 'avg_freq_beginner'], ['novice', 'avg_freq_novice'], ['advanced', 'avg_freq_advanced']]
word_groups_by_avg_freq: list[tuple[list[tuple[str, str]], str, float]]
  
def load_previous_progress():
  # Try to load previous progress
  if os.path.exists("pickle-output/seen_hanja_index.pkl"):
    with open("pickle-output/seen_hanja_index.pkl", "rb") as f:
      seen_hanja_index = pickle.load(f)
  else:
    seen_hanja_index = -1

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

  return seen_hanja_index, word_groups_by_avg_freq, seen_words, seen_frequencies

def save_progress(seen_hanja_index, word_groups_by_avg_freq, seen_words, seen_frequencies):
  with open("pickle-output/seen_hanja_index.pkl", "wb") as f:
    pickle.dump(seen_hanja_index, f)
  
  with open("pickle-output/word_group_frequency_progress.pkl", "wb") as f:
    pickle.dump(word_groups_by_avg_freq, f)

  with open("pickle-output/seen_words.pkl", "wb") as f:
    pickle.dump(seen_words, f)

  with open("pickle-output/seen_frequencies.pkl", "wb") as f:
    pickle.dump(seen_frequencies, f)

## PART 1: Create database of hanja groups -> words
def create_word_database(hanjas, freq_dict):
  seen_hanja_index, word_groups_by_avg_freq, seen_words, seen_frequencies = load_previous_progress()

  # Output current progress out for checking
  with open("output/word-database-progress.json", "w", encoding='utf-8') as f:
    json.dump(word_groups_by_avg_freq, f, ensure_ascii=False)

  seen_hanja_index = int(seen_hanja_index)

  print("seen_hanja_index = " + str(seen_hanja_index))
  # print("seen_frequencies = " + str(seen_frequencies))
  print("seen_frequencies (count) = " + str(len(seen_frequencies)))

  LEN_HANJAS = len(hanjas)

  print("Starting...")

  for index_hanja, hanja in enumerate(hanjas):
    # Skip if already processed
    if index_hanja <= seen_hanja_index:
      print(f"{hanja} +")
      continue

    # Process each word corresponding to the current hanja
    words = get_words(hanja)
    words_freq_sorted = []

    # Sort all words by frequency number increasing
    for word in (w for w in words if w != hanja):
      print(word)

      if "-" in word: # ignore words with a dash (these are prefixes or suffixes)
        print("skip")
        continue

      get_hangul_result = get_hangul(word)
      if get_hangul_result is not None:
        hangul, _ = get_hangul(word)
      else: 
        hangul = None
        continue  # ignore hanja with no recognizable pronunciation
      print(hangul)

      # Ignore words not in 5800 list or seen words list (or already assigned to a different hanja)
      if word in seen_words:
        print("seen")
        continue
      if hangul not in freq_dict:
        print("rare")
        seen_words.add(word)
        continue

      freq = freq_dict.index(hangul)
      if freq == None:
        print("no freq error")
        return
       
      w_freq = freq_dict.index(hangul)
      words_freq_sorted.append((word, hangul, w_freq))

      seen_words.add(word)
      seen_frequencies.add(freq)

      # Save seen frequencies
      with open("pickle-output/seen_frequencies.pkl", "wb") as f:
        pickle.dump(seen_frequencies, f)

      # Output seen words and frequencies to double check
      with open("output/seen_words.json", "w", encoding='utf-8') as f:
        json.dump(list(seen_words), f, ensure_ascii=False)
      with open("output/seen_frequencies.json", "w", encoding='utf-8') as f:
        json.dump(list(seen_frequencies), f, ensure_ascii=False)

    words_freq_sorted.sort(key=lambda x: x[2])
    # print("frequency sorted " + str(words_freq_sorted))

    word_group = []  # list[tuple(hanja, hangul)]
    
    # Group into GROUP_SIZE number groups
    for index_word, hanja_hangul_freq in enumerate(words_freq_sorted): # Go through each non-self hanja in word
          
      word, hangul, freq = hanja_hangul_freq

      word_group.append(hanja_hangul_freq)

      # Dump group after seeing GROUP_SIZE number of words, or when close to the end of the list
      if (((index_word + 1) % GROUP_SIZE == 0 and index_word < len(words_freq_sorted) - GROUP_SIZE - 1) or 
          (index_word == len(words_freq_sorted) - 1)):
        # Calculate average frequency
        print("index_word = " + str(index_word) + ", dump " + str(word_group))
        avg_freq = mean([freq for _, _, freq in word_group]) 
        word_groups_by_avg_freq.append((word_group, hanja, avg_freq + HANJA_FREQUENCY_DISPLACEMENT))  # Show hanja much earlier by artificially lowering its frequency rankings
        # print(word_groups_by_avg_freq)  ## TESTING
        word_group = []  # Reset when dumped
      
    # Save progress for this hanja
    save_progress(index_hanja, word_groups_by_avg_freq, seen_words, seen_frequencies)

    print("progress saved for hanja " + hanja + " " + "(" + str(index_hanja + 1) + " / " + str(LEN_HANJAS) + ")")

    # Print current progress out for checking
    with open("output/word-database-progress.json", "w", encoding='utf-8') as f:
      json.dump(word_groups_by_avg_freq, f, ensure_ascii=False)

  # Sort groups of words by frequency 
  word_groups_by_avg_freq.sort(key=lambda x: x[2])

  # (Save progress after sorting all words)
  save_progress(index_hanja, word_groups_by_avg_freq, seen_words, seen_frequencies)

  # # Pickle data
  # save_data(word_groups_by_avg_freq, seen_words, seen_frequencies)

  return None, word_groups_by_avg_freq, seen_words, seen_frequencies