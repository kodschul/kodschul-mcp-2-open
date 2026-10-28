# Lab 7.1 – Übung: Zugriffsrichtlinie schreiben und im Server durchsetzen

**Dauer:** ca. 25 Minuten
**Ändert die Vantra-Projektbasis?** Ja — `policy.md` und `auth.py` mit Rollen und Bestätigungspflicht; der Stand entspricht `checkpoints/ende-m07-abgesichert/` und ist die Basis für Lab 8.1.
**Arbeitsdateien:** `playground/policy.md`, `playground/auth.py`, `playground/server.py`
**Starter:** `starters/m07-l01-policy.md`, `starters/m07-l01-auth.py`
**Beispiel (zum Vergleichen):** `examples/m07-security-hardening/l01-access-control/` (`policy.md`, `auth.py`, `server.py`)

Die Markierungen `TODO(Aufgabe n)` in beiden Startern entsprechen den Aufgabennummern unten: `m07-l01-policy.md` enthält Aufgabe 1–4, `m07-l01-auth.py` Aufgabe 5–10.

**Zeitplan:** Teil A (Aufgabe 1–4) ca. 8 Minuten, je Abschnitt zwei bis drei Stichpunkte; die Tabelle aus der Theorie darf übernommen werden. Teil B (Aufgabe 5–11) ca. 17 Minuten.

## Vorbereitung

- Virtuelle Umgebung ist aktiv, Befehle laufen im Projektordner `output/project`.
- `playground/server.py` und `playground/context.py` liegen im Stand von Lab 5.2. Fehlen sie: aus `examples/m05-cloud-integration/l02-container-prep/` nach `playground/` kopieren.
- Starter kopieren:

```bash
cp starters/m07-l01-policy.md playground/policy.md
cp starters/m07-l01-auth.py playground/auth.py
```

## Aufgaben

### Teil A: Policy (`playground/policy.md`, ca. 8 Minuten)

1. **Geltungsbereich und Grundsätze:** Trage ein, wo die Prüfung stattfindet und warum dort. Formuliere drei Grundsätze: Least Privilege, Verhalten bei Unbekanntem, Quelle der Rolle.
2. **Rollen und Tools:** Fülle die Tabelle für `viewer` und `operator` aus: Art je Tool, erlaubt oder verboten, Bedingung. Lege die Standardrolle fest.
3. **Bestätigungspflicht:** Benenne die Tools, die nie ohne Bestätigung laufen. Halte fest, wer bestätigt, über welchen Kanal und welcher Fehlercode ohne Bestätigung kommt.
4. **Erkennung:** Beschreibe, woran ein kompromittierter Client erkannt wird: was protokolliert wird und welche Auffälligkeiten zählen.

### Teil B: Durchsetzung (`playground/auth.py`, `playground/server.py`, ca. 17 Minuten)

5. **Allow-List:** Ergänze in `ROLE_TOOLS` die Rolle `operator` mit allen drei Tools.
6. **Rollenprüfung:** Lasse `authorize` einen Aufruf mit `PolicyDenied("policy_denied", …, role=role, tool=tool)` ablehnen, wenn das Tool nicht in der Allow-List der Rolle steht. Entferne `raise NotImplementedError` erst, wenn Aufgabe 7 fertig ist.
7. **Bestätigung:** Lasse `authorize` ein Schreib-Tool ohne `confirmed` mit `PolicyDenied("confirmation_required", …)` ablehnen. Gib am Ende die Rolle zurück.
8. **Import:** Importiere `PolicyDenied` und `authorize` in `playground/server.py`.
9. **Prüfung in jedem Tool:** Rufe in jedem der drei Tools im `try`-Block zuerst `authorize("<toolname>")` auf (Schreib-Tool mit `confirmed=confirmed`). Beantworte `PolicyDenied` mit `error_result(exc.code, exc.message, **exc.details)`.
   - `get_deployment_log`: Ziehe `session.resolve_ticket_id(...)` samt der Prüfung auf `None` in den `try`-Block hinter `authorize("get_deployment_log")`.
   - Resource `tickets://{ticket_id}`: Rufe `authorize("get_ticket")` auf und beantworte `PolicyDenied` mit `raise ResourceNotFoundError(exc.message) from exc`, damit die Resource nicht an der Prüfung vorbei Daten liefert.
10. **Parameter:** Gib `update_ticket_status` den Parameter `confirmed: bool = False`.
11. **Aufrufe prüfen:** Rufe `update_ticket_status` mit dem Skript-Client dreimal auf: Rolle `viewer`, Rolle `operator` ohne `confirmed`, Rolle `operator` mit `"confirmed": true`.

```bash
python shared/script_client.py --server playground/server.py --role viewer --call update_ticket_status '{"ticket_id": "VAN-101", "status": "closed", "expected_version": 1}'
```

Setze für die beiden anderen Aufrufe `--role operator` und nimm beim dritten `"confirmed": true` ins JSON auf. Notiere je Aufruf `is_error` und den Fehlercode.

Erwartete Ausgabe für Rolle `viewer`:

```text
is_error=True
{"error": "policy_denied", "message": "Rolle 'viewer' darf das Tool 'update_ticket_status' nicht aufrufen.", ...}
```

## Checkpoint

- `playground/policy.md` hat keine `TODO`-Zeilen mehr in Aufgabe 1–4.
- Der Aufruf mit Rolle `viewer` endet mit `is_error=True` und dem Code `policy_denied`.
- Der Aufruf mit Rolle `operator` ohne `confirmed` endet mit `is_error=True` und dem Code `confirmation_required`.
- Der Aufruf mit Rolle `operator` und `confirmed: true` liefert das Ticket mit erhöhter `version`.
- `get_ticket` mit `VAN-102` funktioniert mit Rolle `viewer`.

## Abschlusskriterien

- Die Policy nennt Rollen, Tools, Bedingungen, Bestätigungspflicht und Erkennung.
- Der Server setzt jede Regel der Rollen-Tabelle durch; keine Regel steht nur in der Policy.
- Die Rolle kommt ausschließlich aus `VANTRA_ROLE`.

## Erweiterung (optional)

**Code:** Härte `playground/server.py`: Erlaube für `ticket_id` nur das Format `VAN-<1 bis 6 Ziffern>` und begrenze `tail` bei `get_deployment_log` auf höchstens 100 Zeilen. Prüfe beides mit `../etc/passwd` und `"tail": 500`.

**Ohne Programmierung (Review/Entscheidung):**

- Trage unter „Offene Punkte“ ein, was die Policy bewusst nicht regelt.
- Entscheide, wie ein Client beim HTTP-Transport identifiziert werden soll. Vergleiche drei Optionen (Rolle je Server-Prozess, Token je Client, vorgeschaltetes Gateway) nach Aufwand, Zuordenbarkeit von Aufrufen und Risiko. Halte die Entscheidung in fünf Zeilen fest. Grundlage: Abschnitt „Authentifizierung in MCP“ der Theorie.

## Fallback

Ohne lauffähigen Server genügt Teil A; `examples/m07-security-hardening/l01-access-control/auth.py` wird dann nach `playground/auth.py` kopiert und gelesen (Aufgaben 5–11 entfallen).
