# Reproduction: `nuget.registryUrls` from the global config is ignored since Renovate 44.171.2

Self-hosted Renovate CLI (Docker), `--platform=local`, no network access to any private host needed.

## What it does
- `mockfeed.py` is a tiny NuGet v3 feed on `127.0.0.1:8099` (stands in for a private feed).
- `config.js` sets `nuget.registryUrls` to that feed only.
- `repo/Test.csproj` has no `NuGet.config`.

## Run
```
bash run.sh 44.171.1 44.171.2
```
(Needs docker, python3 and internet, because when the bug triggers Renovate talks to api.nuget.org.)

## Result
| Renovate | requests to configured feed | registryUrl used | outcome |
|---|---|---|---|
| 44.171.1 | 6 | `http://127.0.0.1:8099/v3/index.json` | only the private package gets an update; packages missing from the feed: `no-result` |
| 44.171.2 .. 44.175.0 | **0** | `https://api.nuget.org/v3/index.json` | public packages get updates (`autofac-9.x`, `newtonsoft.json-13.x`); the private package: `no-result` |
