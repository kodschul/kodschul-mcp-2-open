# Zugriffsrichtlinie – Vorlage

Vorlage für Lab 7.1. Leere Felder `<…>` ausfüllen, nicht zutreffende Zeilen streichen.

## Geltungsbereich

- Server: `<Name des MCP-Servers>`
- Tools: `<Liste der Tools>`
- Durchsetzung: `<wo wird geprüft: Server, Client, Policy-Layer>`

## Grundsätze

1. Least Privilege: `<was gilt?>`
2. Standardverhalten bei Unbekanntem: `<erlauben oder ablehnen?>`
3. Woher kommt die Rolle eines Aufrufers: `<Quelle, nie das Modell>`

## Rollen und Tools

| Tool | Art (lesen/schreiben) | `<Rolle 1>` | `<Rolle 2>` | Bedingung |
| ---- | --------------------- | ----------- | ----------- | --------- |
| `<tool>` | `<…>` | `<erlaubt/verboten>` | `<erlaubt/verboten>` | `<z. B. Bestätigung, Parameter-Grenzen>` |

## Bestätigungspflicht

- Betroffene Tools: `<…>`
- Wer bestätigt, und über welchen Kanal: `<…>`
- Was passiert ohne Bestätigung: `<Fehlercode>`

## Erkennung und Reaktion

- Protokolliert wird: `<…>`
- Auffälligkeiten, die einen Alarm auslösen: `<…>`
- Reaktion: `<Sperren, Rolle entziehen, Benachrichtigung>`

## Offene Punkte

- `<was ist bewusst noch nicht geregelt?>`
