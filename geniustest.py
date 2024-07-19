#import webbrowser
import requests
from bs4 import BeautifulSoup
import re

#Lyrics__Container-sc-1ynbvzw-1 kUgSbL
def RipLyrics(lyrics_path):
    response = requests.get(lyrics_path)
    soup = BeautifulSoup(response.content, 'html.parser')
    lyrics_containers = soup.find_all(class_='Lyrics__Container-sc-1ynbvzw-1 kUgSbL')

    if lyrics_containers:
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
        for container in lyrics_containers:
            lyrics.append('\n')
            extract_text(container)
            

        # Join the list into a single string
        lyrics_text = ''.join(lyrics)

        # Remove non-ASCII and non-printable characters
        lyrics_text = re.sub(r'[^\x00-\x7F]+', '', lyrics_text)

        print(lyrics_text)
    else:
        print("We're sorry, lyrics could not be retrieved for this song.\nHere's the link to the page, so you can add them manually.")
        print(lyrics_path)


artistName = "Logic"
songName = "Homicide"
albumName = "Confessions of a Dangerous Mind"

songName = songName.replace(" ", "-").lower()
artistName = artistName.replace(" ", "-").lower()
albumName = albumName.replace(" ", "-").lower()

lyrics_path = "https://genius.com/"+artistName+"-"+songName+"-lyrics"
response = requests.head(lyrics_path)
print("lyrics status code: -> " + response.status_code.__str__())
lyricsNotFound = response.status_code == 404 

if lyricsNotFound:
    albumPath = "https://genius.com/albums/"+artistName+"/"+albumName
    response = requests.head(albumPath)
    print("album status code: -> " + response.status_code.__str__())
    albumNotFound = response.status_code == 404
    if albumNotFound:
        artist_path = "https://genius.com/artists/"+artistName
        response = requests.head(artist_path)
        print("artist status code: -> " + response.status_code.__str__())
        artistNotFound = response.status_code == 404
        if artistNotFound:
            print("The page does not exist.\nPlease check if the song, artist and album names are correct.")
        else:
            print("We could not find the lyrics for the song you are looking for.\nHere's the artist page, maybe you can find the song and add the lyrics manually.")
            print(artist_path)
            #webbrowser.open(artist_path)
    else:
        print("We could not find the lyrics for the song you are looking for.\nHere's the album page, maybe you can find the song and add the lyrics manually.")
        print(albumPath)
        #webbrowser.open(albumPath)
        
else:
    print("The page exists.")
    #webbrowser.open(lyrics_path)
    RipLyrics(lyrics_path)

