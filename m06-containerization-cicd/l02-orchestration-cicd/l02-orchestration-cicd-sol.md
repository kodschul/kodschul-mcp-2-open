# Lab 6.2 – Lösung: Kubernetes-Manifest vervollständigen und Pipeline skizzieren

Vergleichsdateien: `examples/m06-containerization-cicd/l02-orchestration-cicd/k8s.yaml` und `pipeline.yml`.

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

`viewer` ist die restriktivste Rolle und damit der sichere Standard. Der Dienst `vantra-mock-api` ist im Manifest nicht enthalten; ohne ihn schlagen Tool-Aufrufe fehl, der Health-Pfad antwortet trotzdem.

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

Ausgabe 7.1 (aufgezeichnet für das Beispielmanifest, gleiche Ressourcen):

```text
['ConfigMap', 'Deployment', 'Service']
```

Erwartete Ausgabe 7.2 (Format von kubeconform; für das Beispielmanifest als gültig gemeldet, hier nicht erneut ausgeführt):

```text
Summary: 3 resources found in 1 file - Valid: 3, Invalid: 0, Errors: 0, Skipped: 0
```

Mit `replicas: zwei` meldet `kubeconform` für das Deployment einen Typfehler und im Summary `Invalid: 1`. Der Starter ohne Service liefert `2 resources found`: das Schema ist gültig, das Manifest aber unvollständig.

### Vollständiges Manifest (Basis)

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
    # pip-audit stoppt ein kompromittiertes Paket vor dem Deploy
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

Die Skizze lässt Registry-Login, `push` und den Cluster-Zugang weg; das Beispiel `pipeline.yml` zeigt sie (`docker/login-action`, `docker/build-push-action`, `KUBECONFIG_DATA` als Plattform-Secret). Das Beispiel prüft im Scan zusätzlich die Tool-Beschreibungen gegen die freigegebene Liste (Schutz vor Tool-Spoofing) und baut `checkpoints/ende-m07-abgesichert`.

### B6: Prüfen

```bash
python -c "import yaml; print(list(yaml.safe_load(open('playground/pipeline.yml'))['jobs']))"
```

```text
['build', 'test', 'scan', 'deploy', 'rollback']
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

Erwartet (nicht auf einem Cluster aufgezeichnet): `curl` liefert `200 OK` und `{"status":"ok"}`. Der Tag `9.9.9` existiert nicht: die neuen Pods melden `ErrImagePull`/`ImagePullBackOff`, die alten Pods bleiben im Dienst; `rollout undo` stellt die vorige Revision wieder her. Ohne Cluster entfällt die Erweiterung.
