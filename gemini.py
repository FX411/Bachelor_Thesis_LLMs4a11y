#!/bin/usr/env python
import os
import json
import re
import sys
from PIL import Image
import io
from google import genai

client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

# Prompt für die KI
BASE_PROMPT = (
    "Du bist ein spezialisierter Code-Transformer für HTML, CSS und JavaScript. "
    "Zusätzlich erhältst du Bilder als Base64-codierte Strings, die du in deiner Transformation berücksichtigen kannst. "
    "Deine Aufgabe ist es, gelieferten Code nach bestimmten Kriterien zu verändern. "
    "Du gibst ausschließlich validen und vollständigen HTML-, CSS- oder JavaScript-Code zurück, "
    "ohne Kommentare oder Erklärungen. Dein Output muss als gültiges JSON-Format zurückkommen, "
    "welches ein Dictionary mit Dateinamen als Keys und Code als Values enthält. "
    "Wenn Bilder gesendet werden, passe den Code entsprechend an.\n\n"
    "Regeln:\n"
    "1. Erhalte die Code-Struktur: Bewahre die grundlegende Struktur und Funktionalität.\n"
    "2. Modifikationen nach Vorgabe: Führe nur die verlangten Änderungen durch.\n"
    "3. Kein unnötiger Text: Deine Antwort enthält ausschließlich den geänderten Code im JSON-Format.\n"
    "4. Validität: Der zurückgegebene Code muss fehlerfrei und funktionsfähig sein.\n\n"
    "Antworte NUR mit dem JSON-Format, ohne zusätzliche Erklärungen oder Text!"
)

# Verzeichnisse mit den Dateien
DIRECTORY = "./public/"
IMG_DIRECTORY = "./public/img/"

# Unterstützte Dateitypen
SUPPORTED_EXTENSIONS = (".html", ".css", ".js")
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")


def load_files(directory):
    """Liest alle unterstützten Dateien in einem Dictionary ein."""
    filedict = {}
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.endswith(SUPPORTED_EXTENSIONS):
            with open(file_path, 'r', encoding='utf-8') as file:
                filedict[filename] = file.read()
    return filedict

def load_json_report(json_path):
    """Lädt ein JSON-File. Falls es nicht existiert oder ungültig ist, bricht das Skript ab."""
    if not os.path.isfile(json_path):
        print(f"❌ Fehler: Die Datei '{json_path}' existiert nicht!")
        sys.exit(1)

    try:
        with open(json_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print("❌ Fehler: Das JSON-File konnte nicht geladen werden! Stelle sicher, dass es gültig ist.")
        sys.exit(1)

def load_images(directory):
    """Liest alle Bilder ein und gibt eine Liste von Bildpfaden zurück."""
    images = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.lower().endswith(IMAGE_EXTENSIONS):
            images.append(file_path)
    return images


# Bereinige die Antwort und entferne Markdown-Formatierungen
def clean_json_response(response_text):
    """Extrahiert JSON aus einer möglichen Markdown-Antwort der KI."""
    match = re.match(r"```json\s*(\{.*\})\s*```", response_text, re.DOTALL)
    if match:
        return match.group(1)
    return response_text.strip()


# Sende an die KI
def send_to_ai(filedict, images, accessibility_report):
    input_data = json.dumps(filedict, indent=2)

    content = [BASE_PROMPT + (
        "Mache die Website so WCAG konform wie nur möglich, das Ziel ist es AAA Konformität zu erreichen. "
        "Beachte den mitgeschickten Report und behebe außerdem die dort aufgezeigten Fehler.\n\n"
        f"Hier ist der Code:\n{input_data}\n\n"
        f"Hier ist ein Accessibility-Report, der beachtet werden soll:\n\n{json.dumps(accessibility_report, indent=2)}"
    )]

    for image_path in images:
        try:
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
            image = Image.open(io.BytesIO(image_data))
            content.append(image)
        except Exception as e:
            print(f"Fehler beim Laden des Bildes {image_path}: {e}")

    response = client.models.generate_content(
        model="gemini-1.5-pro",
        contents=content)

    try:
        cleaned_json = clean_json_response(response.text)
        return json.loads(cleaned_json)
    except json.JSONDecodeError:
        print("❌ Fehler: Die KI hat kein gültiges JSON zurückgegeben!")
        print(f" Antwort der KI (bereinigt):\n{response.text}")
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
    if len(sys.argv) < 2:
        print("❌ Fehler: Du musst eine JSON-Datei als Accessibility Report angeben!")
        print(" Nutzung: python script.py accessibility_report.json")
        sys.exit(1)

    accessibility_report = load_json_report(sys.argv[1])
    file_contents = load_files(DIRECTORY)
    image_files = load_images(IMG_DIRECTORY)  # Bildpfade laden
    transformed_files = send_to_ai(file_contents, image_files, accessibility_report)  # Bilder übergeben
    save_transformed_files(transformed_files, DIRECTORY)
