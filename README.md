This is an internal project for performing load testing on kobotoolbox components (kpi, kobocat, enkeno).

# Running with docker

- `docker-compose build`
- `docker-compose up`

# Running without docker

- Create virtual environment
- `locust`

# Using

- Go to http://0.0.0.0:8089/
- Enter web address of kobo enketo instance

# Debugging

Using an IDE is easiest. VS Code debugger should work thanks to provided .vscode/launch.json file.

See [more info](https://github.com/locustio/locust/issues/613)
