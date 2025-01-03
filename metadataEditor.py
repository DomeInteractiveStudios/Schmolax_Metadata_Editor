import os
import sys
import locale

# Ensure the script can handle non-ASCII characters
locale.setlocale(locale.LC_ALL, '')
sys.stdout.reconfigure(encoding='utf-8')
import platform
import tkinter as tk
import webbrowser
import re
import time
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, USLT, TIT2, TPE1, TALB, TDRC, TCON, APIC, TPE2, TCOM, TRCK, TPOS, COMM, TXXX, TBPM
from mutagen.flac import FLAC, Picture
import ctypes
from io import BytesIO
file_path = ""
file_name = ""

from geniusSearch import getVariables
from musicBrainzSearch import GetImgVariables

notebook = None  # Notebook widget
tab1 = None  # Song Info tab
tab2 = None  # Lyrics tab
tab3 = None  # Cover Art tab
tab4 = None  # Read Only tab

e1 = None  # Song Name field
e2 = None  # Artist field
e3 = None  # Album field
e4 = None  # Abum Artist field
e5 = None  # Composer field
e6 = None  # Track Number field
e7 = None  # Disc Number field
e8 = None  # Year field
e9 = None  # Genre field
e10 = None # BPM field
e11 = None # Comment field
lyric_text_field = None  # Lyrics field
image_label = None  # Image label field
no_img_text = None  # Placeholder for no image

# Metadata fields
song_name = ""
artist = ""
album = ""
album_artist = ""
composer = ""
track_number = ""
total_tracks = ""
disc_number = ""
total_discs = ""
year = ""
genre = ""
bpm = ""
comment = ""
lyrics = ""
image = None

#Read Only Metadata Fields
kind = ""
duration = ""
size = ""
bit_rate = ""
sample_rate = ""
channels = ""

# Flags to check metadata completion
no_metadata = False
num_of_saves = 0
current_file_path = ""
current_tab = ""
# multipleFiles = []
# outer_notebooks = []

# block features
# allowMultipleFiles = False

# def openSettings():
#     print("Settings opened")

# def remove_all_notebooks():
#     #print(f"number of outer notebooks: {len(outer_notebooks)}\n")
#     if len(outer_notebooks) != 0:
#         #print("removing all outer notebooks\n")
#         for notebook in outer_notebooks:
#             #print(f"name: {notebook}\n")
#             notebook.destroy()
#         outer_notebooks.clear()

def CleanText():
    text.config(state=tk.NORMAL)  
    text.delete(1.0, tk.END) 
    text.config(state=tk.DISABLED)  

def PrintText(message, color):

    text.config(state=tk.NORMAL)  # Allow text insertion
    text.insert(tk.END, message, color)

    # Define the regex pattern to detect URLs
    url_pattern = re.compile(r'(https?://\S+)')

    # Find all URLs in the message and tag them
    for url in url_pattern.findall(message):
        start_idx = text.search(url, '1.0', tk.END)
        if start_idx:
            # Parse the line and column
            line, col = start_idx.split('.')
            start_pos = f"{line}.{col}"

            # Compute the end position
            end_col = int(col) + len(url)
            end_pos = f"{line}.{end_col}"

            # Add and configure the tag
            text.tag_add('link', start_pos, end_pos)
            text.tag_config('link', foreground='blue', underline=1)

            # Bind the link to open in a web browser
            text.tag_bind('link', '<Button-1>', lambda e, url=url: webbrowser.open(url))

    text.config(state=tk.DISABLED)  # Prevent typing in the Text widget
    text.see(tk.END)  # Ensure the latest text is visible

def get_file_path():
    global file_path, file_name, tab1, notebook
    file_path = filedialog.askopenfilename()
    if file_path:
        # remove_all_notebooks()
        # if len(multipleFiles) != 0: return
        if(file_path.endswith(".mp3") or file_path.endswith(".flac")):
            num_of_saves = 0
            file_name = file_path.split("/")[-1]
            current_file_path = file_path   
            get_file_metadata(file_path)
            if not e1:
                show_entry_fields(root)
            update_entry_fields()
        else:
            CleanText()
            PrintText("Invalid file format. Please select an MP3 or FLAC file\n", "red")
    else: 
        if current_file_path:
            get_file_metadata(current_file_path)
            update_entry_fields()
        else:
            PrintText("No file selected\n", "red")
    if notebook and tab1: 
        notebook.select(tab1)

# def get_folder_path():
#     if not allowMultipleFiles:
#         PrintText("This feature is not available at the moment\n", "yellow")
#         return
#     folder_path = filedialog.askdirectory()
#     if folder_path:
#         multipleFiles.clear()
#         remove_all_notebooks()  # Clear all previous notebooks
#         print(f"Current number of files in folder: {len(multipleFiles)}")
#         if len(multipleFiles) != 0: return
#         for file in os.listdir(folder_path):
#             if file.endswith(".mp3") or file.endswith(".flac"):
#                 multipleFiles.append(os.path.join(folder_path, file))
#         if len(multipleFiles) > 1:
#             print(f"Number of files in folder: {len(multipleFiles)}")
#             notebook = ttk.Notebook(root)
#             notebook.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
#             outer_notebooks.append(notebook)  # Keep track of the outer notebook

#             for i, file_path in enumerate(multipleFiles, start=1):
#                 get_file_metadata(file_path)

#                 tab = ttk.Frame(notebook)
#                 notebook.add(tab, text=f'Song {i}')

#                 inner_notebook = show_entry_fields(tab)

#                 if not e1:  # Assuming e1 is a condition to check for the first time
#                     show_entry_fields(inner_notebook)
#                 update_entry_fields()
#         else:
#             file_path = multipleFiles[0]
#             get_file_metadata(file_path)
#             if not e1:
#                 show_entry_fields(root)
#             update_entry_fields()
#     else:
#         CleanText()
#         PrintText("No MP3 or FLAC files found in the folder\n", "red")

#     for file in multipleFiles:
#         file_name = file.split("/")[-1]
#         PrintText(f"Song {multipleFiles.index(file) + 1}: {file_name}\n", "default")


def show_entry_fields(origin):
    global e1, e2, e3, e4, e5, e6, es6, e7, es7, e8, e9, e10, e11, lyric_text_field, image_label, no_img_text
    global tab1, tab2, tab3, tab4, notebook

    # Create a notebook widget for tabs
    notebook = ttk.Notebook(origin)
    notebook.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    # Create frames for the tabs
    tab1 = tk.Frame(notebook, width=380, height=600)
    tab2 = tk.Frame(notebook, width=380, height=600)
    tab3 = tk.Frame(notebook, width=380, height=600)
    tab4 = tk.Frame(notebook, width=380, height=600)

    tab1.grid_propagate(False)
    tab2.grid_propagate(False)
    tab3.grid_propagate(False)
    tab4.grid_propagate(False)

    notebook.add(tab1, text='Song Info')
    notebook.add(tab2, text='Lyrics')
    notebook.add(tab3, text='Cover Art')
    notebook.add(tab4, text='Read Only')
    # Bind tab switching event
    notebook.bind("<<NotebookTabChanged>>", on_tab_switch)

    # Add an image to tab3
    image_label = tk.Label(tab3)
    image_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
    if image:
        update_image()
    else:
        no_img_text = tk.Text(tab3, height=3, width=50) #always create the no_img_text field, just hide it if there is an image
        no_img_text.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        no_img_text.insert(tk.END, "No Cover Art Found")
        no_img_text.configure(state=tk.DISABLED)

    # Add change cover art button
    button_change_cover = tk.Button(tab3, text="Change Cover Art", command=get_cover_art).grid(row=2, column=0, columnspan=2, padx=20, pady=10)
    button_save_cover = tk.Button(tab3, text="Save Cover Art", command=download_cover_art).grid(row=3, column=0, columnspan=2, padx=20, pady=10)
    button_search_cover = tk.Button(tab3, text="Search Cover Art Online", command=search_cover_art_online).grid(row=4, column=0, columnspan=2, padx=20, pady=10)

    # Add a new text field to tab2
    lyric_text_field = tk.Text(tab2, height=30, width=40, wrap=tk.WORD)
    lyric_text_field.grid(row=0, column=0, padx=10, pady=10)
    button_search_lyrics = tk.Button(tab2, text="Search Lyrics Online", command=search_lyrics_online)
    button_search_lyrics.grid(row=1, column=0, padx=20, pady=10)

    button_save = tk.Button(root, text="Save", command=save_changes)
    button_save.grid(row=7, column=0, columnspan=2, pady=10)

    tk.Label(tab1, text="Song Name").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    tk.Label(tab1, text="Artist").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    tk.Label(tab1, text="Album").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    tk.Label(tab1, text="Album Artist").grid(row=5, column=0, padx=10, pady=5, sticky="e")
    tk.Label(tab1, text="Composer").grid(row=6, column=0, padx=10, pady=5, sticky="e")
    tk.Label(tab1, text="Track Number").grid(row=7, column=0, padx=10, pady=5, sticky="e")
    tk.Label(tab1, text=" of ").grid(row=7, column=2, padx=10, pady=5, sticky="e")
    tk.Label(tab1, text="Disc Number").grid(row=8, column=0, padx=10, pady=5, sticky="e")
    tk.Label(tab1, text=" of ").grid(row=8, column=2, padx=10, pady=5, sticky="e")
    tk.Label(tab1, text="Year").grid(row=9, column=0, padx=10, pady=5, sticky="e")
    tk.Label(tab1, text="Genre").grid(row=10, column=0, padx=10, pady=5, sticky="e")
    tk.Label(tab1, text="BPM").grid(row=11, column=0, padx=10, pady=5, sticky="e")
    tk.Label(tab1, text="Comment").grid(row=12, column=0, padx=10, pady=5, sticky="e")

    e1 = tk.Entry(tab1)
    e2 = tk.Entry(tab1)
    e3 = tk.Entry(tab1)
    e4 = tk.Entry(tab1)
    e5 = tk.Entry(tab1)
    e6 = tk.Entry(tab1)
    es6 = tk.Entry(tab1)
    e7 = tk.Entry(tab1)
    es7 = tk.Entry(tab1)
    e8 = tk.Entry(tab1)
    e9 = tk.Entry(tab1)
    e10 = tk.Entry(tab1)
    e11 = tk.Text(tab1, height=10, width=30, wrap=tk.WORD)
    e11 = tk.Text(tab1, height=10, width=15, wrap=tk.WORD)

    entries = [e1, e2, e3, e4, e5, e6, es6, e7, es7, e8, e9, e10, e11]
    for entry in entries:
        entry.pack()
        entry.bind("<KeyRelease>", on_entry_modified)

    e1.grid(row=2, column=1, padx=10, pady=5, sticky="w") # Song Name
    e2.grid(row=3, column=1, padx=10, pady=5, sticky="w") # Artist
    e3.grid(row=4, column=1, padx=10, pady=5, sticky="w") # Album
    e4.grid(row=5, column=1, padx=10, pady=5, sticky="w") # Album Artist
    e5.grid(row=6, column=1, padx=10, pady=5, sticky="w") # Composer
    e6.grid(row=7, column=1, padx=10, pady=5, sticky="w") # Track Number
    es6.grid(row=7, column=3, padx=10, pady=5, sticky="w") # Total Tracks
    e7.grid(row=8, column=1, padx=10, pady=5, sticky="w") # Disc Number
    es7.grid(row=8, column=3, padx=10, pady=5, sticky="w") # Total Discs
    e8.grid(row=9, column=1, padx=10, pady=5, sticky="w") # Year
    e9.grid(row=10, column=1, padx=10, pady=5, sticky="w") # Genre
    e10.grid(row=11, column=1, padx=10, pady=5, sticky="w") # BPM
    e11.grid(row=12, column=1, padx=10, pady=5, sticky="w") # Comment

    # Read Only Metadata Fields Tab
    tk.Label(tab4, text="Kind: ").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    tk.Label(tab4, text="Duration: ").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    tk.Label(tab4, text="Size: ").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    tk.Label(tab4, text="Bit Rate: ").grid(row=5, column=0, padx=10, pady=5, sticky="e")
    tk.Label(tab4, text="Sample Rate: ").grid(row=6, column=0, padx=10, pady=5, sticky="e")
    tk.Label(tab4, text="Channels: ").grid(row=7, column=0, padx=10, pady=5, sticky="e")

    tk.Label(tab4, text=kind).grid(row=2, column=1, padx=10, pady=5, sticky="e")
    tk.Label(tab4, text=duration).grid(row=3, column=1, padx=10, pady=5, sticky="e")
    tk.Label(tab4, text=size).grid(row=4, column=1, padx=10, pady=5, sticky="e")
    tk.Label(tab4, text=bit_rate).grid(row=5, column=1, padx=10, pady=5, sticky="e")
    tk.Label(tab4, text=sample_rate).grid(row=6, column=1, padx=10, pady=5, sticky="e")
    tk.Label(tab4, text=channels).grid(row=7, column=1, padx=10, pady=5, sticky="e")


def update_entry_fields():
    global lyrics, song_name, artist, album, album_artist, composer, track_number, total_tracks, disc_number, total_discs, year, genre, bpm, comment, image, image_label, no_img_text
    if e1:
        e1.delete(0, tk.END)
        e1.insert(0, song_name)
    if e2:
        e2.delete(0, tk.END)
        e2.insert(0, artist)
    if e3:
        e3.delete(0, tk.END)
        e3.insert(0, album)
    if e4:
        e4.delete(0, tk.END)
        e4.insert(0, album_artist)
    if e5:
        e5.delete(0, tk.END)
        e5.insert(0, composer)
    if e6:
        e6.delete(0, tk.END)
        e6.insert(0, track_number)
    if es6:
        es6.delete(0, tk.END)
        es6.insert(0, total_tracks)
    if e7:
        e7.delete(0, tk.END)
        e7.insert(0, disc_number)
    if es7:
        es7.delete(0, tk.END)
        es7.insert(0, total_discs)
    # Year Field with Fallback
    if e8:
        e8.delete(0, tk.END)
        e8.insert(0, year if year else "")

    # Genre Field with Fallback
    if e9:
        e9.delete(0, tk.END)
        e9.insert(0, genre if genre else "Unknown Genre")
    if e10:
        e10.delete(0, tk.END)
        e10.insert(0, bpm)
    if e11:
        e11.delete(1.0, tk.END)
        e11.insert(tk.END, "")
        #print("Before insertion, comment variable:", repr(comment))
        e11.insert(tk.END, comment)
    if lyric_text_field:
        lyrics_to_display = lyrics.replace('\r', '\n').replace('\u2005', ' ')
        lyric_text_field.delete(1.0, tk.END)
        lyric_text_field.insert(tk.END, lyrics_to_display)

    if image_label:
        update_image()

def update_image():
    global image, image_label, no_img_text, tab3
    if image:
        try:
            img = Image.open(BytesIO(image))
            img = img.resize((360, 360), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(img)
            image_label.config(image=img)
            image_label.image = img  # Keep a reference to avoid garbage collection

            # Remove the placeholder text if it exists
            if no_img_text:
                no_img_text.grid_forget()
                no_img_text = None
        except Exception as e:
            print(f"Error loading image: {e}")
            PrintText("Invalid image format. Please select a JPG/JPEG file\n", "red")
    else:
        print("No image found")
        image_label.config(image="")
        image_label.image = None
        # Create a placeholder text if it doesn't exist
        if not no_img_text: 
            no_img_text = tk.Text(tab3, height=3, width=50)
            no_img_text.grid(row=1, column=0, columnspan=2, padx=20, pady=10)
        no_img_text.insert(tk.END, "No Cover Art Found")
        no_img_text.configure(state=tk.DISABLED)

def get_file_metadata(file_path):
    global song_name, artist, album, album_artist, composer, track_number, total_tracks, disc_number, total_discs, year, lyrics, genre, bpm, comment, image, no_metadata
    global kind, duration, size, bit_rate, sample_rate, channels, encoding
    no_metadata = False
    total_tracks_set_by_track_number = False
    audio = mutagen.File(file_path, easy=True)

    if audio:
        if audio.get("title", [""])[0] != "": song_name = audio.get("title", [""])[0]
        else: song_name = file_name.split(".")[0]
        if audio.get("artist", [""])[0] != "": artist = audio.get("artist", [""])[0]
        else: artist = ""
        if audio.get("album", [""])[0] != "": album = audio.get("album", [""])[0]
        else: album = ""
        if audio.get("albumartist", [""])[0] != "": album_artist = audio.get("albumartist", [""])[0]
        else: album_artist = ""
        if audio.get("composer", [""])[0] != "": composer = audio.get("composer", [""])[0]
        else: composer = ""
        if audio.get("tracknumber", [""])[0] != "": 
            trackNum = audio.get("tracknumber", [""])[0]
            track_number = trackNum.split("/")[0] if "/" in trackNum else trackNum
            total_tracks = trackNum.split("/")[1] if "/" in trackNum else ""
        else: track_number = ""
        if audio.get("totaltracks", [""])[0] != "": 
            total_tracks = audio.get("totaltracks", [""])[0] #get total tracks only if not set by track number
        else: 
            if(not total_tracks): total_tracks = ""
        if audio.get("discnumber", [""])[0] != "": 
            discNum = audio.get("discnumber", [""])[0]
            disc_number = discNum.split("/")[0] if "/" in discNum else discNum
            total_discs = discNum.split("/")[1] if "/" in discNum else ""
        else: disc_number = ""
        if audio.get("totaldiscs", [""])[0] != "": 
            total_discs = audio.get("totaldiscs", [""])[0]
        else: 
            if(not total_discs): total_discs = ""
        if audio.get("comment", [""])[0] != "": comment = audio.get("comment", [""])[0] #? get comment before year so that the year can be added at the end of the comment
        else: comment = ""
        if audio.get("date", [""])[0] != "" and len(audio["date"]) > 0:
            temp_year = audio.get("date", [""])[0]
            if("-" in temp_year): 
                comment += f"\nFull date: {temp_year}\n" #? if the year has more than just the year save the original date as a comment

            # Check if there’s a 4-digit year in the entire date string
            dateSegments = temp_year.split("-") if "-" in temp_year else [temp_year]

            # Loop through each segment to find a 4-digit year
            for segment in dateSegments:
                if len(segment) == 4 and segment.isdigit():
                    year = segment
                    break  # Stop as soon as we find a valid year
            else:
                year = ""  # Set to empty if no 4-digit year was found
        else:
            year = ""
        # Check if the "genre" key exists and if the associated list is non-empty
        if "genre" in audio and len(audio["genre"]) > 0 and audio["genre"][0] != "": genre = audio["genre"][0]
        else: genre = ""
        if audio.get("bpm", [""])[0] != "": bpm = audio.get("bpm", [""])[0]
        else: bpm = ""

        # Check if the file is an MP3 file and use ID3 tags if it is
        if file_path.endswith(".mp3"):
            audio = ID3(file_path)
            lyrics = ""
            image = None
            for tag in audio.values():
                if isinstance(tag, USLT):
                    lyrics += tag.text
                elif isinstance(tag, APIC):
                    image = tag.data

        # Check if the file is a FLAC file and use FLAC tags if it is
        elif file_path.endswith(".flac"):
            audio = FLAC(file_path)
            lyrics = ""
            lyrics = audio.get("LYRICS", [""])[0]
            if audio.pictures:
                image = audio.pictures[0].data
            else:
                image = None
        else:
            lyrics = audio.get("lyrics", [""])[0]

        CleanText()
        PrintText("File loaded successfully: " + file_name + "\n", "default")
    else:
        song_name = ""
        artist = ""
        album = ""
        year = ""
        album_artist = ""
        composer = ""
        track_number = ""
        total_tracks = ""
        disc_number = ""
        total_discs = ""
        lyrics = ""
        genre = ""
        bpm = ""
        comment = ""
        image = None
        no_metadata = True
        CleanText()
        PrintText("File loaded successfully: " + file_name + "\n", "default")
        PrintText("No metadata found for file: " + file_name + "\n", "yellow")

    #print main info in console
    if platform.system() == 'Linux': os.system('clear')
    if platform.system() == 'Windows': os.system('cls')
    print(f"Song: {song_name}\nArtist: {artist}\nAlbum: {album}\nYear: {audio.get("date", [""])[0]}\nGenre: {genre}\n")

    def audio_duration(length): 
        hours = length // 3600  # calculate in hours 
        length %= 3600
        mins = length // 60  # calculate in minutes 
        length %= 60
        seconds = length  # calculate in seconds 

        if hours < 10: hours = f"0{hours}"
        if mins < 10: mins = f"0{mins}"
        if seconds < 10: seconds = f"0{seconds}"

        return hours, mins, seconds  # returns the duration 

    # Read Only Metadata Fields
    if file_path.endswith(".mp3") and audio: 
        audio_temp = MP3(file_path)
        kind = "MP3 File"
        length = int(audio_temp.info.length)
        hours, mins, seconds = audio_duration(length) # get the duration of the audio file
        duration = f"{hours} : {mins} : {seconds}"
        temp_size = os.stat(file_path).st_size / (1024 * 1024) # convert size to MB
        size = f"{temp_size:.2f} MB"
        bit_rate = f"{audio_temp.info.bitrate // 1000} kbps"
        #print(f"size in bytes: {os.stat(file_path).st_size * 8} bits\nchannels: {audio_temp.info.channels}\nsample rate: {audio_temp.info.sample_rate} Hz\nduration: {length} s")
        sample_rate = f"{(audio_temp.info.sample_rate // 1000):.2f} kHz"
        channels = audio_temp.info.channels
    elif file_path.endswith(".flac") and audio:
        kind = "FLAC File"
        audio_temp = FLAC(file_path)
        length = int(audio_temp.info.length)
        hours, mins, seconds = audio_duration(length) # get the duration of the audio file
        duration = f"{hours} : {mins} : {seconds}"
        temp_size = os.stat(file_path).st_size / (1024 * 1024) # convert size to MB
        size = f"{temp_size:.2f} MB"
        bit_rate = f"{audio_temp.info.bitrate // 1000} kbps"
        sample_rate = f"{(audio_temp.info.sample_rate // 1000):.2f} kHz"
        channels = audio_temp.info.channels
    else:
        kind = "unknown"
        duration = "unknown"
        size = "unknown"
        bit_rate = "unknown"
        sample_rate = "unknown"
        channels = "unknown"

def get_cover_art():
    global image
    image_path = filedialog.askopenfilename()
    if image_path:
        if image_path.endswith(".jpg") or image_path.endswith(".jpeg") or image_path.endswith(".png"):
            with open(image_path, "rb") as img_file:
                image = img_file.read()
            update_entry_fields()
        else:
            PrintText("Invalid image format. Please select a JPG/JPEG or PNG file\n", "red")

def download_cover_art():
    if image:
        suggested_file_name = f"{album}_cover.jpg" if album else "cover.jpg"
        file_path = filedialog.asksaveasfilename(defaultextension=".jpg", initialfile=suggested_file_name, filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "wb") as f:
                f.write(image)
            PrintText(f"Cover art downloaded to {file_path}\n", "green")
    else:
        PrintText("No cover art to download\n", "red")

def is_tag(value):
    # Check if the value is in the set of known tags
    return value.lower() in KNOWN_TAGS

def search_lyrics_online():
    global lyrics
    i=0
    outputs = getVariables(artist, song_name, album)

    #print("outputs length: ", len(outputs))
    for output in outputs: 
        array = []
        for value in output:
            array.append(value)

        # Determine which element is the tag and which is the message
        if is_tag(array[0]):
            tag, message = array[0], array[1]
        else:
            message, tag = array[0], array[1]
        #print("got ", i+1, " message from function" )
        if len(outputs) == 3:
            #print("length is 3 -> ", i)
            if(i==2): 
                lyric_text_field.delete(1.0, tk.END)
                lyric_text_field.insert(tk.END, message)
                lyrics = message
            else: 
                PrintText(message, tag)
        else:
            #print("now printed ", i+1, " message")
            PrintText(message, tag)
        i+=1

    update_entry_fields()

def search_cover_art_online():
    GetImgVariables(artist, album)

def apply_changes():
    global song_name, artist, album, album_artist, composer, track_number, total_tracks, disc_number, total_discs, year, lyrics, genre, bpm, comment, image, no_metadata

    song_name = e1.get().strip()
    artist = e2.get().strip()
    album = e3.get().strip()
    album_artist = e4.get().strip()
    composer = e5.get().strip()
    track_number = e6.get().strip()
    total_tracks = es6.get().strip()
    disc_number = e7.get().strip()
    total_discs = es7.get().strip()
    year = e8.get().strip()
    genre = e9.get().strip()
    bpm = e10.get().strip()
    comment = e11.get(1.0, tk.END).strip()
    lyrics = lyric_text_field.get(1.0, tk.END).strip()

    if file_path.endswith(".mp3"):
        audio = ID3(file_path)
        if no_metadata:
            attributes = [("TIT2", song_name), ("TPE1", artist), ("TALB", album),
                          ("TDRC", year), ("TCON", genre), ("USLT", lyrics),
                          ("TPE2", album_artist), ("TCOM", composer),
                          ("TRCK", track_number), ("TPOS", disc_number),
                          ("TXXX:totaltracks", total_tracks), ("TXXX:totaldiscs", total_discs),
                          ("TBPM", bpm), ("COMM", comment)]
            for tag, value in attributes:
                if tag == "USLT":
                    if tag not in audio:
                        audio.add(USLT(encoding=3, lang=u'eng', desc=u'desc', text=value))
                    else:
                        audio[tag] = USLT(encoding=3, lang=u'eng', desc=u'desc', text=value)
                elif tag == "COMM":
                    if tag not in audio:
                        audio.add(COMM(encoding=3, lang=u'eng', desc=u'desc', text=value))
                    else:
                        audio[tag] = COMM(encoding=3, lang=u'eng', desc=u'desc', text=value)
                elif tag.startswith("TXXX:"):
                    txxx_key = tag.split(":")[1]
                    if txxx_key not in audio:
                        audio.add(TXXX(encoding=3, desc=txxx_key, text=value))
                    else:
                        audio[tag] = TXXX(encoding=3, desc=txxx_key, text=value)
                else:
                    if tag not in audio:
                            audio[tag] = eval(f"{tag}(encoding=3, text=value)")
                    else:
                        audio[tag] = eval(f"{tag}(encoding=3, text=value)")
        else:
            if "TIT2" not in audio:
                audio.add(TIT2(encoding=3, text=song_name))
            else:
                audio["TIT2"] = TIT2(encoding=3, text=song_name)
            if "TPE1" not in audio:
                audio.add(TPE1(encoding=3, text=artist))
            else:
                audio["TPE1"] = TPE1(encoding=3, text=artist)
            if "TALB" not in audio:
                audio.add(TALB(encoding=3, text=album))
            else:
                audio["TALB"] = TALB(encoding=3, text=album)
            if "TDRC" not in audio:
                audio.add(TDRC(encoding=3, text=year))
            else:
                audio["TDRC"] = TDRC(encoding=3, text=year)
            if "TCON" not in audio:
                audio.add(TCON(encoding=3, text=genre))
            else:
                audio["TCON"] = TCON(encoding=3, text=genre)
            if "USLT" not in audio:
                audio.add(USLT(encoding=3, lang=u'eng', desc=u'desc', text=lyrics))
            else:
                audio["USLT"] = USLT(encoding=3, lang=u'eng', desc=u'desc', text=lyrics)
            if "TPE2" not in audio:
                audio.add(TPE2(encoding=3, text=album_artist))
            else:
                audio["TPE2"] = TPE2(encoding=3, text=album_artist)
            if "TCOM" not in audio:
                audio.add(TCOM(encoding=3, text=composer))
            else:
                audio["TCOM"] = TCOM(encoding=3, text=composer)
            if "TRCK" not in audio:
                audio.add(TRCK(encoding=3, text=track_number))
            else:
                audio["TRCK"] = TRCK(encoding=3, text=track_number)
            if "TPOS" not in audio:
                audio.add(TPOS(encoding=3, text=disc_number))
            else:
                audio["TPOS"] = TPOS(encoding=3, text=disc_number)
            if "TXXX:totaltracks" not in audio:
                audio.add(TXXX(encoding=3, desc="totaltracks", text=total_tracks))
            else:
                audio["TXXX:totaltracks"] = TXXX(encoding=3, desc="totaltracks", text=total_tracks)
            if "TXXX:totaldiscs" not in audio:
                audio.add(TXXX(encoding=3, desc="totaldiscs", text=total_discs))
            else:
                audio["TXXX:totaldiscs"] = TXXX(encoding=3, desc="totaldiscs", text=total_discs)
        if image:
            if "APIC" in audio:
                audio.delall("APIC")
            audio.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Front cover', data=image))
        audio.save()
    elif file_path.endswith(".flac"):
        audio = FLAC(file_path)
        audio["title"] = song_name
        audio["artist"] = artist
        audio["album"] = album
        audio["date"] = year
        audio["genre"] = genre
        audio["albumartist"] = album_artist
        audio["composer"] = composer
        audio["tracknumber"] = track_number
        audio["discnumber"] = disc_number
        audio["totaltracks"] = total_tracks
        audio["totaldiscs"] = total_discs
        audio["bpm"] = bpm
        audio["comment"] = comment
        if lyrics:
            audio["LYRICS"] = lyrics
        if image:
            picture = Picture()
            picture.data = image
            picture.type = 3  # Cover (front)
            picture.mime = "image/jpeg"
            audio.clear_pictures()  # Remove all existing pictures
            audio.add_picture(picture)
        audio.save()
    else:
        audio = mutagen.File(file_path, easy=True)
        audio["title"] = song_name
        audio["artist"] = artist
        audio["album"] = album
        audio["date"] = year
        audio["genre"] = genre
        audio["lyrics"] = lyrics
        audio["albumartist"] = album_artist
        audio["composer"] = composer
        audio["tracknumber"] = track_number
        audio["discnumber"] = disc_number
        audio["totaltracks"] = total_tracks
        audio["totaldiscs"] = total_discs
        audio["bpm"] = bpm
        audio["comment"] = comment
        audio.save()

def save_changes():
    global no_metadata, has_unsaved_changes, num_of_saves, current_tab

    num_of_saves += 1

    if no_metadata: 
        apply_changes()
        PrintText("Metadata fields have been created\n", "green")
        no_metadata = False

    apply_changes()
    PrintText(f"Changes Saved {num_of_saves}: {current_tab}\n", "green")

    has_unsaved_changes = False  # Reset flag after saving changes

# Callback for when an entry is modified
def on_entry_modified(event):
    global has_unsaved_changes
    has_unsaved_changes = True
    #print("Change detected")

# Function to handle tab switching
def on_tab_switch(event):
    global has_unsaved_changes, current_tab
    if has_unsaved_changes:
        save_changes()  # Save changes before switching tabs

    current_tab = event.widget.tab(event.widget.select(), "text")
    #print("Tab switched")

# Main loop
root = tk.Tk()
myappid = 'dome.schmolax_metadata.dolly.v_0.5'  # version string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

# Change window title
root.title("Schmolax Metadata Editor")
# Change window icon
root.iconbitmap("Icons/schmolax.ico")

# Create a canvas widget with a fixed size
canvas = tk.Canvas(root, width=500, height=800)
canvas.grid(row=0, column=0, columnspan=2, rowspan=6)
canvas.grid_propagate(False)  # Prevent the canvas from resizing

# Create a button widget for selecting files
button_select_file = tk.Button(root, text="Open File", command=get_file_path)
button_select_file.grid(row=0, column=0, columnspan=2, pady=10)
# button_select_folder = tk.Button(root, text="Open Folder", command=get_folder_path)
# button_select_folder.grid(row=1, column=0, columnspan=2, pady=10)

#create settings button on the top right corner
# button_settings = tk.Button(root, text="⚙️", command=openSettings)
# button_settings.grid(row=0, column=2, columnspan=2, pady=10)

# Create a text widget for displaying status messages
text = tk.Text(root, height=3, width=50, font=("Californian FB", 12))
text.config(state=tk.DISABLED) 
text.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# Track unsaved changes
has_unsaved_changes = False

# Create text tags for different colors
text.tag_configure("red", foreground="red")
text.tag_configure("green", foreground="green")
text.tag_configure("yellow", foreground="#9c7200")
text.tag_configure("blue", foreground="blue")
text.tag_configure("default", foreground="black")

KNOWN_TAGS = {"red", "green", "yellow", "blue", "default"}

root.mainloop()