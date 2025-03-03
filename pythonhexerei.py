#!/usr/bin/env python3
import json
import sys
import subprocess
from bs4 import BeautifulSoup

# Automatische Installation von fehlenden Bibliotheken
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    install("beautifulsoup4")
except Exception as e:
    print("❌ Fehler beim Installieren von Paketen:", e)
    sys.exit(1)

# HTML-Datei öffnen und <h1>-Tag ändern
def modify_h1_tag(file_path, new_text):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        h1_tag = soup.find('h1')
        if h1_tag:
            h1_tag.string = new_text
        else:
            print("⚠️ Kein <h1>-Tag gefunden!")
            return 1  # Fehlercode zurückgeben, damit Jenkins es erkennt

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(str(soup))

        print("✅ <h1>-Tag erfolgreich geändert!")
        return 0

    except Exception as e:
        print(f"❌ Fehler beim Bearbeiten der Datei: {e}")
        return 1

# Hauptprogramm für Jenkins
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Fehler: Keine Report-Datei angegeben!")
        sys.exit(1)

    report_path = sys.argv[1]
    html_file_path = "public/index.html"

    try:
        with open(report_path, 'r', encoding='utf-8') as report_file:
            report_data = json.load(report_file)  # JSON-Report korrekt einlesen

        # Debug: Zeige die ersten 500 Zeichen des Reports
        print(f"📄 WCAG-Report geladen: {json.dumps(report_data, indent=2)[:500]}...")

        new_h1_text = json.dumps(report_data)

        exit_code = modify_h1_tag(html_file_path, new_h1_text)

    except json.JSONDecodeError:
        print("❌ Fehler: Der Report ist kein gültiges JSON!")
        exit_code = 1
    except FileNotFoundError:
        print(f"❌ Fehler: Report-Datei {report_path} nicht gefunden!")
        exit_code = 1
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        exit_code = 1

    sys.exit(exit_code)
