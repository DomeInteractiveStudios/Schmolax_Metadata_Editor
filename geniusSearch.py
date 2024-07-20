#import webbrowser
import requests
from bs4 import BeautifulSoup
import re

from globalFunctions import PrintText

#get the song, artist and album names from the user
global artistName, songName, albumName

def getVariables(artist, song_name, album):
    global artistName, songName, albumName

    artistName = artist
    songName = song_name
    albumName = album
    
    songName = songName.replace(" ", "-").lower()
    artistName = artistName.replace(" ", "-").lower()
    albumName = albumName.replace(" ", "-").lower()

    main()

    
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

def main():
    lyrics_path = "https://genius.com/"+artistName+"-"+songName+"-lyrics"
    response = requests.head(lyrics_path)
    print()
    lyricsNotFound = response.status_code == 404 

    if lyricsNotFound:
        PrintText("lyrics status code: -> " + response.status_code.__str__(), "red")
        albumPath = "https://genius.com/albums/"+artistName+"/"+albumName
        response = requests.head(albumPath)
        albumNotFound = response.status_code == 404
        if albumNotFound:
            PrintText("Album status code: " + response.status_code.__str__(), "red")
            artist_path = "https://genius.com/artists/"+artistName
            response = requests.head(artist_path)
            artistNotFound = response.status_code == 404
            if artistNotFound:
                PrintText("Artist status code: " + response.status_code.__str__(), "red")
                PrintText("The page does not exist.\nPlease check if the song, artist and album names are correct.", "red")
            else:
                PrintText("Artist status code: " + response.status_code.__str__(), "green")
                PrintText("We could not find the lyrics for the song you are looking for.\nHere's the artist page, maybe you can find the song and add the lyrics manually.", "yellow")
                PrintText(artist_path, "blue")
                #webbrowser.open(artist_path)
        else:
            PrintText("Album status code: " + response.status_code.__str__(), "green")
            PrintText("We could not find the lyrics for the song you are looking for.\nHere's the album page, maybe you can find the song and add the lyrics manually.", "yellow")
            PrintText(albumPath, "blue")
            #webbrowser.open(albumPath)
            
    else:
        PrintText("lyrics status code: -> " + response.status_code.__str__(), "green")
        PrintText("Lyrics Found", "green")
        #webbrowser.open(lyrics_path)
        RipLyrics(lyrics_path)

