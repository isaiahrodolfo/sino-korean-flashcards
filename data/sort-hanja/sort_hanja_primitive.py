## Sorts hanzi by frequency
## Does not convert traditional characters

with open("data/sort-hanja/chinese-hanja-freq-5000.txt", "r") as file:
  hanzi_list = file.read()

with open("data/hanja-1800.txt", "r") as file:
  hanja_list = file.read()

sorted_freq_hanja = []
unsorted_freq_hanja = []

for character in hanzi_list:
  if character in hanja_list:
    sorted_freq_hanja.append(character)

for character in hanja_list:
  if character not in sorted_freq_hanja:
    unsorted_freq_hanja.append(character)

# Join sorted and unsorted (rare, could not be found within first 5000 Chinese characters)
sorted_freq_hanja = sorted_freq_hanja + unsorted_freq_hanja
  
with open("output/hanja-chinese-freq-1800.txt", "w") as file:
  file.write("".join(sorted_freq_hanja))