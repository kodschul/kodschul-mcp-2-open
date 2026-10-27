# Lab 3.1: State vs. Memory

**Leitfragen:**

<details>
<summary>Was passiert mit State, wenn der Agent neu startet?</summary>

Session-State lebt nur so lange wie der Prozess, der ihn hält. Nach einem Neustart ist er leer; nur Daten, die bewusst persistiert wurden (Memory), bleiben erhalten.

</details>

<details>
<summary>Welche Daten dürfen nie ins Langzeit-Memory?</summary>

Geheimnisse (Tokens, Passwörter, Schlüssel), personenbezogene Daten ohne Zweck und Rechtsgrundlage sowie ungeprüfte Inhalte aus Tool-Ergebnissen, die dort als Anweisung überdauern könnten.

</details>

- Kontextfenster, Session-State und Memory sind drei verschiedene Speicherorte mit unterschiedlicher Lebensdauer.
- Jedes Datum bekommt genau einen Ort; die Entscheidung folgt aus Lebensdauer, Sensibilität und Größe.

## Drei Speicherorte

| Ort | Wo liegt es? | Lebensdauer | Grenze |
| --- | --- | --- | --- |
| Kontextfenster | im Prompt des Modells (System-Prompt, Nachrichten, Tool-Ergebnisse) | ein Modellaufruf, solange die Nachrichten mitgesendet werden | feste Token-Obergrenze; alles darin kostet Platz und Geld |
| Session-State | im Server- oder Client-Prozess (Variablen, Objekte) | bis zum Ende des Prozesses bzw. der Session | weg bei Neustart, nicht geteilt zwischen Prozessen |
| Memory (persistent) | Datei, Datenbank, Vektorspeicher | über Sessions hinweg, bis zum Löschen | braucht Schema, Zugriffsschutz und Löschkonzept |

```text
Nutzer ──► Agent-Client ──► LLM
              │   ▲  Kontextfenster = Nachrichtenliste, die mitgeschickt wird
              ▼   │
          MCP-Server ── Session-State (Prozessspeicher)
              │
              ▼
          Memory (Datei/Datenbank), nur wenn bewusst gebaut
```

Das Kontextfenster ist kein Speicher des Servers: Das Modell sieht nur, was der Client in die Nachrichtenliste legt. Der Server hält State, der Client entscheidet, welcher Ausschnitt davon ins Fenster gelangt.

## Entscheidung pro Datentyp

Drei Fragen entscheiden über den Ort:

1. Wird das Datum nach dem Ende der Session noch gebraucht? Wenn nein: kein Memory.
2. Muss das Modell es im nächsten Schritt sehen? Wenn nein: nicht ins Kontextfenster, sondern in den Server-State.
3. Ist es geheim oder personenbezogen? Wenn ja: nicht ins Modell-Prompt und nicht ins Memory ohne Schutzkonzept.

| Datentyp | Beispiel (Vantra) | Ort | Begründung |
| --- | --- | --- | --- |
| Laufende Konversation | Nutzerfrage „Zeige Ticket VAN-102“ und Antwort | Kontextfenster (Nachrichtenliste des Clients) | Das Modell braucht den Verlauf für den nächsten Schritt; Ende mit der Session |
| Nutzerpräferenz | „Antworten immer kurz und auf Deutsch“ | Memory (persistent) | gilt über Sessions hinweg; klein, nicht geheim, vom Nutzer löschbar |
| Einmaliges Tool-Ergebnis | vollständiges Deployment-Log von `dep-2041` | Session-State des Servers, nur der benötigte Ausschnitt ins Kontextfenster | groß und nur für diesen Vorgang relevant; später neu abrufbar |

## Was im Kursprojekt umgesetzt ist

- Session-State: das Objekt `session` in `context.py` (Lab 3.2) lebt im Serverprozess. Bei stdio startet der Client den Server als Kindprozess; endet der Client, endet der State.
- Memory ist im Kursprojekt bewusst nicht implementiert. Die Entscheidung „was gehört dorthin“ gehört zum Entwurf, nicht zur Umsetzung.
- Ein Neustart zeigt den Effekt direkt: Der Aufruf `get_deployment_log` ohne `ticket_id` braucht das zuvor abgefragte Ticket. In einem frisch gestarteten Server fehlt es:

```text
Error executing tool get_deployment_log: Keine ticket_id angegeben und kein Ticket im Kontext: zuerst get_ticket aufrufen.
```

## Was nicht ins Langzeit-Memory gehört

| Daten | Risiko |
| --- | --- |
| Tokens, Passwörter, API-Schlüssel | dauerhafte Ablage von Geheimnissen, Leck bei jedem Zugriff auf das Memory |
| personenbezogene Daten ohne Zweck | Löschpflichten, Zweckbindung |
| rohe Tool-Ergebnisse mit fremdem Text (z. B. Ticket-Beschreibungen) | eingeschleuste Anweisungen (Prompt Injection) wirken in jeder späteren Session |
| Behauptungen des Modells ohne Prüfung | Fehler verfestigen sich als „Wissen“ |

> **Merksatz:** Session-State ist Arbeitsspeicher, Memory ist Archiv. Was ins Archiv wandert, wird bewusst ausgewählt, geprüft und löschbar gehalten.

## Fazit

- Kontextfenster, Session-State und Memory unterscheiden sich in Lebensdauer, Größe und Risiko.
- Neustart leert den Session-State; das Kursprojekt hält State nur im Prozess.
- Geheimnisse und ungeprüfte Fremdtexte gehören nicht ins Memory.

Die Übung ordnet drei Datentypen ihrem Speicherort zu und belegt den Neustart-Effekt am Beispielserver.
