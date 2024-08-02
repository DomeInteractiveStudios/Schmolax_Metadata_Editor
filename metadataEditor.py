import tkinter as tk
import webbrowser
import re
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import mutagen
from mutagen.id3 import ID3, USLT, TIT2, TPE1, TALB, TDRC, TCON, APIC
from mutagen.flac import FLAC, Picture
import ctypes
from io import BytesIO
file_path = ""
file_name = ""

from geniusSearch import getVariables


e1 = None  # Song Name field
e2 = None  # Artist field
e3 = None  # Album field
e4 = None  # Year field
e5 = None  # Genre field
lyric_text_field = None  # Lyrics field
image_label = None  # Image label field
no_img_text = None  # Placeholder for no image

song_name = ""
artist = ""
album = ""
year = ""
lyrics = ""
genre = ""
image = None
no_metadata = False

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
    global file_path, file_name
    file_path = filedialog.askopenfilename()
    if(file_path != ""):
        if(file_path.endswith(".mp3") or file_path.endswith(".flac")):
            file_name = file_path.split("/")[-1]
            get_file_metadata(file_path)
            if not e1:
                show_entry_fields()
            update_entry_fields()
        else:
            CleanText()
            PrintText("Invalid file format. Please select an MP3 or FLAC file\n", "red")

def show_entry_fields():
    global e1, e2, e3, e4, e5, lyric_text_field, image_label, no_img_text

    # Create a notebook widget for tabs
    notebook = ttk.Notebook(root)
    notebook.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    # Create frames for the tabs
    tab1 = tk.Frame(notebook, width=380, height=600)
    tab2 = tk.Frame(notebook, width=380, height=600)
    tab3 = tk.Frame(notebook, width=380, height=600)

    tab1.grid_propagate(False)
    tab2.grid_propagate(False)
    tab3.grid_propagate(False)

    notebook.add(tab1, text='Song Metadata')
    notebook.add(tab2, text='Lyrics')
    notebook.add(tab3, text='Cover Art')

    # Add an image to tab3
    image_label = tk.Label(tab3)
    image_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
    if image:
        update_image()
    else:
        no_img_text = tk.Text(tab3, height=3, width=50)
        no_img_text.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        no_img_text.insert(tk.END, "No Cover Art Found")
        no_img_text.configure(state=tk.DISABLED)
    
    # Add change cover art button
    button_change_cover = tk.Button(tab3, text="Change Cover Art", command=get_cover_art)
    button_change_cover.grid(row=2, column=0, columnspan=2, padx=20, pady=10)

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
    tk.Label(tab1, text="Year").grid(row=5, column=0, padx=10, pady=5, sticky="e")
    tk.Label(tab1, text="Genre").grid(row=6, column=0, padx=10, pady=5, sticky="e")

    e1 = tk.Entry(tab1)
    e2 = tk.Entry(tab1)
    e3 = tk.Entry(tab1)
    e4 = tk.Entry(tab1)
    e5 = tk.Entry(tab1)

    e1.grid(row=2, column=1, padx=10, pady=5, sticky="w")
    e2.grid(row=3, column=1, padx=10, pady=5, sticky="w")
    e3.grid(row=4, column=1, padx=10, pady=5, sticky="w")
    e4.grid(row=5, column=1, padx=10, pady=5, sticky="w")
    e5.grid(row=6, column=1, padx=10, pady=5, sticky="w")

def update_entry_fields():
    global lyrics
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
        e4.insert(0, year)
    if lyric_text_field:
        lyrics_to_display = lyrics.replace('\r', '\n').replace('\u2005', ' ')
        lyric_text_field.delete(1.0, tk.END)
        lyric_text_field.insert(tk.END, lyrics_to_display)
    if e5:
        e5.delete(0, tk.END)
        e5.insert(0, genre)

    if image_label:
        update_image()

def update_image():
    global image, image_label, no_img_text
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

def get_file_metadata(file_path):
    global song_name, artist, album, year, lyrics, genre, image, no_metadata
    no_metadata = False
    audio = mutagen.File(file_path, easy=True)
    
    if audio:
        if audio.get("title", [""])[0] != "": song_name = audio.get("title", [""])[0]
        if audio.get("artist", [""])[0] != "": artist = audio.get("artist", [""])[0]
        if audio.get("album", [""])[0] != "": album = audio.get("album", [""])[0]
        if audio.get("date", [""])[0] != "": 
            temp_year = audio.get("date", [""])[0]
            year = temp_year.split("-")[0] if temp_year else ""
        if audio.get("genre", [""])[0] != "": genre = audio.get("genre", [""])[0]
        
        # Check if the file is an MP3 file and use ID3 tags if it is
        if file_path.endswith(".mp3"):
            audio = ID3(file_path)
            lyrics = ""
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
            lyrics = audio.get("lyrics", [""])[0]
        
        CleanText()
        PrintText("File loaded successfully: " + file_name + "\n", "default")
    else:
        song_name = ""
        artist = ""
        album = ""
        year = ""
        lyrics = ""
        genre = ""
        image = None
        no_metadata = True
        CleanText()
        PrintText("File loaded successfully: " + file_name + "\n", "default")
        PrintText("No metadata found for file: " + file_name + "\n", "yellow")

def get_cover_art():
    global image
    image_path = filedialog.askopenfilename()
    if image_path:
        if image_path.endswith(".jpg") or image_path.endswith(".jpeg"):
            with open(image_path, "rb") as img_file:
                image = img_file.read()
            update_entry_fields()
        else:
            PrintText("Invalid image format. Please select a JPG/JPEG file\n", "red")

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



def apply_changes():
    global song_name, artist, album, year, lyrics, genre, image, no_metadata

    song_name = e1.get().strip()
    artist = e2.get().strip()
    album = e3.get().strip()
    year = e4.get().strip()
    genre = e5.get().strip()
    lyrics = lyric_text_field.get(1.0, tk.END).strip()

    if file_path.endswith(".mp3"):
        audio = ID3(file_path)
        if no_metadata:
            attributes = [("TIT2", song_name), ("TPE1", artist), ("TALB", album),
                          ("TDRC", year), ("TCON", genre), ("USLT", lyrics)]
            for tag, value in attributes:
                if tag == "USLT":
                    if tag not in audio:
                        audio.add(USLT(encoding=3, lang=u'eng', desc=u'desc', text=value))
                    else:
                        audio[tag] = USLT(encoding=3, lang=u'eng', desc=u'desc', text=value)
                else:
                    if tag not in audio:
                        audio.add(eval(f"{tag}(encoding=3, text=value)"))
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
        audio.save()

def save_changes():
    global no_metadata

    if no_metadata: 
        apply_changes()
        PrintText("Metadata fields have been created\n", "green")
        no_metadata = False
    
    apply_changes()
    PrintText("Changes Saved\n", "green")

# Main loop
root = tk.Tk()
myappid = 'dome.schmolax_metadata.dolly.v_0.1'  # arbitrary string
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
button_select_file = tk.Button(root, text="Select File", command=get_file_path)
button_select_file.grid(row=0, column=0, columnspan=2, pady=10)

# Create a text widget for displaying status messages
text = tk.Text(root, height=3, width=50, font=("Californian FB", 12))
text.config(state=tk.DISABLED) 
text.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# Create text tags for different colors
text.tag_configure("red", foreground="red")
text.tag_configure("green", foreground="green")
text.tag_configure("yellow", foreground="#9c7200")
text.tag_configure("blue", foreground="blue")
text.tag_configure("default", foreground="black")

KNOWN_TAGS = {"red", "green", "yellow", "blue", "default"}

root.mainloop()
