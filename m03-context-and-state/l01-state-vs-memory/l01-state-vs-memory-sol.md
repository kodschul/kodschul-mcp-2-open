# Lab 3.1 – Lösung: State vs. Memory

## Aufgabe 1: Tabelle anlegen

Die Tabelle aus der Übung steht unverändert in `playground/m03-l01-entscheidung.md`.

## Aufgabe 2: Die drei Datentypen

| Datentyp | Ort | Lebensdauer | Risiko | Begründung |
| --- | --- | --- | --- | --- |
| laufende Konversation | Kontextfenster | eine Session | wächst bis zur Token-Grenze | Das Modell braucht den Verlauf für den nächsten Schritt |
| Nutzerpräferenz | Memory | über Sessions | falsche oder veraltete Präferenz bleibt bestehen | gilt dauerhaft, klein, vom Nutzer löschbar |
| einmaliges Tool-Ergebnis | Session-State (Ausschnitt im Kontextfenster) | eine Session | große Logs sprengen das Fenster | nur für diesen Vorgang, später neu abrufbar |

## Aufgabe 3: Vier weitere Daten

| Datentyp | Ort | Lebensdauer | Risiko | Begründung |
| --- | --- | --- | --- | --- |
| API-Token des Mock-Servers | weder Kontextfenster noch Memory; Umgebungsvariable des Serverprozesses | Prozess | Leck im Prompt oder Memory | Geheimnis gehört dem Server, das Modell braucht es nicht |
| zuletzt abgefragte Ticket-ID | Session-State | Session | veraltet nach neuer Abfrage | ersetzt Wiederholung der ID („das Deployment dazu“) |
| Rolle des Nutzers | Session-State (vom Server gesetzt) | Session | Modell darf sie nicht ändern können | Sicherheitsentscheidung, nie aus Modelltext ableiten |
| Text einer Ticket-Beschreibung | Kontextfenster, nie Memory | Session | enthält ggf. fremde Anweisungen | Fremdtext wird als Daten behandelt, nicht gespeichert |

Zeilen mit „nie ins Memory“: API-Token, Ticket-Beschreibung.

## Aufgabe 4: Neustart-Effekt

Erster Aufruf: `get_ticket` liefert das Ticket `VAN-102` (Version 3). Zweiter Aufruf, neuer Prozess:

```text
Tool 'get_deployment_log' failed: 'Error executing tool get_deployment_log: Keine ticket_id angegeben und kein Ticket im Kontext: zuerst get_ticket aufrufen.'
Server: vantra-ops · Protokoll 2026-07-28
Tools: get_ticket, get_deployment_log
is_error=True
Error executing tool get_deployment_log: Keine ticket_id angegeben und kein Ticket im Kontext: zuerst get_ticket aufrufen.
```

Satz für die Datei: „Jeder `--call` startet einen neuen Serverprozess; `session.last_ticket` ist dort `None`, der State des ersten Prozesses ist mit dessen Ende verloren.“

## Aufgabe 5: Plenum

Typische Abweichungen und ihre Auflösung:

- Nutzerpräferenz als Session-State: gültig, wenn sie nur für diese Sitzung gelten soll; für „immer kurz und auf Deutsch“ fehlt dann die Persistenz.
- Tool-Ergebnis im Memory: nur als geprüfte Zusammenfassung vertretbar, nie als Rohtext.

## Erweiterung

| Datenart | Memory nötig? | Löschen |
| --- | --- | --- |
| Eskalationsregeln | ja, aber als versionierte Konfiguration, nicht als Agenten-Memory | Fachverantwortliche |
| Bereitschaftsplan | nein, bei Bedarf aus dem Planungssystem abrufen | entfällt |
| Ergebnis einer Fehleranalyse | ja, als geprüfte Notiz mit Quelle und Datum | Ticket-Eigentümer:in |
