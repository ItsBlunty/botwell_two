This is a new version of Botwell, for Joshua Bardwell's discord server.

Botwell was originally created by a user named Puck, and was a bot that allows you to search for videos on Joshua Bardwell's youtube channel.

This version is a revival of the original Botwell since we lost touch with Puck and had none of the original code.

This is a project by itsblunty, and is a project to learn Python and discord.py.

Botwell has quite a few features, including:
- Searching for videos on Joshua Bardwell's youtube channel
- Caching messages to a file, so that we can log deleted messages.
- A feedback command, that allows you to send feedback to the developers.
- A help command, that shows all the commands and their descriptions.

## Configuration

The bot reads the following environment variables (locally via a `.env` file, see `.env.example`):

| Variable | Required | Description |
| --- | --- | --- |
| `DISCORD_TOKEN` | yes | Discord bot token |
| `YOUTUBE_API_KEY` | yes | YouTube Data API v3 key (video search + new-video notifications) |
| `LOGGING_CHANNEL` | yes | Channel ID where deleted messages are logged |
| `VIDEO_CHANNEL` | yes | Channel ID where new-video announcements are posted |
| `DATA_DIR` | no | Directory for the pickle caches. Defaults to the project directory. Set this to a mounted volume path (e.g. `/data`) to persist caches across restarts. |

## Running locally

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py                # reads variables from a local .env file
```

## Deploying on Railway

This repo is ready to deploy on [Railway](https://railway.com) using the "Deploy from GitHub repo" flow:

1. Create a new project → **Deploy from GitHub repo** and pick this repository.
2. Railway builds it with Nixpacks (Python is detected from `requirements.txt` / `.python-version`) and starts it with `python main.py` (defined in `Procfile` and `railway.json`).
3. Under the service's **Variables** tab, add `DISCORD_TOKEN`, `YOUTUBE_API_KEY`, `LOGGING_CHANNEL`, and `VIDEO_CHANNEL`. (No `.env` file is needed in production — Railway injects these into the environment.)
4. **(Recommended) Persist the caches:** Railway containers have an ephemeral filesystem, so the `message_cache.pkl` / `video_cache.pkl` files are wiped on every restart or redeploy. To keep them, add a **Volume** to the service, then set `DATA_DIR` to the volume's mount path (e.g. `/data`).

This is a worker-style service (the bot connects out to Discord and does not serve HTTP), so it needs no public domain or exposed port.