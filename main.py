from datastructures.word_entry import WordEntry
from datastructures.hanja_words import HanjaWords

from parts.create_word_database import create_word_database
from parts.create_native_korean_flashcards import create_native_korean_flashcards
from parts.create_sino_korean_flashcards import create_sino_korean_flashcards

from helpers.create_lists import create_lists
# from helpers.get_words import get_words
# from helpers.korean_dict import get_hangul, get_word_grade, get_anki_fields

hanjas, freq_dict = create_lists()

# PART 1: Create word database
hanja_dict, word_groups_by_avg_freq, seen_words, seen_frequencies = create_word_database(hanjas, freq_dict)

# PART 2: Create native Korean flashcards
create_native_korean_flashcards(freq_dict, seen_frequencies)

# PART 3: Sino-Korean into flashcards format
create_sino_korean_flashcards(seen_words, word_groups_by_avg_freq, freq_dict)