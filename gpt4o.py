#!/bin/usr/env python
import os
import json
import sys
import re
from openai import OpenAI

#client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
client = OpenAI(api_key='sk-proj-HfNPdXrBfP3nYSvFpnDzT3BlbkFJADrJMgJjCpBvw4A4epXE')

# Prompt für die KI
BASE_PROMPT = (
    "Du bist ein spezialisierter Code-Transformer für HTML, CSS und JavaScript. "
    "Deine Aufgabe ist es, gelieferten Code nach bestimmten Kriterien zu verändern. "
    "Du gibst ausschließlich validen und vollständigen HTML-, CSS- oder JavaScript-Code zurück, "
    "ohne Kommentare oder Erklärungen. Dein Output muss als gültiges JSON-Format zurückkommen, "
    "welches ein Dictionary mit Filenamen als Keys und Code als Values enthält.\n\n"
    "Regeln:\n"
    "1. Erhalte die Code-Struktur: Bewahre die grundlegende Struktur und Funktionalität.\n"
    "2. Modifikationen nach Vorgabe: Führe nur die verlangten Änderungen durch.\n"
    "3. Kein unnötiger Text: Deine Antwort enthält ausschließlich den geänderten Code im JSON-Format.\n"
    "4. Validität: Der zurückgegebene Code muss fehlerfrei und funktionsfähig sein.\n\n"
    "Antworte NUR mit dem JSON-Format, ohne zusätzliche Erklärungen oder Text!"
)

# Verzeichnis mit den Dateien
DIRECTORY = "./public/"

# Unterstützte Dateitypen
SUPPORTED_EXTENSIONS = (".html", ".css", ".js")

def load_files(directory):
    """Liest alle unterstützten Dateien in einem Dictionary ein."""
    filedict = {}
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.endswith(SUPPORTED_EXTENSIONS):
            with open(file_path, 'r', encoding='utf-8') as file:
                filedict[filename] = file.read()
    return filedict

# Bereinige die Antwort und entferne Markdown-Formatierungen
def clean_json_response(response_text):
    """Extrahiert JSON aus einer möglichen Markdown-Antwort der KI."""
    
    # Falls die Antwort mit ```json beginnt und mit ``` endet, entferne diese sicher
    match = re.match(r"```json\s*(\{.*\})\s*```", response_text, re.DOTALL)
    
    if match:
        return match.group(1)  # JSON-Inhalt zurückgeben (ohne Backticks)

    return response_text.strip()  # Falls keine Backticks vorhanden sind, normal zurückgeben

# Sende an die KI
def send_to_ai(filedict):
    input_data = json.dumps(filedict, indent=2)
    response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": BASE_PROMPT},
                {
                    "role": "user",
                    "content": f"Ändere alle Farben zu rosatönen.\n\nHier ist der Code:\n{input_data}"
                }
            ]
    )

    try:
        # KI-Antwort bereinigen und JSON umwandeln
        cleaned_json = clean_json_response(response.choices[0].message.content)
        return json.loads(cleaned_json)
    
    except json.JSONDecodeError:
        print("❌ Fehler: Die KI hat kein gültiges JSON zurückgegeben!")
        print(f"🛑 Antwort der KI (bereinigt):\n{cleaned_json}")  # Debugging
        return {}

# Speichere transformierte Dateien
def save_transformed_files(transformed_data, directory):
    for filename, new_content in transformed_data.items():
        file_path = os.path.join(directory, filename)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f"✅ Datei gespeichert: {file_path}")

# Hauptprozess
if __name__ == "__main__":
    file_contents = load_files(DIRECTORY)
    transformed_files = send_to_ai(file_contents)
    save_transformed_files(transformed_files, DIRECTORY)
