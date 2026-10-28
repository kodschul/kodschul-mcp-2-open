# Lab 4.3 – Lösung: Debrief

Die Lösung baut auf den Beobachtungen aus der Lösung von Lab 4.2 auf.

## Aufgabe 1 bis 4: Tabelle

| Risiko | Beleg aus dem Testlauf | Schaden | Wahrscheinlichkeit | Baustein | Rang |
| --- | --- | --- | --- | --- | --- |
| Schreib-Tool ohne Rollenprüfung und Bestätigung | `update_ticket_status` setzte `VAN-102` von Version 3 auf 4, ohne Rückfrage | hoch (Daten ändern) | mittel | Absicherung | 1 |
| Fremdtext im Tool-Ergebnis kann das Modell steuern | Annahme: Ergebnisse gehen unverändert als `tool`-Nachricht an das Modell, Ticket-Beschreibungen sind freier Text; ein Angriff wurde im Testlauf nicht beobachtet | hoch | mittel | Absicherung | 2 |
| Kein Protokoll der Aufrufe auf Serverseite | Ausgaben nur im Client-Terminal | mittel | hoch (tritt bei jedem Vorfall ein) | Monitoring | 3 |
| Nur lokaler stdio-Prozess | Server startet als Kindprozess des Clients | mittel | hoch | Betrieb | – |
| Kontext geht beim Neustart verloren | Log-Frage im neuen Prozess scheitert | niedrig | hoch | Betrieb (Memory-Entscheidung) | – |

Begründung der Einstufung „hoch“: Schreibzugriff ändert Produktivdaten ohne Berechtigungsprüfung; Fremdtext hat denselben Effekt über den Umweg des Modells.

## Aufgabe 5: Entscheidungssatz

„Am kritischsten ist der ungeschützte Schreibzugriff, weil eine Änderung ohne Rolle, Bestätigung und Protokoll möglich ist. Zuerst braucht der Prototyp Absicherung: Betrieb und Monitoring würden sonst einen ungeschützten Dienst verbreiten bzw. nur beobachten.“

## Aufgabe 6: Plenum

Begründbare Abweichungen:

- Monitoring auf Rang 1: sinnvoll, wenn der Agent zunächst nur lesend läuft; dann fehlt vor allem die Nachvollziehbarkeit.
- Betrieb auf Rang 1: nur vertretbar, wenn der Dienst isoliert und ohne Schreibrechte laufen soll.

## Erweiterung

| Risiko | Rang Betriebsrolle | Rang Sicherheitsrolle |
| --- | --- | --- |
| Schreibzugriff ohne Prüfung | 2 | 1 |
| Kein Dienstbetrieb | 1 | 3 |
| Kein Protokoll | 3 | 2 |

Die Reihenfolge entscheidet die für das Gesamtsystem verantwortliche Person (z. B. Architektur oder Produktverantwortung), mit Sicherheits- und Betriebsrolle als Beratung.
