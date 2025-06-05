# Solomon-OpenAI-FastAPI

FastAPI connections to OpenAI assistants.

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements-minimal.txt
```

3. Set the `PYTHONPATH` so the `app` package can be imported:

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/app
```

## Running Tests

Install any additional test dependencies listed in `requirements.txt` if needed and run:

```bash
pytest -q
```

The tests include an example WebSocket client that connects to the running server.

## WebSocket Authentication

Send a JSON message containing your `solomon_consumer_key` immediately after connecting to `/ws/assistant/<assistant_id>`.
