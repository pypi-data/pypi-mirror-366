# Flow

Flow is a set of tools that enable you to visualize flow of your code. Using these tools you can draw state diagrams and call flow diagram.

Currently, this has been vide-coded to check feasibility but the end goal is to have a swappable backends, a Grafana plugin and client libraries in multiple languages.

The intent is to strengthen my python skills while simultaneously building something useful for the community.

## Design

The clients POSTs to an HTTP server which write it to Redis(swappable). The Grafana plugin (3rd party plugin) GETs the latest diagrams from HTTP server.
TBD

## Setup

```bash
docker compose up --build
```

After running the above command go to `localhost:3000` and login using admin/admin, change the password. In the left hand menu, go to "Administration", "Plugins an data", "Plugins" and search for "Diagrams", install the one "By Jeremy Branham" by selecting the search result. Go to home and click on "New Dashboard" at the bottom and edit it. Follow the first example below.

## Using HTTP Sender

The file `examples/http_sender.py` shows an example of how you can use it in your code. This example shows an example `FlowchartBuilder` which will draw flowcharts for you:

```bash
python -m examples.http_sender
```

Click "Refresh", it should automatically render the latest diagram.

![alt text](design/flowcharts/example_http_sender.png "Example HTTP State Diagram")

## Using Redis Sender

This plugin bypasses the HTTP API and directly writes to Redis.

```bash
python -m examples.redis_sender
```

## Using Curl

```bash
curl -X POST http://localhost:8000/diagrams -H "Content-Type: application/json" \
  --data-binary @- <<EOF | jq
{
  "diagram_type": "flowchart",
  "content": "graph TD;\n  A[Start] --> B{Is it working?};\n  B -- Yes --> C[Great];\n  B -- No --> D[Fix it];\n  D --> B;\n B --> B"
}
EOF
```

## Using file writer

```bash
python receiver/file_writer.py
cd receiver/static
python3 -m http.server 8000
python -m examples.sequence
python -m examples.basic_flow
```
