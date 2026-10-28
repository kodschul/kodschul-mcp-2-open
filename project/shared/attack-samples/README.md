# Angriffsproben (Lab 7.2)

Präparierte, manipulierte Tool-Ergebnisse zur Analyse. Keine davon führt für sich Code aus; sie zeigen, wie Text in Tool-Ergebnissen oder Tool-Beschreibungen ein Modell steuern will.

| Datei | Angriff | Wo steckt die Manipulation? |
| ----- | ------- | --------------------------- |
| `01-prompt-injection-ticket.json` | Prompt Injection | Freitextfeld `description` eines Tickets (im Mock-Datensatz als VAN-106 hinterlegt) |
| `02-gefaelschte-tool-beschreibung.json` | Tool-Spoofing | `description` und Schema eines Tools eines fremden Servers |
| `03-ueberprivilegierte-anweisung.json` | Rechteausweitung | Log-Zeile im Deployment-Log |

Aufgabe: je Probe Auffälligkeit, Gegenmaßnahme und Verteidigungslinie (Modell, Client, Server, Policy) benennen. Die erwarteten Auffälligkeiten stehen in der Lösung zu Lab 7.2 (`m07-security-hardening/l02-injection/l02-injection-sol.md`), nicht in den Proben.

Showcase C (nur Probe 1 ist ausführbar):

```bash
# ohne Policy: Server aus Lab 3.3, der Aufruf gelingt
python shared/agent_client.py --server examples/m03-context-and-state/l03-multi-agent/server.py --replay injection --confirm none
# mit Policy: Server aus Lab 7.1, der Server blockt (Rolle viewer)
python shared/agent_client.py --server examples/m07-security-hardening/l01-access-control/server.py --replay injection --confirm none
```
