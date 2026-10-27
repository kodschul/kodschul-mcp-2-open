# Security-Review-Checkliste für MCP-Server (Lab 7.3)

Prüfgegenstände: Dockerfile, Zugriffsrichtlinie (`policy.md`), Server-Konfiguration. Je Punkt: erfüllt (✔), nicht erfüllt (✘) oder nicht prüfbar (?). Jeder Befund bekommt eine Schwere:

- **blockierend:** verhindert den Produktionseinsatz
- **wichtig:** vor dem Produktionseinsatz beheben oder bewusst akzeptieren
- **nice to have:** Verbesserung ohne akutes Risiko

## A. Dockerfile

| # | Prüffrage | Ergebnis | Befund / Zeile |
| - | --------- | -------- | -------------- |
| A1 | Basis-Image mit fester Version statt `latest`? | | |
| A2 | Läuft der Prozess als Nicht-Root-Nutzer (`USER`)? | | |
| A3 | Stehen Secrets (Schlüssel, Tokens, Passwörter) im Image oder in `ENV`? | | |
| A4 | Werden nur benötigte Dateien kopiert (kein `COPY . .`, `.dockerignore` vorhanden)? | | |
| A5 | Sind Abhängigkeiten auf feste Versionen gepinnt? | | |
| A6 | Gibt es einen `HEALTHCHECK`? | | |
| A7 | Nur benötigte Ports freigegeben, keine unnötigen Pakete oder Dienste? | | |
| A8 | Dateirechte restriktiv (kein `chmod 777`)? | | |

## B. Zugriffsrichtlinie

| # | Prüffrage | Ergebnis | Befund / Zeile |
| - | --------- | -------- | -------------- |
| B1 | Rollen nach Least Privilege getrennt (nicht alle Rollen alle Tools)? | | |
| B2 | Unbekannte Rollen/Tools werden abgelehnt (deny by default)? | | |
| B3 | Kommt die Rolle aus einer vertrauenswürdigen Quelle, nicht aus Modell oder Tool-Argumenten? | | |
| B4 | Schreibende Tools nur mit Bestätigung des Nutzers? | | |
| B5 | Wird die Richtlinie im Server durchgesetzt (nicht nur im Prompt)? | | |
| B6 | Jeder Aufruf wird protokolliert, auch abgelehnte? | | |
| B7 | Eigene Identität je Client statt gemeinsamem Zugang? | | |
| B8 | Erkennung und Reaktion auf Auffälligkeiten beschrieben? | | |

## C. Server und Betrieb

| # | Prüffrage | Ergebnis | Befund / Zeile |
| - | --------- | -------- | -------------- |
| C1 | Eingaben der Tools validiert (Format, Grenzen)? | | |
| C2 | Tool-Ergebnisse als Daten behandelt, nie als Anweisung? | | |
| C3 | Konfiguration über Umgebung/Secret-Store, nicht im Code? | | |
| C4 | Protokolle enthalten keine Secrets und keine Ticket-Inhalte? | | |
| C5 | Rollback-Weg für fehlerhafte Releases vorhanden? | | |
