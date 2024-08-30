This is an internal project for performing load testing on kobotoolbox components (kpi, enketo).

# Running with docker

- `docker compose up`
- `docker compose build`

# Running without docker

- Create virtual environment
- `locust`

# Using

Create a form with 1 input field and 1 file input field.

You'll need the Enketo FORM ID and an API Token. Set these as environment variables. If using docker compose:

`cp docker-compose.yaml docker-compose.override.yaml`

Edit FORM_UID (found in the enketo survey URL) and API_TOKEN (Found in KPI account settings)

- Start the server (docker-compose up)
- Go to http://0.0.0.0:8089/
- Enter web address of kobo enketo instance

# Debugging

Using an IDE is easiest. VS Code debugger should work thanks to provided .vscode/launch.json file.

See [more info](https://github.com/locustio/locust/issues/613)
