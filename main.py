import sys
import pickle
import os

from collections import defaultdict

from helpers.create_lists import create_lists
from helpers.get_words import get_words
from helpers.korean_dict import get_hangul, get_word_grade, get_anki_fields

from dataclasses import dataclass, field
from collections import defaultdict
from typing import TypedDict, List

# Data structures
@dataclass
class HanjaWords:
  beginner: list[str] = field(default_factory=list) # All words with dictionary entries also in 5800 list
  novice: list[str] = field(default_factory=list)
  advanced: list[str] = field(default_factory=list)
  avg_freq_beginner: float = field(default_factory=float) # Average frequency of words in 5800 list
  avg_freq_novice: float = field(default_factory=float)
  avg_freq_advanced: float = field(default_factory=float)

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
if os.path.exists("hanja_progress.pkl"):
  with open("hanja_progress.pkl", "rb") as f:
    hanja_dict = pickle.load(f)
else:
  hanja_dict = defaultdict(HanjaWords)

if os.path.exists("word_group_frequency_progress.pkl"):
  with open("word_group_frequency_progress.pkl", "rb") as f:
    word_groups_by_avg_freq = pickle.load(f)
else:
  word_groups_by_avg_freq = []

hanjas, freq_dict = create_lists()

def save_progress():
  with open("hanja_progress.pkl", "wb") as f:
    pickle.dump(hanja_dict, f)
  
  with open("word_group_frequency_progress.pkl", "wb") as f:
    pickle.dump(word_groups_by_avg_freq, f)

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

    # Ignore words not in 5800 list or already assigned to a different hanja
    if get_hangul(word) not in freq_dict:
      print("too rare")
      continue
    if word in seen_words:
      print("already seen")
      continue

    match get_word_grade(word):
      case "초급":
        if word not in hanja_dict[hanja].beginner:
          hanja_dict[hanja].beginner.append(word)
      case "중급":
        if word not in hanja_dict[hanja].novice:
          hanja_dict[hanja].novice.append(word)
      case "고급":
        if word not in hanja_dict[hanja].advanced:
          hanja_dict[hanja].advanced.append(word)
      case "unknown":
        print("unknown grade")
        if word not in hanja_dict[hanja].novice: # If grade is unknown, add to novice category
          hanja_dict[hanja].novice.append(word)
      case _:
        print("save progress and try again later")
        sys.exit()

    seen_words.add(word)

  # Calculate avergage frequencies
  print("calculate avg freqs")
  for grade in [['beginner', 'avg_freq_beginner'], ['novice', 'avg_freq_novice'], ['advanced', 'avg_freq_advanced']]:
    grade_words = getattr(hanja_dict[hanja], grade[0])
    # If no words in category, set to -1
    if len(grade_words) == 0:
      setattr(hanja_dict[hanja], grade[1], -1)
      continue
    avg_freq = sum(freq_dict.index(get_hangul(word)) for word in grade_words) / len(grade_words) if grade_words else -1 ## TODO: Getting hangul for each word a second time, prevent this
    # Add to local list
    setattr(hanja_dict[hanja], grade[1], avg_freq)
    # Add to master list
    word_groups_by_avg_freq.append([grade_words, hanja, avg_freq])
  
  print(hanja_dict)
  print(word_groups_by_avg_freq)

  # Save progress for this hanja
  save_progress()
  print("progress saved for hanja " + hanja)

# Sort groups of words by frequency 
word_groups_by_avg_freq.sort(key=lambda x: x[2])

# (Save progress after sorting all words)
save_progress()

## PART 2: Into flashcards format

# Add each word to Anki list
for list_of_words in word_groups_by_avg_freq:
  for hanja_word in list_of_words[0]:
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

    # TODO: Add Traditional, Simplified Chinese and Korean versions of hanja, no matter if they differ (but add a "different hanja?" field)

    final_word_list.append(word_entry)