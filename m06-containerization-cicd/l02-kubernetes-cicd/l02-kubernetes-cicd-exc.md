# Lab 6.2 – Übung: Kubernetes-Manifest vervollständigen und Pipeline skizzieren

**Dauer:** ca. 40 Minuten (Einzel/Paar)
**Ändert die Vantra-Projektbasis?** Ja – Ergebnis sind ein validiertes Deployment-Manifest und eine Pipeline-Skizze; beide gehören zum Stand „containerisiert“ (Lab 7.1 baut darauf auf).
**Arbeitsdateien:** `playground/k8s.yaml` (Teil A), `playground/pipeline.yml` (Teil B)
**Starter:** `starters/m06-l02-k8s.yaml`, `starters/m06-l02-pipeline.yml`
**Vergleich:** `examples/m06-containerization-cicd/l02-kubernetes-cicd/k8s.yaml` und `pipeline.yml`

## Vorbereitung

- Terminal im Projektordner `output/project`, venv aktiv (für PyYAML).
- Starter kopieren:

  ```bash
  cp starters/m06-l02-k8s.yaml playground/k8s.yaml
  cp starters/m06-l02-pipeline.yml playground/pipeline.yml
  ```

- Validierungswerkzeug: `kubeconform` (Installation durch die Kunden-IT bzw. Binary von der Projektseite von kubeconform; `kubeconform -v` zeigt die Version). Ohne Werkzeug gilt der Fallback.
- Die Lücken tragen die Markierung `TODO(Aufgabe n)` im Manifest (Teil A) bzw. `TODO(Aufgabe B1)` … `TODO(Aufgabe B5)` in der Pipeline (Teil B).
- Vorlage für Teil A: Theorie, Abschnitte „Deployment“, „Einheiten und Sicherheitskontext“ und „Service“; die vorgegebene Mock-API am Ende von `playground/k8s.yaml` zeigt Probes, `securityContext` und `resources` in fertiger Form.
- Vorlage für Teil B: Theorie, Abschnitte „Ausgearbeitetes Beispiel“ und „Kernausschnitte“. Das Gerüst der fünf Jobs ist im Starter vorgegeben.

## Aufgaben

### Teil A: Manifest

1. **ConfigMap:** Ergänze `MOCK_API_URL` (Dienst `vantra-mock-api`, Port 8001), `TOOL_CALL_LOG` (`/data/tool_calls.jsonl`, vorbereitet für Lab 8.1) und `VANTRA_ROLE` mit dem Standard `viewer` (vorbereitet für Lab 7.1).
2. **Secret-Referenz:** Binde `MOCK_API_TOKEN` per `secretKeyRef` aus dem Secret `vantra-ops-secrets` ein, als optional. Schreibe keinen Wert ins Manifest.
3. **Probes:** Ergänze `readinessProbe` und `livenessProbe` als HTTP-GET auf `/health` des Ports `mcp`. Wähle Periode und Fehlerschwelle; die Liveness-Probe soll seltener prüfen als die Readiness-Probe.
4. **Sicherheitskontext:** Setze für den Pod (unter `template.spec`): nicht als Root (uid 10001, wie im Dockerfile). Setze für den Container: keine Rechteausweitung, schreibgeschütztes Wurzel-Dateisystem. Mounte dafür ein `emptyDir`-Volume nach `/data` (`volumeMounts` im Container, `volumes` unter `template.spec`).
5. **Ressourcen:** Setze `requests` und `limits` für CPU und Speicher, z. B. `requests` 100m/128Mi und `limits` 500m/256Mi (Einheiten: Theorie, Tabelle „Einheiten und Sicherheitskontext“).
6. **Service:** Ergänze am Dateiende einen Service vom Typ `ClusterIP` für die Pods mit `app=vantra-ops-mcp` auf Port 8000 (Ziel: der benannte Port `mcp`).
7. **Validieren:**
   1. Zähle die Ressourcen: `python -c "import yaml; print([d['kind'] for d in yaml.safe_load_all(open('playground/k8s.yaml')) if d])"`
   2. Prüfe das Schema: `kubeconform -strict -summary playground/k8s.yaml`
   3. Provoziere einen Fehler: ändere `replicas: 2` in `replicas: zwei`, führe `kubeconform` erneut aus, notiere den Summary und stelle `2` wieder her.

### Teil B: Pipeline-Skizze

B1. **build:** Ergänze im Job `build` die `outputs`, einen Schritt `meta`, der den Tag aus den ersten 12 Zeichen der Commit-Kennung (`GITHUB_SHA`) bildet, und den `docker build`-Schritt für `playground/Dockerfile` mit diesem Tag.
B2. **test:** Ergänze im Job `test` die Schritte: Python 3.13 einrichten, `requirements.txt` installieren, `pytest -q` ausführen.
B3. **scan:** Ergänze im Job `scan` `needs: [build, test]`, die Abhängigkeitsprüfung mit `pip-audit` und den Dateisystem-Scan mit Trivy. Schreibe als Kommentar in den Job, welcher Schritt ein Paket mit bekannter Schwachstelle stoppt und was er nicht erkennt.
B4. **deploy:** Ergänze im Job `deploy` `needs`, `if` (nur `main`), `environment: production` und ersetze den Platzhalter-Schritt durch `kubectl set image` auf den neuen Tag und `kubectl rollout status`.
B5. **rollback:** Ergänze im Job `rollback` `needs: [deploy]` und `if: failure()` und ersetze den Platzhalter-Schritt durch `kubectl rollout undo`.
B6. **Prüfen:** `python -c "import yaml; d=yaml.safe_load(open('playground/pipeline.yml')); print(list(d['jobs'])); print(d['jobs']['deploy'].get('needs'), d['jobs']['rollback'].get('if'))"`

## Checkpoint

- Aufgabe 7.1 gibt `['ConfigMap', 'Deployment', 'Service', 'Deployment', 'Service']` aus (die letzten zwei sind die vorgegebene Mock-API).
- `kubeconform` meldet 5 Ressourcen, alle gültig (`Valid: 5, Invalid: 0`); mit `replicas: zwei` meldet es `Invalid: 1`.
- In `playground/k8s.yaml` stehen `readinessProbe`, `livenessProbe`, `securityContext`, `resources` und der Service, aber kein Secret-Wert.
- B6 gibt `['build', 'test', 'scan', 'deploy', 'rollback']` und danach `['build', 'scan'] failure()` aus.
- `playground/pipeline.yml` enthält keine `TODO`-Markierung und keinen `echo`-Platzhalter mehr.
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

Zeigt `kubectl get pods` schon für `1.0.0` den Status `ErrImagePull`, sieht der Cluster das lokal gebaute Image nicht: Theorie, Abschnitt „Typische Fehler“, Absatz „Lokaler Cluster mit Docker Desktop“.

## Fallback

- **Kein Cluster:** Erweiterung entfällt; validiert wird nur mit `kubeconform` (Aufgabe 7). Das Manifest bleibt unangewendet; `kubectl apply --dry-run=client` braucht je nach Version einen erreichbaren Cluster.
- **Kein `kubeconform`:** Aufgabe 7.1 (Ressourcenliste) ersetzt die Schema-Prüfung; sie belegt Syntax und Vollständigkeit der Ressourcen, nicht die Feldnamen.
- **Zeitdruck oder keine Pipeline-Ausführung nötig:** Teil B entfällt als Datei; stattdessen eine Tabelle mit den fünf Stufen, je einer Zeile „Was läuft?“ und „Was verhindert die Stufe?“ in `playground/pipeline-skizze.md`.
