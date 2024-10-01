import requests
from bs4 import BeautifulSoup
import unicodedata

outputs = [] # List to hold the outputs of the search
global failed

# Global variables
global artistName, songName, albumName
global backupArtistName, backupSongName

def getVariables(artist, song_name, album):
    global artistName, songName, albumName, failed
    global backupArtistName, backupSongName
    failed = False
    outputs.clear() # Clear the outputs list before starting a new search

    artistName = artist
    songName = song_name
    albumName = album

    #these are needed for the recursive search
    backupArtistName = artist
    backupSongName = song_name

    # Remove accents from the names
    songName = unicodedata.normalize('NFKD', songName).encode('ASCII', 'ignore').decode('utf-8')
    artistName = unicodedata.normalize('NFKD', artistName).encode('ASCII', 'ignore').decode('utf-8')
    albumName = unicodedata.normalize('NFKD', albumName).encode('ASCII', 'ignore').decode('utf-8')
    # Convert the names to lowercase and replace certain characters
    replacements = [
        (" ", "-"),
        ("(", ""),
        (")", ""),
        ("'", ""),
        (",", ""),
        (".", ""),  # Dots should be replaced by hyphens, but since after a dot there is almost always a space, it is not necessary
        ("&", "and")
    ]

    # Apply the replacements
    for char, replacement in replacements:
        songName = songName.replace(char, replacement).lower()
        artistName = artistName.replace(char, replacement).lower()
        albumName = albumName.replace(char, replacement).lower()

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

        outputs.append((
            lyrics_text, 
            "default"
        ))

    else:
        if soup.find(class_='LyricsPlaceholder__Message-uen8er-2 gotKKY'):
            lyrics_containers = soup.find_all(class_='LyricsPlaceholder__Message-uen8er-2 gotKKY')
            lyrics_text = lyrics_containers[0].text
            outputs.append((lyrics_text, "default"))
        else: 
            outputs.append((
                "We're sorry, lyrics could not be retrieved for this song.\nHere's the link to the page, so you can add them manually.\n", 
                "yellow"
            ))
            outputs.append((
                lyrics_path + "\n", 
                "blue"
            ))

def main():
    global artistName, songName, albumName, failed
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
                if failed:
                    outputs.append((
                        "Artist status code: " + response.status_code.__str__() + "\n",
                        "green"
                    ))
                    outputs.append((
                        "We could not find the lyrics for the song you are looking for.\nHere's the artist page, maybe you can find the song and add the lyrics manually.\n", 
                        "yellow"
                    ))
                    outputs.append((
                        artist_path + "\n", 
                        "blue"
                    ))
                    #webbrowser.open(artist_path)
                else:
                    failed = True
                    cuts = [
                        "(", "feat", "with", "ft", "and", "&", "prod", "prod.", "produced", "by", "remix", "remixed", "remixes", "remixing"
                    ]
                    for cut in cuts:
                        if cut in backupArtistName:
                            artistName = backupArtistName.split(cut)
                        if cut in backupSongName:
                            songName = backupSongName.split(cut)

                    print(f"Hold on this is a tough one, let me try something else\nSong Name {songName}\nArtist Name {artistName}\nAlbum Name {albumName}")

                    main()
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
                albumPath + "\n", 
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
