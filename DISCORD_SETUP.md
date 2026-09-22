# Discord Bot Setup

This lets you log transactions by typing them in a Discord channel (e.g. `200 - food`)
instead of running `cli.py` yourself every time. The bot just calls the same engine
`cli.py` uses, so `data/state.json` stays the single source of truth either way.

## 1. Create the Discord application + bot

1. Go to https://discord.com/developers/applications -> **New Application** -> give it
   a name (e.g. "Finance Bot") -> Create.
2. Open the **Bot** tab (a bot is created automatically with the app). Under
   **Privileged Gateway Intents**, turn on **MESSAGE CONTENT INTENT** -- the bot can't
   read your messages without this.
3. On the same page, click **Reset Token** and copy it. This is `DISCORD_BOT_TOKEN` --
   keep it secret, never commit it to git.

## 2. Invite the bot to your server

1. Open the **OAuth2 -> URL Generator** tab.
2. Under **Scopes**, check `bot`.
3. Under **Bot Permissions**, check `Send Messages`, `Read Message History`, `View Channel`.
4. Copy the generated URL at the bottom, open it in your browser, pick your server, authorize.

## 3. Get the channel ID (optional but recommended)

By default (no channel set) the bot only responds to **DMs** to keep it from replying
in a shared server channel to messages that aren't meant for it. If you'd rather use a
dedicated channel (e.g. `#finance`):

1. In Discord: User Settings -> Advanced -> turn on **Developer Mode**.
2. Right-click the channel -> **Copy Channel ID**. That's `DISCORD_CHANNEL_ID`.

## 4. Run it

```
pip install -r requirements.txt
export DISCORD_BOT_TOKEN="paste-your-token"
export DISCORD_CHANNEL_ID="paste-channel-id"   # omit to use DMs only
python3 discord_bot.py
```

Then in Discord type things like:
```
200 - food
Salary increased to 105000
dashboard
forecast
```

## 5. Keep it running 24/7

A terminal window closing kills the bot. On a Linux machine you keep on, the simplest
reliable option is `systemd`:

`/etc/systemd/system/finance-bot.service`:
```ini
[Unit]
Description=Personal finance Discord bot
After=network.target

[Service]
WorkingDirectory=/home/YOURUSER/finance
Environment=DISCORD_BOT_TOKEN=paste-your-token
Environment=DISCORD_CHANNEL_ID=paste-channel-id
ExecStart=/usr/bin/python3 discord_bot.py
Restart=on-failure
User=YOURUSER

[Install]
WantedBy=multi-user.target
```

Then:
```
sudo systemctl daemon-reload
sudo systemctl enable --now finance-bot
sudo journalctl -u finance-bot -f   # to watch logs
```

On macOS/Windows, or if you'd rather not use systemd, running it inside `tmux`/`screen`
(Linux/macOS) or as a Scheduled Task / `pm2` (Windows) works too -- anything that
restarts the process and keeps it attached to a persistent session.

## Notes

- `data/state.json` is written to on every transaction. If you also use `cli.py`
  yourself, both read/write the same file, so they stay in sync -- just don't run both
  at the exact same instant against the same file.
- The bot ignores messages it can't parse as a transaction (so normal chatter in a
  shared channel won't trigger spammy replies).
- Supported shorthand: `<amount> - <description>` (e.g. `500 - groceries`, `3.5k - trip`).
  Everything `cli.py` understands works too (see `README.md`).
