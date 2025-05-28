## Extracts hanja from the website: https://ko.wiktionary.org/wiki/%EB%B6%80%EB%A1%9D:%ED%95%9C%EB%AC%B8_%EA%B5%90%EC%9C%A1%EC%9A%A9_%EA%B8%B0%EC%B4%88_%ED%95%9C%EC%9E%90_1800
## In order to get most used 1800 hanja

hanjas = []

# Read in the hanja list
with open("data/extract-hanja/chinese-hanja-freq-5000.txt", "r") as file:
# with open("data/hanja-1800-wikipedia.txt", "r") as file:
  content = file.read()
  for char in content:
    if ord(char) in range(0x4E00, 0x9FFF):
      hanjas.append(char)

# Output onlly hanja to a file
with open("output/chinese-hanja.txt", "w") as file:
# with open("output/hanjas.txt", "w") as file:
  for word in hanjas:
    file.write(word)