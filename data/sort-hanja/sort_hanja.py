## Sorts hanzi by frequency
## DOES convert traditional characters, given a mapping
## Ignores 的

traditional_to_hanja = {
  "腳": "脚",
  "卻": "却",
  "舉": "擧",
  "雞": "鷄",
  "啟": "啓",
  "礦": "鑛",
  "教": "敎",
  "既": "旣",
  "隸": "隷",
  "裹": "裏",
  "晚": "晩",
  "仿": "倣",
  "翻": "飜",
  "並": "竝",
  "屏": "屛",
  "峰": "峯",
  "冰": "氷",
  "查": "査",
  "尚": "尙",
  "敘": "敍",
  "緒": "緒",
  "唇": "脣",
  "慎": "愼",
  "顏": "顔",
  "研": "硏",
  "污": "汚",
  "為": "爲",
  "偽": "僞",
  "飲": "飮",
  "獎": "奬",
  "牆": "墻",
  "妝": "粧",
  "眾": "衆",
  "即": "卽",
  "真": "眞",
  "鎮": "鎭",
  "著": "着",
  "慚": "慙",
  "窗": "窓",
  "青": "靑",
  "清": "清",
  "值": "値",
  "鬥": "鬪",
  "恆": "恒",
  "鄉": "鄕",
  "毀": "毁",
  "攜": "携",
}
with open("data/sort-hanja/chinese-hanja-freq-5000.txt", "r") as file:
  hanzi_list = file.read()

with open("data/hanja-1800.txt", "r") as file:
  hanja_list = file.read()

sorted_freq_hanja = []
unsorted_freq_hanja = []

for character in hanzi_list:
  if character in hanja_list:
    sorted_freq_hanja.append(character)
  else:
    hanja_version = traditional_to_hanja.get(character)
    if hanja_version:
      sorted_freq_hanja.append(hanja_version)

for character in hanja_list:
  if character not in sorted_freq_hanja:
    unsorted_freq_hanja.append(character)

# Join sorted and unsorted (rare, could not be found within first 5000 Chinese characters)
sorted_freq_hanja = sorted_freq_hanja + unsorted_freq_hanja
  
with open("output/hanja-chinese-freq-1800-converted.txt", "w") as file:
  file.write("".join(sorted_freq_hanja))