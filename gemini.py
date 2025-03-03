#!/bin/usr/env python
import os
from google import genai

client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

prompt = (
    "Du bist ein spezialisierter Code-Transformer für HTML, CSS und JavaScript. "
    "Deine Aufgabe ist es, gelieferten Code nach bestimmten Kriterien zu verändern. "
    "Du gibst ausschließlich validen und vollständigen HTML-, CSS- oder JavaScript-Code zurück, "
    "ohne Kommentare oder Erklärungen. Deine Antwort muss so strukturiert sein, dass sie direkt "
    "maschinell weiterverarbeitet werden kann.\n\n"
    "Regeln:\n"
    "1. Erhalte die Code-Struktur: Bewahre die grundlegende Struktur und Funktionalität des Codes.\n"
    "2. Modifikationen nach Vorgabe: Führe nur die Änderungen durch, die explizit in der Anfrage angegeben sind.\n"
    "3. Kein unnötiger Text: Deine Antwort enthält ausschließlich den geänderten Code – keine Kommentare, keine Erklärungen, kein Markdown-Format.\n"
    "4. Validität sicherstellen: Der zurückgegebene Code muss fehlerfrei und funktionsfähig sein.\n\n"
    "Antworte stets nur mit dem modifizierten Code."
)
directory = "public"
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    if os.path.isfile(f) and filename.endswith(".html"):
        with open(f, "r", encoding="utf-8") as file:
            html_content = file.read()

            completion = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[prompt + "Füge der Website einen Text über das Ende des zweites Weltkriegs in Europa ein. Hier ist der HTMl Code, den du bearbeiten sollst: " + html_content]
            )

        with open(f, 'w', encoding='utf-8') as file:
                    file.write(completion.text)
