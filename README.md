# Back-End-Development-Songs

Project: Band website Songs microservice — IBM Back-end Application Development Capstone.

Flask REST API backed by MongoDB. Implements health, count, song listing, retrieval, creation, update and deletion. Course seed data is inserted only when missing; restarting does not clear the database.

## Run

Install requirements, provide `MONGODB_SERVICE` and `MONGODB_PORT` (default 27017). If authentication is enabled, also set `MONGODB_USERNAME` and `MONGODB_PASSWORD` in the environment. Never commit credentials.

```sh
python -m flask --app app run --host 0.0.0.0 --port 3000
```

Local verification: actual MongoDB 7 with health/list/create/update/delete requests. Cloud deployment is pending and is not represented as complete here.

Based on IBM Skills Network's hvlga template. Implementation and debugging were assisted by OpenAI Codex; the learner must review and understand the work before submission.
