# DTR RTS HTTP control service

A lightweight Python HTTP server to control the **DTR** and **RTS** lines of a serial port.

---

## Motivation

I have a 3D printer and the best upgrade I did is starting using [klipper](https://www.klipper3d.org/) and [moonraker](https://moonraker.readthedocs.io).  
One of features I like - an ability to control power of 3D printer, but when I was choosing platform I decided to use thin client (which are available for a fraction of price of raspberry pi), so I quite limited in available GPIO.  
Luckly a lot of thin clients have serial port, which gives 2 easily controllable "GPIO" -- DTR and RTS serial lines.  
I decided to make simple HTTP server which allows to control satete of DTR and RTS, so I can use one of them to control SSR which controls power to my printer.

---

## Features

- Exposes serial **DTR** and **RTS** control over HTTP.
- Query the current status (`ON`/`OFF`) via GET requests.
- Toggle lines via POST request.
- Configurable serial port and HTTP port via environment variables or command-line arguments.

---

## Requirements

- Python 3.7+
- `pyserial` library

Install dependencies with:

```bash
pip install pyserial
```

---
## Usage
``` bash
python serial_http_server.py --port /dev/ttyS0 --http-port 8080
```
### Docker
```bash
docker run -it \
  --device=/dev/ttyS0:/dev/ttyS0 \
  -p 8080:8080 \
  ghcr.io/ivanbayan/ivanbayan/dtr-rts-http-service:latest \
  --port /dev/ttyS0 --http-port 8080
```

### Environment Variables
You can also use environment variables instead of command-line arguments:
```bash
export PORT=/dev/ttyS0
export HTTP_PORT=8080
```

## API Description
This script exposes a serial port’s DTR and RTS lines over HTTP. It allows checking status and toggling these lines via HTTP requests:
* GET /dtr?action=status – Get DTR status
* GET /rts?action=status – Get RTS status
* POST /dtr – Set DTR line (action=on or action=off)
* POST /rts – Set RTS line (action=on or action=off)

---
## HTTP API Examples
### Check Status
```bash
curl "http://localhost:8080/dtr?action=status"
# Response: {"result": "OFF"}

curl "http://localhost:8080/rts?action=status"
# Response: {"result": "ON"}
```

### Set DTR/RTS
```bash
curl -X POST -d "action=on" "http://localhost:8080/dtr"
# Response: {"result": "ON"}

curl -X POST -d "action=off" "http://localhost:8080/rts"
# Response: {"result": "OFF"}
```
or
```bash
curl -X POST "http://localhost:8080/dtr?action=on"
# Response: {"result": "ON"}
```
