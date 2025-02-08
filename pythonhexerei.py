#!/bin/usr/env python

# HTML-Datei öffnen und einlesen
def modify_html(file_path, new_text, htmltag):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
    
    # Tag finden und Inhalt ändern
    tag = soup.find(htmltag)
    if tag:
        tag.string = new_text
    else:
        print("Kein " + htmltag + "-Tag gefunden!")
        return
    
    # Geänderten Inhalt zurück in die Datei schreiben
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))
    
    print(htmltag + "-Tag erfolgreich geändert!")

if __name__ == "__main__":

    import subprocess
    import sys
    import os

    def install(package):
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    try:
        install("beautifulsoup4")
    except:
        exit() 

    from bs4 import BeautifulSoup

    datei_pfad = 'public/index.html' 
    neuer_text = 'HEX HEX'
    modify_html(datei_pfad, neuer_text, "h1")
