import pickle
import os

from datastructures.word_entry import WordEntry
from datastructures.hanja_words import HanjaWords

# from parts.create_word_database_by_grades import create_word_database
from parts.create_word_database_equal_group_sizes import create_word_database
from parts.create_native_korean_flashcards import create_native_korean_flashcards
from parts.create_sino_korean_flashcards import create_sino_korean_flashcards
from parts.create_sino_native_flashcards import create_sino_native_flashcards

from helpers.create_lists import create_lists
# from helpers.get_words import get_words
# from helpers.korean_dict import get_hangul, get_word_grade, get_anki_fields

def get_current_part_number():
  if os.path.exists("pickle-output/part_number.pkl"):
    with open("pickle-output/part_number.pkl", "rb") as f:
      part_number = pickle.load(f)
  else:
    part_number = 1

  return part_number

# Get current part number
part_number = get_current_part_number()

hanjas, freq_dict = create_lists()

# PART 1: Create word database
if part_number == 1:
  hanja_dict, word_groups_by_avg_freq, seen_words, seen_frequencies = create_word_database(hanjas, freq_dict)
part_number += 1

# a) Create separate Sino & native flashcards

# PART 2: Create native Korean flashcards
if part_number == 2:
  create_native_korean_flashcards(freq_dict, seen_frequencies)
part_number += 1

# PART 3: Sino-Korean into flashcards format
if part_number == 3:
  create_sino_korean_flashcards(freq_dict, word_groups_by_avg_freq)
part_number += 1

# b) Create combined Sino & native flashcards

# PART 4
if part_number == 4:
  create_sino_native_flashcards(freq_dict, word_groups_by_avg_freq, seen_frequencies)