# Reads in word lists from txt files
def create_lists():

  freq_dict = []
  hanjas = []

  # Read in the hanja list
  with open("data/hanja-chinese-freq-1800-converted.txt", "r") as file:
    content = file.read()
    for char in content:
        hanjas.append(char)

  # Read in the frequency dictionary
  # with open("data/sample-data/korean-frequency-sample-100.txt", "r") as file:
  with open("data/korean-frequency-5000.txt", "r") as file:
    freq_dict = file.read().split('\n')

  return hanjas, freq_dict