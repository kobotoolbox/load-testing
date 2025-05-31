This is an internal project for performing load testing on KoboToolbox components (`kpi`, `enketo`, `openrosa`).

## Running with Docker

```bash
docker compose build
docker compose up
```

## Running without Docker

```bash
poetry install
poetry shell
locust
```

## Usage

### Setup Instructions

#### 1. Prepare the Test Form

- Copy the provided `.env.sample` file:
  ```bash
  cp .env.sample .env
  ```

- Open the `assets/` directory and locate the provided XLSX form file.

- On the KoboToolbox instance you want to test, create a new project by importing this XLSX form and deploy it.

- After deployment, locate the `project_uid` in the URL:
  ```
  https://[your-kpi-domain]/#/forms/<project_uid>/landing
  ```

#### 2. Generate Environment Variables

From a Django shell on the instance (e.g. `./manage.py shell`), run:

```python
import os
a = Asset.objects.get(uid='<project_uid>')

print('# Project unique identifiers')
print(f'PROJECT_UID={a.uid}')
print(f'VERSION_UID={a.latest_deployed_version.uid}')
print(f'FORM_UUID={a.deployment.xform.uuid}')
print(f"ENKETO_FORM_UID={a.deployment.get_enketo_survey_links()['url'].split('/')[-1]}")

print('\n# Auth')
print(f'API_TOKEN={Token.objects.get(user=a.owner).key}')
print('DIGEST_USER=')
print('DIGEST_PASS=')

print('\n# URLs')
print(f"ENKETO_SUBDOMAIN={os.getenv('ENKETO_EXPRESS_PUBLIC_SUBDOMAIN')}")
print(f"KC_SUBDOMAIN={os.getenv('KOBOCAT_PUBLIC_SUBDOMAIN')}")
print(f"KPI_SUBDOMAIN={os.getenv('KOBOFORM_PUBLIC_SUBDOMAIN')}")
print(f"SCHEME={os.getenv('PUBLIC_REQUEST_SCHEME')}")
print(f"DOMAIN_NAME={os.getenv('PUBLIC_DOMAIN_NAME')}")
```

- Paste the output into your `.env` file (replacing the placeholders).

- Then, edit the following values at the bottom of `.env` to match your test configuration:

```
# Locust
MASTER_IP=1.2.3.4
LOCUST_TAGS=tag1,tag2,tag3
```

### Tags

- `all`: Run all tests.
- `enketo`: Run all tests simulating data collection with Enketo Express.
- `simple`: Run tests simulating data collection without attachments (Enketo).
- `attachments`: Run tests with attachments (via Enketo or OpenRosa).
- `slow`: Run tests simulating **slow** data collection with attachments (Enketo).
- `normal`: Run standard Enketo data collection tests.
- `kpi`: Run tests simulating KPI UI usage (e.g. data exports, submission deletions).
- `openrosa`: Run tests that POST submissions directly to the OpenRosa API.

### Known Bugs

Submitting data with Digest Auth doesn't currently work.  
The first request correctly waits for a 401 response, but the second attempt uses Token Auth instead.

## Starting Locust

- Start the server:
  ```bash
  docker compose up
  ```

- Open the Locust web UI: [http://0.0.0.0:8089](http://0.0.0.0:8089)

## Debugging

Using an IDE is recommended. The VS Code debugger should work out of the box, thanks to the `.vscode/launch.json` file.

See [Locust Issue #613](https://github.com/locustio/locust/issues/613) for more information.
