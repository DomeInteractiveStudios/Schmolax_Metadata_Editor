import tkinter as tk
import metadataEditor

def PrintText(message, color):
    text = metadataEditor.text
    text.insert(tk.END, message, color); 
    text.see(tk.END)