# Best Practices

Modulübergreifende Regeln aus dem Kurs, je mit einem Grund. Details stehen in den Modulen (Spalte Lab).

## Server und Protokoll

| Regel | Grund | Lab |
| --- | --- | --- |
| Als Vorlage nur Material zu SDK 2.x und Spezifikation 2026-07-28 verwenden | Tutorials zu SDK 1.x (`FastMCP`, `initialize`, HTTP+SSE) laufen nicht mehr | 1.2, 2.1 |
| Version des SDK fest pinnen (`mcp==2.3.0`) | Ergebnisse sind reproduzierbar, Importpfade ändern sich zwischen Hauptversionen | 1.2 |
| Bei stdio nichts auf stdout schreiben, Logs nach stderr oder in eine Datei | stdout gehört dem Protokoll; ein `print()` zerstört die Nachrichten | 1.2, 8.1 |
| Zuerst stdio, Streamable HTTP erst für den Containerbetrieb | stdio braucht weder Port noch Netzwerk und ist am einfachsten zu testen | 1.2, 6.1 |
| Tool-Schema aus Typhinweisen und Docstring erzeugen, Docstring abgrenzend formulieren | Das Modell wählt Tools nach Beschreibung; überlappende Beschreibungen führen zu falschen Aufrufen | 2.2, 4.1 |
| Lesende Tools mit `read_only_hint=True` kennzeichnen | Clients und Policies können lesend und schreibend unterscheiden | 2.2 |
| Erwartbare Fehler als `ToolError` mit hilfreicher Meldung auslösen | Die Meldung erreicht das Modell, eine normale Exception zeigt nur `Error executing tool <name>` | 2.3 |
| Tool-Fehler und Protokollfehler getrennt behandeln | Tool-Fehler (`isError`) lassen sich mit korrigierten Argumenten wiederholen, Protokollfehler verlangen eine Korrektur des Clients | 2.3 |
| Mit dem Skript-Client oder Inspector testen, bevor ein LLM beteiligt ist | Fehler im Server und Fehler der Modellwahl bleiben getrennt | 1.2, 4.1 |

## Kontext und Zustand

| Regel | Grund | Lab |
| --- | --- | --- |
| Kontext als Schema führen (Feld, Quelle, Lebensdauer, Sichtbarkeit für das LLM) | Es bleibt nachvollziehbar, was gespeichert und was dem Modell übergeben wird | 3.2 |
| Je Tool-Ergebnis ein eigenes Feld, nur Ausschnitte ablegen | Das zweite Tool überschreibt den Kontext des ersten nicht, das Kontextfenster bleibt klein | 3.2 |
| Geheimnisse und Tokens nie in Prompt, Kontext oder Memory | Modell und Protokoll würden sie offenlegen | 3.1, 5.2 |
| Schreibende Tools mit `expected_version` absichern | Ohne Versionsprüfung überschreibt ein Agent die Änderung eines anderen unbemerkt | 3.3 |
| Bei `version_conflict` neu lesen und mit neuer Version wiederholen | Der Fehler enthält `expected_version` und `current_version` | 3.3 |

## Agent und Test

| Regel | Grund | Lab |
| --- | --- | --- |
| Läufe mit Replay-LLM als Skript-Agent kennzeichnen | Ein Skript-Agent wählt keine Tools; das Ergebnis sagt nichts über die Tool-Auswahl eines Modells | 4.2 |
| Testprotokoll mit Eingabe, erwartetem und tatsächlichem Tool-Call führen | Abweichungen sind belegt und später reproduzierbar | 4.2 |
| Lücken mit Beleg festhalten und nach Risiko ordnen | Das Backlog für Absicherung, Betrieb und Monitoring entsteht aus Beobachtungen | 4.3 |

## Container und Betrieb

| Regel | Grund | Lab |
| --- | --- | --- |
| Transport, Host und Port über Umgebungsvariablen steuern | Dasselbe Image läuft lokal, in Compose und in Kubernetes | 5.2 |
| `/health` ohne Authentifizierung und ohne Daten anbieten | Docker, Compose und Kubernetes prüfen damit die Gesundheit | 5.2, 6.1 |
| Bei Container-HTTP `MCP_HOST=0.0.0.0` setzen | Bei `127.0.0.1` ist der Server trotz Portfreigabe nicht erreichbar | 5.2, 6.1 |
| Abhängigkeiten vor dem Code kopieren (eigener Layer) | Codeänderungen installieren nicht alles neu | 5.2 |
| Nicht als Root laufen, nur `/data` beschreibbar | Ein kompromittierter Prozess hat weniger Möglichkeiten | 5.2, 7.1 |
| Festen Image-Tag verwenden, nie `latest` | Rollout und Rollback beziehen sich auf eine bekannte Version | 5.1, 6.2 |
| Secrets zur Laufzeit übergeben (`-e`, Compose-Secret, `secretKeyRef`), nie per `ENV` oder im Repo | `docker inspect` und `docker history` zeigen `ENV`-Werte | 5.2, 6.2 |
| Kubernetes-Manifest vor dem Anwenden validieren (`kubeconform`) | Schemafehler fallen ohne Cluster auf | 6.2 |
| Pipeline mit Test, Scan und Freigabe vor dem Deploy, Rollback als eigene Stufe | Ein kompromittiertes Tool gelangt nicht ungeprüft in Produktion | 6.2 |

## Security

| Regel | Grund | Lab |
| --- | --- | --- |
| Least Privilege und deny by default | Unbekannte Rollen und Tools werden abgelehnt statt erlaubt | 7.1 |
| Rolle aus der Prozessumgebung beziehen, nie vom Modell | Das Modell kann manipuliert werden und darf sich keine Rechte geben | 7.1, 7.2 |
| Schreibende Tools nur mit Bestätigung je Aufruf | Eine Injection darf keine Änderung ohne Zustimmung auslösen | 7.1 |
| Eingaben validieren (`^VAN-\d{1,6}$`) und Ausgaben begrenzen (`tail` ≤ 100) | Ungültige oder übergroße Werte erreichen weder Backend noch Modell | 7.1 |
| Tool-Ergebnisse und Tool-Beschreibungen als nicht vertrauenswürdige Eingabe behandeln | Anweisungen im Datenfeld sind der Weg der Prompt Injection | 7.2 |
| Mehrere Verteidigungslinien kombinieren (Modell, Client, Server, Policy/Betrieb) | Die Modell-Linie ist probabilistisch; die Server-Linie greift auch bei Versagen | 7.2 |
| Tokens nur akzeptieren, die für den Server ausgestellt sind | Token Passthrough ist ein Anti-Pattern | 7.1 |
| Reviews nach Schweregrad einstufen (blockierend, wichtig, nice to have) | Die Freigabe hängt an den blockierenden Befunden | 7.3 |

## Monitoring

| Regel | Grund | Lab |
| --- | --- | --- |
| Jeden Tool-Call als JSON-Zeile protokollieren (`ts`, `tool`, `role`, `status`, `error_code`, `duration_ms`) | Missbrauch und Fehler sind auswertbar | 8.1 |
| Keine Ticket-Texte, Log-Inhalte, Secrets, Tokens oder `confirmed` ins Protokoll | Datenschutz; das Protokoll hat eigene Zugriffsrechte | 8.1 |
| Alarmregeln mit Status, Schwelle und Zeitfenster definieren (z. B. 3 × `denied` in 60 s) | Wiederholt abgelehnte Aufrufe sind der schnellste Hinweis auf einen Angriff | 8.1 |
| Lücken bis zum Produktivbetrieb ausdrücklich benennen | Authentifizierung je Client, Ratenbegrenzung und Log-Aufbewahrung sind im Projekt nicht umgesetzt | 8.2 |
| Trends und Versionen mit Quelle und Datum festhalten (Stand: 27.10.2026) | Roadmap-Punkte sind Richtung, keine Zusage | 8.3 |
