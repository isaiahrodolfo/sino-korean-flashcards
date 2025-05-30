# Reads in word lists from txt files
def create_lists():

  freq_dict = []
  hanjas = []

  # Read in the hanja list
  # with open("data/hanja-chinese-freq-1800-converted.txt", "r") as file:
  with open("data/small-data/hanja-chinese-freq-few-converted.txt", "r") as file:  ## TESTING
    content = file.read()
    for char in content:
        hanjas.append(char)

  # Read in the frequency dictionary
  # with open("data/korean-frequency-5000.txt", "r") as file:
  with open("data/small-data/korean-frequency-few.txt", "r") as file: 
    freq_dict = file.read().split('\n')

  return hanjas, freq_dict