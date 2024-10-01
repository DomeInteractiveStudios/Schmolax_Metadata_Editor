import webbrowser
import requests
from bs4 import BeautifulSoup
import os
import unicodedata
import time

save_img = False
global artistName, albumName, backupAlbumName, backupArtistName


def GetImgVariables(album, artist):
    global artistName, albumName, backupAlbumName, backupArtistName

    artistName = artist
    albumName = album

    backupArtistName = artistName
    backupAlbumName = albumName

    # Remove accents from the names
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
        artistName = artistName.replace(char, replacement).lower()
        albumName = albumName.replace(char, replacement).lower()

    main()


def main():
    image_path = f"https://musicbrainz.org/search?query={albumName}+{artistName}&type=release&limit=1&method=indexed"
    response = requests.get(image_path)
    soup = BeautifulSoup(response.content, 'html.parser')

    if response.status_code != 404:
        time.sleep(1) # Wait for the page to be fully loaded

        # Continue with scraping the page
        table = soup.find('table', class_='tbl')
        tbody = table.find('tbody')
        tr = tbody.find('tr')
        td = tr.find('td')
        anchor = td.find('a')
        # Extract the href attribute
        link = anchor['href']
        full_url = f"https://musicbrainz.org{link}"  # Construct the full URL

        response = requests.get(full_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        if response.status_code != 404:

            time.sleep(1) # Wait for the page to be fully loaded

            # Find the image tag
            image_div = soup.find('div', class_='artwork-cont')
            image_p = image_div.find('p', class_='small')
            image_tag = image_p.find_all('a')[-1]
            #print(image_tag)

            # Create a new folder called TempAlbumImage if it doesn't exist
            folder_path = "../Schmolax_Metadata_Editor/TempAlbumImage"
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            # Download the album image
            image_src = image_tag['href']
            image_url = f"https:{image_src}"
            if save_img:
                img_name = albumName.replace("+", "_")
                image_filename = os.path.join(folder_path, f"{img_name}.jpg")
                response = requests.get(image_url)
                with open(image_filename, 'wb') as f:
                    f.write(response.content)

                print(f"Album image downloaded and saved as {image_filename}")
            else:
                webbrowser.open(image_url)
                print("Album image opened in browser")
        else:
            print(f"We found the album {albumName} by {artistName} on MusicBrainz, but couldn't find an image\nHere's the link to the album page: {full_url}")
    else:
        print(f"Couldn't find a reference to the album {backupAlbumName} by {backupArtistName} on MusicBrainz")