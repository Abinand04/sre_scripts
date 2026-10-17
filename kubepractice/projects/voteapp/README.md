# Kubernetes Deployment: Example Voting App

The application and its container images come from Docker's open-source
[example-voting-app](https://github.com/dockersamples/example-voting-app), as used in
KodeKloud's *Kubernetes for the Absolute Beginners* course. **I did not write the
application.** The Kubernetes manifests, design choices, and incident write-ups below
are my own, built and tested on a local [kind](https://kind.sigs.k8s.io/) cluster.

## Architecture

```
user ──► vote-app ──► redis ──► worker-app ──► db (postgres) ◄── result-app ◄── user
```

| Component  | Image                                   | Service              | Why                                   |
|------------|-----------------------------------------|----------------------|---------------------------------------|
| vote-app   | `kodekloud/examplevotingapp_vote:v1`    | NodePort, port 80    | Users connect to it from outside      |
| result-app | `kodekloud/examplevotingapp_result:v1`  | NodePort, port 80    | Users connect to it from outside      |
| redis      | `redis`                                 | ClusterIP, port 6379 | Internal only: vote-app and worker    |
| postgres   | `postgres:13`                           | ClusterIP `db`, 5432 | Internal only: worker and result-app  |
| worker-app | `kodekloud/examplevotingapp_worker:v1`  | none                 | Only makes outbound connections; nothing connects to it |

The application code connects to the hostnames `redis` and `db`, so those two
Service names are fixed. The postgres Deployment is named `postgres`, but its
Service must be named `db`.

## Design choices

**Two labels on every pod.**
Each component carries a shared label and a unique one:

```yaml
app: voting-app   # shared: groups the whole app (kubectl get pods -l app=voting-app)
name: redis       # unique: what each Service and Deployment selector matches on
```

Using only the shared label would make every Service select every pod, so the
`redis` Service would send traffic to postgres, vote, result, and worker pods too.

**Pinned postgres version (`postgres:13`).**
See Incident 1.

**Numbered manifests.**
`kubectl apply -f .` applies files in alphabetical order, so the numeric prefixes
create the namespace first, then the backends, then the apps. Ordering doesn't
guarantee readiness, though; the worker retries until `db` accepts connections.

## Run it

```bash
kubectl apply -f .
kubectl get pods,svc -n vote-lab

# in two separate terminals:
kubectl port-forward svc/vote-app 8081:80 -n vote-lab     # vote:    http://localhost:8081
kubectl port-forward svc/result-app 8082:80 -n vote-lab   # results: http://localhost:8082
```

On kind, the nodes are Docker containers, so NodePorts aren't reachable from the
host without extra cluster config. Port-forward is used instead.

Clean up: `kubectl delete namespace vote-lab`

## Incident 1: worker in CrashLoopBackOff (postgres auth)

- **Symptom:** `worker-app` restarted repeatedly; all other pods were healthy, and every Service had endpoints.
- **Investigation:** `kubectl logs --previous` showed `Npgsql ... Authentication method not supported (Received: 10)`.
- **Cause:** the unpinned `postgres` image pulled the latest version, which defaults to SCRAM-SHA-256 authentication (since PostgreSQL 14). The worker's older Npgsql driver doesn't support it. DNS and networking were fine: the worker reached postgres but couldn't log in.
- **Fix:** pinned `postgres:13`, then `kubectl rollout restart` on the worker.
- **Lesson:** an unpinned image tag means the same YAML can deploy different software over time. Pin versions.

## Incident 2: deleted Service, hidden outage (failure test)

- **Test:** deleted the `db` Service while the app was running.
- **What happened:** nothing visibly broke at first. Existing connections to postgres stayed open, so the running worker kept working.
- **Trigger:** a `rollout restart` of the worker. The new pod failed its DNS lookup for `db` (`System.Net.Dns ... Resource temporarily unavailable`) and went into CrashLoopBackOff.
- **Why the rollout didn't stop:** with no readiness probe, the new pod counted as ready during its first second of running, so the healthy old pod was removed.
- **Recovery:** re-applied the saved Service manifest. The first attempt silently failed because it ran from the wrong directory, so the outage lasted longer than necessary.
- **Lessons:** deleting a Service breaks *new* connections, not existing ones, so outages can surface hours later on any restart. Readiness probes are what make rollouts safe. Read the output of every `apply`.

## Known gaps (next steps)

- The postgres password is plain text in the manifest (demo only); a real setup would use a Secret.
- No readiness probes yet (see Incident 2).
- No persistent storage: replacing the postgres pod loses all votes.
- The `redis` image is still unpinned.