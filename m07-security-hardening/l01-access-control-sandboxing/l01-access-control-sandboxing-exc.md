# Lab 7.1 – Übung: Zugriffsrichtlinie schreiben und im Server durchsetzen

**Dauer:** ca. 35 Minuten
**Ändert die Vantra-Projektbasis?** Ja — `policy.md` und `auth.py` mit Rollen und Bestätigungspflicht; der Stand entspricht `checkpoints/ende-m07-abgesichert/` und ist die Basis für Lab 8.1.
**Arbeitsdateien:** `playground/policy.md`, `playground/auth.py`, `playground/server.py`
**Starter:** `starters/m07-l01-policy.md`, `starters/m07-l01-auth.py`
**Beispiel (zum Vergleichen):** `examples/m07-security-hardening/l01-access-control-sandboxing/` (`policy.md`, `auth.py`, `server.py`)

Die `TODO(Aufgabe n)` in `m07-l01-policy.md` gehören zu den Aufgaben A1–A5, die in `m07-l01-auth.py` zu B1–B6.

## Vorbereitung

- Virtuelle Umgebung ist aktiv, Befehle laufen im Projektordner `output/project`.
- `playground/server.py` und `playground/context.py` liegen im Stand von Lab 5.2. Fehlen sie: aus `examples/m05-cloud-integration/l02-container-prep/` nach `playground/` kopieren.
- Starter kopieren:

```bash
cp starters/m07-l01-policy.md playground/policy.md
cp starters/m07-l01-auth.py playground/auth.py
```

## Aufgaben

### Teil A: Policy (`playground/policy.md`)

1. **A1 Geltungsbereich und Grundsätze:** Trage ein, wo die Prüfung stattfindet und warum dort. Formuliere drei Grundsätze: Least Privilege, Verhalten bei Unbekanntem, Quelle der Rolle.
2. **A2 Rollen und Tools:** Fülle die Tabelle für `viewer` und `operator` aus: Art je Tool, erlaubt oder verboten, Bedingung. Lege die Standardrolle fest.
3. **A3 Bestätigungspflicht:** Benenne die Tools, die nie ohne Bestätigung laufen. Halte fest, wer bestätigt, über welchen Kanal und welcher Fehlercode ohne Bestätigung kommt.
4. **A4 Erkennung:** Beschreibe, woran ein kompromittierter Client erkannt wird: was protokolliert wird und welche Auffälligkeiten zählen.

### Teil B: Durchsetzung (`playground/auth.py`, `playground/server.py`)

5. **B1 Allow-List:** Ergänze in `ROLE_TOOLS` die Rolle `operator` mit allen drei Tools.
6. **B2 Rollenprüfung:** Lasse `authorize` einen Aufruf mit `PolicyDenied("policy_denied", …, role=role, tool=tool)` ablehnen, wenn das Tool nicht in der Allow-List der Rolle steht. Entferne `raise NotImplementedError` erst, wenn B3 fertig ist.
7. **B3 Bestätigung:** Lasse `authorize` ein Schreib-Tool ohne `confirmed` mit `PolicyDenied("confirmation_required", …)` ablehnen. Gib am Ende die Rolle zurück.
8. **B4 Import:** Importiere `PolicyDenied` und `authorize` in `playground/server.py`.
9. **B5 Prüfung in jedem Tool:** Rufe in jedem der drei Tools im `try`-Block zuerst `authorize("<toolname>")` auf (Schreib-Tool mit `confirmed=confirmed`). Beantworte `PolicyDenied` mit `error_result(exc.code, exc.message, **exc.details)`. Prüfe auch die Resource `tickets://{ticket_id}`.
10. **B6 Parameter:** Gib `update_ticket_status` den Parameter `confirmed: bool = False`.
11. **B7 Aufrufe prüfen:** Rufe `update_ticket_status` mit dem Skript-Client dreimal auf: Rolle `viewer`, Rolle `operator` ohne `confirmed`, Rolle `operator` mit `"confirmed": true`.

```bash
python shared/script_client.py --server playground/server.py --role viewer --call update_ticket_status '{"ticket_id": "VAN-101", "status": "closed", "expected_version": 1}'
```

Notiere je Aufruf `is_error` und den Fehlercode.

## Checkpoint

- `playground/policy.md` hat keine `TODO`-Zeilen mehr in A1–A4.
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

- A5: Trage unter „Offene Punkte“ ein, was die Policy bewusst nicht regelt.
- Entscheide, wie ein Client beim HTTP-Transport identifiziert werden soll. Vergleiche drei Optionen (Rolle je Server-Prozess, Token je Client, vorgeschaltetes Gateway) nach Aufwand, Zuordenbarkeit von Aufrufen und Risiko. Halte die Entscheidung in fünf Zeilen fest. Grundlage: Abschnitt „Authentifizierung in MCP“ der Theorie.

## Fallback

Ohne lauffähigen Server genügt Teil A; `examples/m07-security-hardening/l01-access-control-sandboxing/auth.py` wird dann nach `playground/auth.py` kopiert und gelesen (Aufgaben B1–B7 entfallen).
