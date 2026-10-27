# Lab 6.2 – Übung: Kubernetes-Manifest vervollständigen und Pipeline skizzieren

**Dauer:** ca. 40 Minuten (Einzel/Paar)
**Ändert die Vantra-Projektbasis?** Ja – Ergebnis sind ein validiertes Deployment-Manifest und eine Pipeline-Skizze; beide gehören zum Stand „containerisiert“ (Lab 7.1 baut darauf auf).
**Arbeitsdateien:** `playground/k8s.yaml` (Teil A), `playground/pipeline.yml` (Teil B)
**Starter:** `starters/m06-l02-k8s.yaml`, `starters/m06-l02-pipeline.yml`
**Vergleich:** `examples/m06-containerization-cicd/l02-orchestration-cicd/k8s.yaml` und `pipeline.yml`

## Vorbereitung

- Terminal im Projektordner `output/project`, venv aktiv (für PyYAML).
- Starter kopieren:

  ```bash
  cp starters/m06-l02-k8s.yaml playground/k8s.yaml
  cp starters/m06-l02-pipeline.yml playground/pipeline.yml
  ```

- Validierungswerkzeug: `kubeconform` (Installation durch die Kunden-IT bzw. Binary von der Projektseite von kubeconform; `kubeconform -v` zeigt die Version). Ohne Werkzeug gilt der Fallback.
- Die Lücken tragen die Markierung `TODO(Aufgabe n)`; Teil B nummeriert in der Datei `pipeline.yml` getrennt (B1 ≙ `TODO(Aufgabe 1)` dort).

## Aufgaben

### Teil A: Manifest

1. **ConfigMap:** Ergänze `MOCK_API_URL` (Dienst `vantra-mock-api`, Port 8001), `TOOL_CALL_LOG` (`/data/tool_calls.jsonl`) und `VANTRA_ROLE` mit dem Standard `viewer`.
2. **Secret-Referenz:** Binde `MOCK_API_TOKEN` per `secretKeyRef` aus dem Secret `vantra-ops-secrets` ein, als optional. Schreibe keinen Wert ins Manifest.
3. **Probes:** Ergänze `readinessProbe` und `livenessProbe` als HTTP-GET auf `/health` des Ports `mcp`. Wähle Periode und Fehlerschwelle; die Liveness-Probe soll seltener prüfen als die Readiness-Probe.
4. **Sicherheitskontext:** Setze für den Pod: nicht als Root (uid 10001, wie im Dockerfile). Setze für den Container: keine Rechteausweitung, schreibgeschütztes Wurzel-Dateisystem. Mounte dafür ein `emptyDir`-Volume nach `/data`.
5. **Ressourcen:** Setze `requests` und `limits` für CPU und Speicher.
6. **Service:** Ergänze am Dateiende einen Service vom Typ `ClusterIP` für die Pods mit `app=vantra-ops-mcp` auf Port 8000 (Ziel: der benannte Port `mcp`).
7. **Validieren:**
   1. Zähle die Ressourcen: `python -c "import yaml; print([d['kind'] for d in yaml.safe_load_all(open('playground/k8s.yaml')) if d])"`
   2. Prüfe das Schema: `kubeconform -strict -summary playground/k8s.yaml`
   3. Provoziere einen Fehler: ändere `replicas: 2` in `replicas: zwei`, führe `kubeconform` erneut aus, notiere den Summary und stelle `2` wieder her.

### Teil B: Pipeline-Skizze

B1. **build:** Ergänze im Job `build` einen Schritt, der das Image aus `playground/Dockerfile` baut und mit einem aus dem Commit-SHA abgeleiteten Tag versieht.
B2. **test:** Lege den Job `test` an (Python einrichten, Abhängigkeiten installieren, `pytest`).
B3. **scan:** Lege den Job `scan` an: Abhängigkeitsprüfung mit `pip-audit` und Dateisystem-/Image-Scan mit Trivy; er läuft erst nach `build` und `test`. Schreibe als Kommentar in den Job, welcher Schritt ein kompromittiertes Paket stoppt.
B4. **deploy:** Lege den Job `deploy` an: nur auf `main`, nach `scan`, mit Environment-Freigabe, `kubectl set image` auf den neuen Tag und `kubectl rollout status`.
B5. **rollback:** Lege den Job `rollback` an, der nur bei Fehlschlag des Deploys läuft und `kubectl rollout undo` ausführt.
B6. **Prüfen:** `python -c "import yaml; print(list(yaml.safe_load(open('playground/pipeline.yml'))['jobs']))"`

## Checkpoint

- Aufgabe 7.1 gibt `['ConfigMap', 'Deployment', 'Service']` aus.
- `kubeconform` meldet 3 Ressourcen, alle gültig (`Valid: 3, Invalid: 0`); mit `replicas: zwei` meldet es `Invalid: 1`.
- In `playground/k8s.yaml` stehen `readinessProbe`, `livenessProbe`, `securityContext`, `resources` und der Service, aber kein Secret-Wert.
- B6 gibt `['build', 'test', 'scan', 'deploy', 'rollback']` aus.
- In `deploy` steht `needs` mit `scan`, in `rollback` steht `if: failure()`.

## Abschlusskriterien

- `playground/k8s.yaml` und `playground/pipeline.yml` enthalten keine `TODO`-Markierung.
- Das Manifest besteht die Schema-Prüfung; kein Geheimnis steht in einer der beiden Dateien.
- Die Pipeline-Reihenfolge lautet build → test → scan → deploy, mit Rollback bei Fehlschlag.

## Erweiterung

Nur mit lokalem Cluster (z. B. Docker Desktop Kubernetes, `kubectl get nodes` antwortet):

1. Baue das Image mit dem Tag aus dem Manifest: `docker build -f playground/Dockerfile -t vantra-ops-mcp:1.0.0 .`
2. Wende das Manifest an: `kubectl apply -f playground/k8s.yaml`, warte mit `kubectl rollout status deployment/vantra-ops-mcp`.
3. Leite den Service weiter: `kubectl port-forward service/vantra-ops-mcp 8000:8000` und rufe in einem zweiten Terminal `curl -i http://localhost:8000/health` auf.
4. Löse einen fehlerhaften Release aus: `kubectl set image deployment/vantra-ops-mcp mcp-server=vantra-ops-mcp:9.9.9`, beobachte `kubectl get pods` und nimm ihn mit `kubectl rollout undo deployment/vantra-ops-mcp` zurück.
5. Räume auf: `kubectl delete -f playground/k8s.yaml`.

## Fallback

- **Kein Cluster:** Erweiterung entfällt; validiert wird nur mit `kubeconform` (Aufgabe 7). Das Manifest bleibt unangewendet; `kubectl apply --dry-run=client` braucht je nach Version einen erreichbaren Cluster.
- **Kein `kubeconform`:** Aufgabe 7.1 (Ressourcenliste) ersetzt die Schema-Prüfung; sie belegt Syntax und Vollständigkeit der Ressourcen, nicht die Feldnamen.
- **Zeitdruck oder keine Pipeline-Ausführung nötig:** Teil B entfällt als Datei; stattdessen eine Tabelle mit den fünf Stufen, je einer Zeile „Was läuft?“ und „Was verhindert die Stufe?“ in `playground/pipeline-skizze.md`.
