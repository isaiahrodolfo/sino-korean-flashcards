import requests
from bs4 import BeautifulSoup

# Gets a list of words that include the given hanja using the website: koreanhanja.app
def get_words(hanja):

  # Fetch and parse the webpage
  url = "https://koreanhanja.app/" + hanja
  response = requests.get(url)
  soup = BeautifulSoup(response.text, "html.parser")

  # Extract the Chinese characters (first <td> in each row)
  table = soup.find("table", class_="similar-words")
  words = []
  
  words.append(hanja) # Append self to list
  for row in table.find_all("tr"):
      td = row.find("td", class_="nowrap")
      if td:
          char = td.get_text(strip=True)
          words.append(char)

  return words

