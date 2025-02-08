#!/bin/usr/env python3
from bs4 import BeautifulSoup

# HTML-Datei öffnen und einlesen
def modify_h1_tag(file_path, new_text):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        # <h1>-Tag finden und Inhalt ändern
        h1_tag = soup.find('h1')
        if h1_tag:
            h1_tag.string = new_text
        else:
            print("Kein <h1>-Tag gefunden!")
            return 1  # Fehlercode zurückgeben, damit Jenkins es erkennt

        # Geänderten Inhalt zurück in die Datei schreiben
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(str(soup))

        print("<h1>-Tag erfolgreich geändert!")
        return 0  # Erfolgscode zurückgeben

    except Exception as e:
        print(f"Fehler beim Bearbeiten der Datei: {e}")
        return 1  # Fehlercode zurückgeben

# Beispielaufruf für Jenkins
if __name__ == "__main__":
    import sys
    import subprocess

    def install(package):
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    try:
        install("beautifulsoup4")
    except Exception as e:
        print("Cannot install packages")
        sys.exit()
    exit_code = modify_h1_tag('public/index.html', 'Neuer H1-Inhalt')
    sys.exit(exit_code)