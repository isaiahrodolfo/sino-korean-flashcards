import os
import pickle

def save_data(word_groups_by_avg_freq, seen_words, seen_frequencies):
  data = (word_groups_by_avg_freq, seen_words, seen_frequencies)

  with open("pickle-output/data.pkl", "wb") as f:
    pickle.dump(data, f)

def load_data():
  if os.path.exists("pickle-output/data.pkl"):
    with open("pickle-output/data.pkl", "rb") as f:
      data = pickle.load(f)
  else:
    data = None
    
  return data