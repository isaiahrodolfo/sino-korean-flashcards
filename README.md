# Korean Anki flashcards: Sino-Korean words for Chinese speakers (and those already familiar with CJK characters)

## About

This code generates a .csv file meant for importing to a flashcard app, like Anki. These flashcards are meant for learners of Korean who already have prior CJK (Chinese, Japanese, Korean) character knowledge.

## Goal

This flashcard deck groups the same characters in the same grade level together, allowing learners to focus on mastering one hanja at a time, while learning new words in the process. Words tend to decrease in frequency, allowing learners to focus on more common words at the beginning, then increasing difficulty.

These flashcards are not meant to be a perfect curation of an introduction to each hanja, only a loose computer-generated organization sorted by frequency. Thus, some cards may be out of place or would be better off in a different order.

## Algorithm

This code aims to gradually introduce Korean words derived from Chinese (Sino-Korean words) using the following algorithm:
1. Using a list of the [5000+ most frequent Korean words](https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/Korean_5800) ("word list") and a list of the [1800 characters taught in Korean grade schools](https://ko.wiktionary.org/wiki/%EB%B6%80%EB%A1%9D:%ED%95%9C%EB%AC%B8_%EA%B5%90%EC%9C%A1%EC%9A%A9_%EA%B8%B0%EC%B4%88_%ED%95%9C%EC%9E%90_1800) sorted by [character frequency with respect to the Chinese language (Traditional characters)](https://technology.chtsai.org/charfreq/94charfreq.html) ("hanja list"),
2. For each character in the hanja list, search for all words that have that hanja using the [koreanhanjaapp website](koreanhanja.app) and assign them to the hanja. If a word is already assigned to a different hanja, ignore it. Then, sort by their level (elementary, middle, high) using [the Republic of Korea's online dictionary](https://krdict.korean.go.kr/openApi/openApiInfo). Filter out words that do not appear in the word list. 
3. For each grade category of each hanja, take the average of the frequency of the words. Sort the frequencies of the word groups in increasing order. This is the order the words are shown in the flashcards.

## How You Can Help

Contribute to this project by:
1. Hand-curating a better flashcard deck
2. Adding definitions for other languages, example sentences and their translations, and other fields