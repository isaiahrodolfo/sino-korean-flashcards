from typing import TypedDict

class WordEntry(TypedDict):
  word: str
  hanja: str
  # highlighted_hanja: str
  part_of_speech: str
  pronunciation: str
  english_translations: list[str]
  korean_definitions: list[str]
  part_of_speech: str
  frequency: int
  