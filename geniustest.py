import webbrowser
import requests
from bs4 import BeautifulSoup
import re

#Lyrics__Container-sc-1ynbvzw-1 kUgSbL
def RipLyrics(lyrics_path):
    response = requests.get(lyrics_path)
    soup = BeautifulSoup(response.content, 'html.parser')
    lyrics_container = soup.find(class_='Lyrics__Container-sc-1ynbvzw-1 kUgSbL')

    if lyrics_container:
        # Initialize an empty list to hold parts of the lyrics
        lyrics = []

        # Recursively extract text from the container
        def extract_text(element):
            if element.name == 'br':
                lyrics.append('\n')
            elif element.name is None:
                lyrics.append(element)
            else:
                for child in element.children:
                    extract_text(child)

        extract_text(lyrics_container)

        # Join the list into a single string
        lyrics_text = ''.join(lyrics)

        # Remove non-ASCII and non-printable characters
        lyrics_text = re.sub(r'[^\x00-\x7F]+', '', lyrics_text)

        print(lyrics_text)
    else:
        print("Lyrics container not found.")


artistName = "Childish Gambino"
songName = "Lithonia"

songName = songName.replace(" ", "-").lower()
artistName = artistName.replace(" ", "-").lower()

lyrics_path = "https://genius.com/"+artistName+"-"+songName+"-lyrics"
response = requests.head(lyrics_path)
print("lyrics status code: -> " + response.status_code.__str__())
lyricsNotFound = response.status_code == 404 

if lyricsNotFound:
    artist_path = "https://genius.com/artists/"+artistName
    response = requests.head(artist_path)
    print("artist status code: -> " + response.status_code.__str__())
    artistNotFound = response.status_code == 404
    if artistNotFound:
        print("The page does not exist.\nPlease check if the artist name and song name are correct.")
    else:
        print("We could not find the lyrics for the song you are looking for.\nHere's the artist page, maybe you can find the song and add the lyrics manually.")
        webbrowser.open(artist_path)
        
else:
    print("The page exists.")
    #webbrowser.open(lyrics_path)
    RipLyrics(lyrics_path)

