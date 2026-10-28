# Lab 6.2 – Lösung: Kubernetes-Manifest vervollständigen und Pipeline skizzieren

Vergleichsdateien: `examples/m06-containerization-cicd/l02-kubernetes-cicd/k8s.yaml` und `pipeline.yml`.

## Aufgabe 1: ConfigMap

```yaml
data:
  MCP_TRANSPORT: streamable-http
  MCP_HOST: 0.0.0.0
  MCP_PORT: "8000"
  MOCK_API_URL: http://vantra-mock-api:8001
  TOOL_CALL_LOG: /data/tool_calls.jsonl
  VANTRA_ROLE: viewer
```

`viewer` ist die restriktivste Rolle und damit der sichere Standard. `MOCK_API_URL` zeigt auf den Dienst `vantra-mock-api`, den der Starter am Ende des Manifests bereits vorgibt (Deployment und Service der Mock-API).

## Aufgabe 2: Secret-Referenz

```yaml
          env:
            - name: MOCK_API_TOKEN
              valueFrom:
                secretKeyRef:
                  name: vantra-ops-secrets
                  key: MOCK_API_TOKEN
                  optional: true
```

Der Betrieb legt den Wert an: `kubectl create secret generic vantra-ops-secrets --from-literal=MOCK_API_TOKEN=<wert>`.

## Aufgabe 3: Probes

```yaml
          readinessProbe:
            httpGet:
              path: /health
              port: mcp
            periodSeconds: 5
            failureThreshold: 3
          livenessProbe:
            httpGet:
              path: /health
              port: mcp
            periodSeconds: 15
            failureThreshold: 3
```

Readiness prüft häufiger und nimmt den Pod nur aus der Verteilung; Liveness startet den Container neu und soll deshalb zurückhaltender auslösen. Das Beispiel ergänzt eine `startupProbe` (15 Versuche im Abstand von 2 s), damit langsame Starts nicht neu gestartet werden.

## Aufgabe 4: Sicherheitskontext und `/data`

```yaml
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: ["ALL"]
          volumeMounts:
            - name: data
              mountPath: /data
      volumes:
        - name: data
          emptyDir: {}
```

Der Server schreibt nur nach `/data`; `emptyDir` stellt dafür ein beschreibbares Verzeichnis bereit, während das übrige Dateisystem schreibgeschützt bleibt. Nicht als Root läuft der Pod über `runAsNonRoot: true` und `runAsUser: 10001` im Pod-`securityContext` (gleiche uid wie im Dockerfile):

```yaml
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
```

## Aufgabe 5: Ressourcen

```yaml
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 256Mi
```

`requests` steuern die Platzierung, `limits` die Obergrenze.

## Aufgabe 6: Service

```yaml
---
apiVersion: v1
kind: Service
metadata:
  name: vantra-ops-mcp
spec:
  type: ClusterIP
  selector:
    app: vantra-ops-mcp
  ports:
    - name: mcp
      port: 8000
      targetPort: mcp
```

## Aufgabe 7: Validieren

```bash
python -c "import yaml; print([d['kind'] for d in yaml.safe_load_all(open('playground/k8s.yaml')) if d])"
kubeconform -strict -summary playground/k8s.yaml
```

Ausgabe 7.1:

```text
['ConfigMap', 'Deployment', 'Service', 'Deployment', 'Service']
```

Ausgabe 7.2 (kubeconform v0.8.0):

```text
Summary: 5 resources found in 1 file - Valid: 5, Invalid: 0, Errors: 0, Skipped: 0
```

Ausgabe 7.3 mit `replicas: zwei`:

```text
playground/k8s.yaml - Deployment vantra-ops-mcp is invalid: problem validating schema. Check JSON formatting: jsonschema validation failed with 'https://raw.githubusercontent.com/yannh/kubernetes-json-schema/master/master-standalone-strict/deployment-apps-v1.json#' - at '/spec/replicas': got string, want null or integer
Summary: 5 resources found in 1 file - Valid: 4, Invalid: 1, Errors: 0, Skipped: 0
```

Häufige Abweichungen: `additionalProperties '…' not allowed` (Feld auf falscher Ebene eingerückt, z. B. `volumes` im Container statt unter `template.spec`) und `got string, want integer` (Zahl in Anführungszeichen außerhalb der ConfigMap).

Der unveränderte Starter liefert `['ConfigMap', 'Deployment', 'Deployment', 'Service']` und `4 resources found ... Valid: 4`: das Schema ist gültig, das Manifest aber unvollständig (Service des MCP-Servers fehlt).

### Vollständiges Manifest (Basis)

Ohne den vorgegebenen Mock-API-Teil am Ende (unverändert aus dem Starter):

```yaml
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: vantra-ops-config
data:
  MCP_TRANSPORT: streamable-http
  MCP_HOST: 0.0.0.0
  MCP_PORT: "8000"
  MOCK_API_URL: http://vantra-mock-api:8001
  TOOL_CALL_LOG: /data/tool_calls.jsonl
  VANTRA_ROLE: viewer
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vantra-ops-mcp
  labels:
    app: vantra-ops-mcp
spec:
  replicas: 2
  selector:
    matchLabels:
      app: vantra-ops-mcp
  template:
    metadata:
      labels:
        app: vantra-ops-mcp
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
      containers:
        - name: mcp-server
          image: vantra-ops-mcp:1.0.0
          ports:
            - name: mcp
              containerPort: 8000
          envFrom:
            - configMapRef:
                name: vantra-ops-config
          env:
            - name: MOCK_API_TOKEN
              valueFrom:
                secretKeyRef:
                  name: vantra-ops-secrets
                  key: MOCK_API_TOKEN
                  optional: true
          readinessProbe:
            httpGet:
              path: /health
              port: mcp
            periodSeconds: 5
            failureThreshold: 3
          livenessProbe:
            httpGet:
              path: /health
              port: mcp
            periodSeconds: 15
            failureThreshold: 3
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 256Mi
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: ["ALL"]
          volumeMounts:
            - name: data
              mountPath: /data
      volumes:
        - name: data
          emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: vantra-ops-mcp
spec:
  type: ClusterIP
  selector:
    app: vantra-ops-mcp
  ports:
    - name: mcp
      port: 8000
      targetPort: mcp
```

## Teil B: Pipeline-Skizze

### B1 bis B5: `playground/pipeline.yml` (build = B1, test = B2, scan = B3, deploy = B4, rollback = B5)

```yaml
name: vantra-ops-mcp

on:
  push:
    branches: [main]

env:
  IMAGE: ghcr.io/vantra-systems/vantra-ops-mcp

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      tag: ${{ steps.meta.outputs.tag }}
    steps:
      - uses: actions/checkout@v4
      - id: meta
        run: echo "tag=${GITHUB_SHA::12}" >> "$GITHUB_OUTPUT"
      - run: docker build -f playground/Dockerfile -t ${IMAGE}:${{ steps.meta.outputs.tag }} .

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
      - run: pip install -r requirements.txt
      - run: pytest -q

  scan:
    # pip-audit und Trivy stoppen Pakete mit bekannten Schwachstellen vor dem Deploy.
    # Nicht erkannt: frisch manipulierte Pakete ohne Eintrag in den Schwachstellenlisten.
    runs-on: ubuntu-latest
    needs: [build, test]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
      - run: pip install pip-audit && pip-audit -r requirements-server.txt
      - uses: aquasecurity/trivy-action@0.28.0
        with:
          scan-type: fs
          scan-ref: .
          severity: CRITICAL,HIGH
          exit-code: "1"

  deploy:
    runs-on: ubuntu-latest
    needs: [build, scan]
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - run: |
          kubectl set image deployment/vantra-ops-mcp mcp-server=${IMAGE}:${{ needs.build.outputs.tag }}
          kubectl rollout status deployment/vantra-ops-mcp --timeout=120s

  rollback:
    runs-on: ubuntu-latest
    needs: [deploy]
    if: failure()
    environment: production
    steps:
      - run: kubectl rollout undo deployment/vantra-ops-mcp
```

Die Skizze lässt Registry-Login, `push` und den Cluster-Zugang weg; das Beispiel `pipeline.yml` zeigt sie (`docker/login-action`, `docker/build-push-action`, `KUBECONFIG_DATA` als Plattform-Secret). Das Beispiel baut den Server-Stand aus Lab 5.2 (`examples/m05-cloud-integration/l02-container-prep`); Tests auf freigegebene Tools und Rechte kommen ab Lab 7.1 hinzu. Skizze und Beispiel bestehen `actionlint` (v1.7.12) ohne Befund; ausgeführt wurde die Pipeline nicht.

### B6: Prüfen

```bash
python -c "import yaml; d=yaml.safe_load(open('playground/pipeline.yml')); print(list(d['jobs'])); print(d['jobs']['deploy'].get('needs'), d['jobs']['rollback'].get('if'))"
```

```text
['build', 'test', 'scan', 'deploy', 'rollback']
['build', 'scan'] failure()
```

Gründe: `scan` hängt an `build` und `test`, `deploy` an `scan` und trägt die manuelle Freigabe (`environment`), `rollback` läuft nur bei `failure()` und macht den Deploy rückgängig.

## Erweiterung

```bash
docker build -f playground/Dockerfile -t vantra-ops-mcp:1.0.0 .
kubectl apply -f playground/k8s.yaml
kubectl rollout status deployment/vantra-ops-mcp
kubectl port-forward service/vantra-ops-mcp 8000:8000
curl -i http://localhost:8000/health
kubectl set image deployment/vantra-ops-mcp mcp-server=vantra-ops-mcp:9.9.9
kubectl get pods
kubectl rollout undo deployment/vantra-ops-mcp
kubectl delete -f playground/k8s.yaml
```

Erwartet (nicht auf einem Cluster aufgezeichnet; bei `ErrImagePull` schon für `1.0.0` siehe Theorie, „Lokaler Cluster mit Docker Desktop“): `curl` liefert `200 OK` und `{"status":"ok"}`. Der Tag `9.9.9` existiert nicht: die neuen Pods melden `ErrImagePull`/`ImagePullBackOff`, die alten Pods bleiben im Dienst; `rollout undo` stellt die vorige Revision wieder her. Ohne Cluster entfällt die Erweiterung.
