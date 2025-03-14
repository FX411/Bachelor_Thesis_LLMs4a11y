#!/bin/usr/env python
import os
import json
import re
import sys
import base64
from openai import OpenAI

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

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
    """Liest alle Bilder ein, kodiert sie in Base64 und bereitet sie für OpenAI vor."""
    images = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.lower().endswith(IMAGE_EXTENSIONS):
            with open(file_path, "rb") as img_file:
                encoded_string = base64.b64encode(img_file.read()).decode("utf-8")
                # Bild als OpenAI-konforme Struktur hinzufügen
                images.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encoded_string}"
                    }
                })
    return images


# Bereinige die Antwort und entferne Markdown-Formatierungen
def clean_json_response(response_text):
    """Extrahiert JSON aus einer möglichen Markdown-Antwort der KI."""
    match = re.match(r"```json\s*(\{.*\})\s*```", response_text, re.DOTALL)
    if match:
        return match.group(1)
    return response_text.strip()

def remove_images_from_response(response_json):
    """Entfernt Bilder aus der Antwort, falls die KI welche zurückschickt."""
    return {key: value for key, value in response_json.items() if not key.lower().endswith(IMAGE_EXTENSIONS)}

# Sende an die KI
def send_to_ai(filedict, images, accessibility_report):
    """Sende Code und Bilder an KI."""
    content = []
    messages = [
        {"role": "system", "content": BASE_PROMPT},
        {"role": "user", "content": content}
    ]

    content.append(
            {"type": "text", "text": "Mache die Website so WCAG konform wie nur möglich, das Ziel ist es AAA Konformität zu erreichen. Beachte den mitgeschickten Report und behebe außerdem die dort aufgezeigten Fehler."},
        )

    # Code-Dateien hinzufügen
    input_data = json.dumps(filedict, indent=2)
    content.append({
        "type": "text",
        "text": f"Hier ist der Code: {input_data}"
        })

    # Bilder als base64 hinzufügen
    for image in images:
        content.append(image)

    # pa11y-report mitschicken
    content.append({
        "type": "text",
        "text": f"Hier ist ein Accessibility-Report, der beachtet werden soll:\n\n{json.dumps(accessibility_report, indent=2)}"
    })

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    try:
        cleaned_json = clean_json_response(response.choices[0].message.content)
        transformed_data = json.loads(cleaned_json)
        transformed_data = remove_images_from_response(transformed_data)  # Bilder entfernen
        return transformed_data
    except json.JSONDecodeError:
        print("❌ Fehler: Die KI hat kein gültiges JSON zurückgegeben!")
        print(f"🛑 Antwort der KI (bereinigt):\n{cleaned_json}")
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
        print("🛠 Nutzung: python script.py accessibility_report.json")
        sys.exit(1)

    accessibility_report = load_json_report(sys.argv[1])

    file_contents = load_files(DIRECTORY)
    image_messages = load_images(IMG_DIRECTORY)
    transformed_files = send_to_ai(file_contents, image_messages, accessibility_report)
    save_transformed_files(transformed_files, DIRECTORY)
