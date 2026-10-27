# Lab 4.3: Debrief

**Leitfragen:**

<details>
<summary>Welches Risiko wäre in einer echten Vantra-Umgebung am kritischsten?</summary>

Der ungeschützte Schreibzugriff: Ein Agent, dem fremder Text (z. B. eine Ticket-Beschreibung) als Anweisung dient, könnte Tickets ändern, ohne dass Rolle, Bestätigung oder Protokoll greifen.

</details>

<details>
<summary>Was braucht der Prototyp zuerst – Absicherung, Betrieb oder Monitoring?</summary>

Absicherung: Betrieb und Monitoring verteilen bzw. beobachten sonst einen ungeschützten Dienst. Monitoring erkennt Vorfälle, verhindert sie aber nicht. Eine andere Reihenfolge ist mit Begründung vertretbar.

</details>

- Der Debrief verdichtet den Testlauf zu einer priorisierten Liste offener Punkte.
- Priorität ergibt sich aus Schaden und Eintrittswahrscheinlichkeit, nicht aus der Reihenfolge der Entdeckung.

## Von der Beobachtung zum Risiko

| Schritt | Frage | Quelle |
| --- | --- | --- |
| Sammeln | Welche Lücken und Auffälligkeiten stehen im Testprotokoll? | `playground/testlauf.md` (Lab 4.2) |
| Beschreiben | Was kann konkret schiefgehen? | Beleg aus dem Lauf |
| Bewerten | Wie hoch ist der Schaden, wie wahrscheinlich der Eintritt (hoch / mittel / niedrig)? | Einschätzung der Gruppe |
| Zuordnen | Welcher Baustein behebt es? | Tabelle unten |
| Priorisieren | Welche drei Punkte zuerst? | Schaden vor Wahrscheinlichkeit |

## Lücken und Bausteine

| Lücke aus dem Testlauf | Risiko | Baustein |
| --- | --- | --- |
| Schreib-Tool ohne Rollenprüfung und Bestätigung | unbefugte oder untergeschobene Änderungen | Zugriffskontrolle, Policy, Bestätigung |
| Fremdtext aus Tool-Ergebnissen wird dem Modell als Daten gegeben | Prompt Injection | Policy-Layer, Eingabevalidierung |
| Kein Protokoll der Aufrufe auf Serverseite | Vorfälle nicht nachvollziehbar | Logging, Alarme |
| Nur lokaler Prozess, kein Dienstbetrieb | kein Betrieb für mehrere Nutzer, keine Wiederherstellung | Container, Orchestrierung, Pipeline |
| Kontext nur im Prozess | Verlust bei Neustart | Memory-Entscheidung (Lab 3.1) |

## Bewertungsraster

| Stufe | Schaden | Beispiel |
| --- | --- | --- |
| hoch | Daten ändern oder abfließen, Dienst ausfallen | Ticket ohne Berechtigung auf `closed` |
| mittel | falsche Antwort, mühsame Fehlersuche | fehlendes Protokoll bei Fehlverhalten |
| niedrig | Komfort | Antwort ohne alle Log-Zeilen |

## Fazit

- Der Debrief erzeugt eine kurze Liste mit Risiko, Bewertung, Baustein und Rangfolge.
- Der ungeschützte Schreibzugriff ist die größte offene Lücke des Prototyps.

Die Übung verdichtet das Testprotokoll aus Lab 4.2 zu dieser Liste.
