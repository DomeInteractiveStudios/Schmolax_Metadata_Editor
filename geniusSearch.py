import requests
from bs4 import BeautifulSoup
import re
import unicodedata

outputs = [] # List to hold the outputs of the search

# Global variables
global artistName, songName, albumName

def getVariables(artist, song_name, album):
    global artistName, songName, albumName
    outputs.clear() # Clear the outputs list before starting a new search

    artistName = artist
    songName = song_name
    albumName = album
    # Remove accents from the names
    songName = unicodedata.normalize('NFKD', songName).encode('ASCII', 'ignore').decode('utf-8')
    artistName = unicodedata.normalize('NFKD', artistName).encode('ASCII', 'ignore').decode('utf-8')
    albumName = unicodedata.normalize('NFKD', albumName).encode('ASCII', 'ignore').decode('utf-8')
    # Convert the names to lowercase and replace spaces with hyphens and remove brackets from the names
    songName = songName.replace(" ", "-").replace("(", "").replace(")", "").replace("'", "").replace(",", "").lower()
    artistName = artistName.replace(" ", "-").replace("(", "").replace(")", "").replace("'", "").replace(",", "").lower()
    albumName = albumName.replace(" ", "-").replace("(", "").replace(")", "").replace("'", "").replace(",", "").lower()

    main()

    return outputs

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

        outputs.append((
            lyrics_text, 
            "default"
        ))

    else:
        outputs.append((
            "We're sorry, lyrics could not be retrieved for this song.\nHere's the link to the page, so you can add them manually.\n", 
            "yellow"
        ))
        outputs.append((
            lyrics_path, 
            "blue"
        ))

def main():
    lyrics_path = "https://genius.com/"+artistName+"-"+songName+"-lyrics"
    response = requests.head(lyrics_path)
    lyricsNotFound = response.status_code == 404 

    if lyricsNotFound:
        outputs.append((
            "lyrics status code: -> " + response.status_code.__str__() + "\n", 
            "red"
        ))
        albumPath = "https://genius.com/albums/"+artistName+"/"+albumName
        response = requests.head(albumPath)
        albumNotFound = response.status_code == 404
        if albumNotFound:
            outputs.append((
                "Album status code: " + response.status_code.__str__() + "\n", 
                "red"
            ))
            artist_path = "https://genius.com/artists/"+artistName
            response = requests.head(artist_path)
            artistNotFound = response.status_code == 404
            if artistNotFound:
                outputs.append((
                    "Artist status code: " + response.status_code.__str__() + "\n",
                    "red"
                ))
                outputs.append((
                    "The page does not exist.\nPlease check if the song, artist and album names are correct.\n",
                    "red"
                ))
            else:
                outputs.append((
                    "Artist status code: " + response.status_code.__str__() + "\n",
                    "green"
                ))
                outputs.append((
                    "We could not find the lyrics for the song you are looking for.\nHere's the artist page, maybe you can find the song and add the lyrics manually.\n", 
                    "yellow"
                ))
                outputs.append((
                    artist_path, 
                    "blue"
                ))
                #webbrowser.open(artist_path)
        else:
            outputs.append((
                "Album status code: " + response.status_code.__str__() + "\n", 
                "green"
            ))
            outputs.append((
                "We could not find the lyrics for the song you are looking for.\nHere's the album page, maybe you can find the song and add the lyrics manually.\n", 
                "yellow"
            ))
            outputs.append((
                albumPath, 
                "blue"
            ))
            #webbrowser.open(albumPath)
    else:
        outputs.append((
            "lyrics status code: -> " + response.status_code.__str__() + "\n", 
            "green"
        ))
        outputs.append((
            "Lyrics Found\n", 
            "green"
        ))
        #webbrowser.open(lyrics_path)
        RipLyrics(lyrics_path)

def PrintText(message, color):
    # Placeholder for the PrintText function
    print(f"{color}: {message}")
