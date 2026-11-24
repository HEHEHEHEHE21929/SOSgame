# Magyar Politika

A classroom-friendly Hungarian political party simulator inspired by early strategy games. It uses Flask and vanilla JavaScript. Political support, county outcomes and seat allocations are simplified game mechanics, not exact history.

## Run locally

```sh
pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000>.

## Deploy on Render

Create a Render **Web Service** connected to this GitHub repository.

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`

No external CDNs or media files are used. Sound is synthesized after the first browser click.

## Controls

- PAUSE, 1x, 2x and 4x control time.
- Space toggles pause; 1, 2 and 3 select 1x, 2x and 4x.
- Use the Game tab to copy or paste a save code.
- Click a county on the map to inspect it.
