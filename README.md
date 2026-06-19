# Room Reservation Bot (Python)

A Telegram bot for creating and viewing room reservations, built with Python,
python-telegram-bot, and Firebase Firestore. Runs as a webhook server so it
can be deployed to Cloud Run and keeps working even when your computer is off.

This is a Python port of the original Java implementation, with the same
commands, parsing rules, and bot responses.

## Features

- Create room bookings with venue conflict detection
- View bookings by venue
- View bookings by date, today, or tomorrow
- View bookings created by your Telegram username
- Basic fallback handling for unknown commands
- Runs as an always-on webhook service (no long polling required)

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Telegram API | python-telegram-bot 21.5 |
| Webhook server | aiohttp |
| Database | Firebase Firestore via firebase-admin |
| Hosting | Google Cloud Run |
| Config | python-dotenv |

## Project Structure

```text
roombot-python/
├── main.py                  # Loads config, initializes Firebase, starts webhook server
├── bot.py                   # Routes incoming Telegram messages to command handlers
├── Dockerfile                # Container build for Cloud Run
├── requirements.txt
|
├── commands/
|   ├── cmd.py                # Base command class with send and argument helpers
|   ├── book_cmd.py           # /book - create a booking
|   ├── cancel_cmd.py         # /cancel - cancel a booking
|   ├── rooms_cmd.py          # /rooms - bookings for a venue
|   ├── date_cmd.py           # /date - bookings for a date
|   ├── today_cmd.py          # /tdy - today's bookings
|   ├── tmr_cmd.py            # /tmr - tomorrow's bookings
|   ├── mine_cmd.py           # /mine - bookings made by the current Telegram user
|   ├── help_cmd.py           # /help and /start
|   └── unknown_cmd.py        # Fallback for unrecognized commands
|
├── model/
|   └── reservation.py        # Reservation domain object and Firestore payload conversion
|
├── service/
|   ├── firestore_svc.py      # Low-level Firestore save/find/delete helpers
|   └── reservation_svc.py    # Reservation queries and conflict checks
|
├── firebase/
|   └── firebase_config.py    # Firebase Admin SDK initialization
|
└── util/
    ├── parse_date.py         # Date parsing
    ├── parse_time.py         # Time parsing
    ├── parse_venue.py        # Venue parsing — loads venues.json into an alias lookup
    └── parse_message.py      # Formats outgoing bot messages
```

## Prerequisites

- Python 3.12+
- A Telegram bot token from BotFather
- A Firebase project with Firestore enabled
- A Firebase service account key saved as `firebaseaccount.json` in the project root
- A Google Cloud project with billing enabled (required for Cloud Run, even on the free tier)
- The `gcloud` CLI installed and authenticated

## Setup

### 1. Add environment variables

Copy `.env.example` to `.env` and fill in your Telegram bot token:

```bash
cp .env.example .env
```

```env
BOT_TOKEN=your_telegram_bot_token_here
WEBHOOK_URL=
```

Leave `WEBHOOK_URL` blank for local development — the bot falls back to long
polling automatically when no `PORT` or `WEBHOOK_URL` is present. It's only
needed once you deploy.

### 2. Configure venues

Venues are configured through a `venues.json` file in the project root. This
file is gitignored since different deployments may need different rooms, so
each setup must create its own copy.

Copy the example file to get started:

```bash
cp venues.example.json venues.json
```

`venues.json` maps each canonical venue name to a list of accepted aliases:

```json
{
  "13L": ["13", "13l", "13 lounge", "level 13 lounge", "lvl 13 lounge"],
  "StudyRoom": ["study room", "12 study room", "level 12 study room"]
}
```

- The canonical name (the JSON key) is what gets saved in Firestore.
- Each string in the array is a user-facing input the bot will accept and normalise to that
canonical name — matching is case-insensitive.
- To add a new venue, add another key to the JSON file with the value as an array of recognised names for that venue

```json
{
  "13L": ["13", "13l", "13 lounge"],
  "MusicRoom": ["music room", "music rm", "mr"]
}
```

If `venues.json` is missing or malformed, the bot starts normally but every
venue lookup will fail — `/book` and `/rooms` will report an invalid venue
until the file is fixed.

### 3. Add Firebase credentials

Download a Firebase service account key and save it in the project root:

```text
firebaseaccount.json
```

Do not commit `.env`, `firebaseaccount.json` and `venues.json`.

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run locally

```bash
python main.py
```

With no `WEBHOOK_URL` set, this runs in long-polling mode — useful for local
testing without deploying anything.

## Deployment (Cloud Run + Webhooks)

Long polling requires your machine to stay on. To keep the bot running
continuously, deploy it as a webhook service on Cloud Run.

### 1. Enable billing and required APIs

Cloud Run requires a billing account linked to your project, even to use the
free tier. Create one at the
[Google Cloud Billing console](https://console.cloud.google.com/billing) and
link it to your project, then enable the APIs:

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com
```

### 2. Create a `.gcloudignore`

`gcloud` falls back to `.gitignore` rules when deciding what to upload, which
will silently exclude `firebaseaccount.json` and `venues.json` from your
build. Create an empty `.gcloudignore` to prevent this:

```bash
touch .gcloudignore
```

Verify both files will be included:

```bash
gcloud meta list-files-for-upload
```

### 3. Build the container

```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/roombot-python
```

### 4. Deploy (first pass — no webhook URL yet)

```bash
gcloud run deploy roombot-python \
  --image gcr.io/YOUR_PROJECT_ID/roombot-python \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --set-env-vars BOT_TOKEN=your_token_here
```

This gives you a Service URL like `https://roombot-python-xxxx-as.a.run.app`.
The container starts and binds its port correctly even without a webhook URl
set yet, but the webhook isn't registered with Telegram until the next step.

### 5. Redeploy with the webhook URL

```bash
gcloud run deploy roombot-python \
  --image gcr.io/YOUR_PROJECT_ID/roombot-python \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --set-env-vars BOT_TOKEN=your_token_here,WEBHOOK_URL=https://roombot-python-xxxx-as.a.run.app
```

On startup, the app calls Telegram's `setWebhook` with this URL. From this
point on, Telegram pushes updates directly to your Cloud Run service — no
polling, no need to keep your computer on.

### 6. Verify

Send `/start` to your bot on Telegram. If it replies with the help message,
you're done.

To check logs:

```bash
gcloud run services logs read roombot-python --region asia-southeast1 --limit 50
```

### Redeploying after code changes

Repeat steps 3 and 5 (rebuild, then redeploy with both env vars set). Step 5
only needs both vars because `--set-env-vars` replaces the full set each time
— omitting `WEBHOOK_URL` on a later deploy will unset it.

## Bot Commands

| Command | Description |
|---|---|
| `/book <venue> <date> <start> <end>` | Create a booking if it does not clash with an existing booking for that venue |
| `/cancel <venue> <date> <start> <end>` | Cancels a booking if it is made by the user |
| `/rooms <venue>` | Show bookings for a venue |
| `/date <date>` | Show bookings for a date |
| `/tdy` | Show today's bookings |
| `/tmr` | Show tomorrow's bookings |
| `/mine` | Show bookings made by your Telegram username |
| `/help`, `/start` | Show the help message |

There are no interactive menus or reply prompts in the current implementation.
Commands must include their required arguments directly.

## Booking Format

```text
/book <venue> <date> <start> <end>
```

Examples:

```text
/book 13L tomorrow 2pm 4pm
/book 13L mon 0900 1030
/book study room next fri 14:00 17:00
```

The bot canonicalizes recognized venue aliases before saving bookings. For
example, `13`, `13l`, and `13 lounge` are saved as `13L`.

## Supported Venues

Venues are configured through `venues.json` (see [Setup](#2-configure-venues)
above). The repository includes a reference set of venues and aliases in
`venues.example.json`:

```json
{
  "12L": ["12", "12l", "12 lounge", "level 12 lounge", "lvl 12 lounge"],
  "13L": ["13", "13l", "13 lounge", "level 13 lounge", "lvl 13 lounge"],
  "14L": ["14", "14l", "14 lounge", "level 14 lounge", "lvl 14 lounge"],
  "StudyRoom": ["study room", "12 study room", "level 12 study room", "12 study rm", "level 12 study rm"]
}
```

## Supported Dates

Accepted natural-language dates include:

```text
today
tdy
tonight
tomorrow
tmr
tmrw
mon
monday
next fri
next next mon
15 jun
jun 15
```

Numeric dates are parsed as day-month-year, not year-month-day:

```text
15-06-2026
15062026
15/06/26
```

All dates shown in bot responses are displayed in day-month-year format
(`dd-mm-yyyy`), regardless of how the date was entered.

## Supported Times

Accepted time formats include:

```text
3pm
3:30pm
15:30
1530
0900
noon
midnight
```

End time must be after start time. Bookings are currently same-day bookings.

## Firestore Data Model

Collection: `reservations`

```json
{
  "telehandle": "@vruaaan",
  "chatId": "123456789",
  "venue": "13L",
  "date_start": "2026-06-17",
  "time_start": "14:00",
  "date_end": "2026-06-17",
  "time_end": "17:00",
  "duration": 3.0,
  "createdAt": "<server timestamp>"
}
```

The document ID is generated by Firestore. Loaded documents are converted back
into `Reservation` objects with `Reservation.from_doc`.

Note: dates are stored in Firestore as ISO `yyyy-mm-dd` strings (as shown
above) — this is the internal storage format only. All bot-facing messages
display dates as `dd-mm-yyyy`.

## Bot Responses

### `/book`

#### Successful booking
```text
venue: 13L
date : 18-06-2026
time  : 14:00 - 16:00
poc: @vruaaan
```

#### Booking conflict
```text
This slot clashes with an existing booking.
```

### `/cancel`

#### Successful cancellation
```text
Booking for 13L on 18-06-2026 (14:00 - 16:00) cancelled
```

#### Cancel — no matching booking found
```text
No matching bookings found
```

#### Cancel — booking exists but belongs to someone else
```text
Booking found not made by you
```

### `/rooms` , `/date` , `/tdy` , `/tmr`

#### If there are bookings made
```text
Bookings made for 18-06-2026:
13L booked on 18-06-2026: 14:00 - 16:00 by @vruaaan
14L booked on 18-06-2026: 09:00 - 10:30 by @harris
```

#### If there are no bookings made
```text
No Bookings made for 18-06-2026
```

### `/mine`

#### If there are bookings made
```text
Bookings made by @vruaaan:
13L booked on 18-06-2026: 14:00 - 16:00
```

#### If user has no bookings made:
```text
You have no bookings made !
```

### `/help` , `/start`
````markdown
*Venue Booking Bot*
Book and manage room reservations right from Telegram.

*Commands*

/book <venue> <date> <start> <end>
Create a booking. Fails if it clashes with an existing one.
_e.g. /book 13L tomorrow 2pm 4pm_

/cancel <venue> <date> <start> <end>
Cancel a booking you made. Must match exactly, and you must be the one who made it.
_e.g. /cancel 13L tomorrow 2pm 4pm_

/rooms <venue>
View all bookings for a venue.
_e.g. /rooms 13L_

/date <date>
View all bookings for a specific date.
_e.g. /date next fri_

/tdy — view today's bookings
/tmr — view tomorrow's bookings
/mine — view your own upcoming bookings

/help, /start — show this message

*Accepted venues*
Defined in venues.json — ask your admin if you're unsure which names are recognised.

*Accepted dates*
today, tdy, tonight, tomorrow, tmr, mon, next fri, next next mon, 15 jun, jun 15, 15-06-2026, 15062026

*Accepted times*
2pm, 2:30pm, 14:00, 1400, noon, midnight

*Notes*
- Times must have an end after the start, or the booking is treated as overnight if the end time is earlier in the day.
- Numeric dates are read as day-month-year, not year-month-year.
- You can only cancel bookings made under your own Telegram username.
````

### General Error Messages

#### Invalid venue or date
```text
I couldn't understand the venue or time, refer to the proper formatting under /help
```

#### Invalid date only
```text
I couldn't understand the date
```

#### Invalid time format
```text
I couldn't understand the time. Try formats like 2pm, 14:00 or 1400.
```

### Unknown command
```text
Unknown command. Type /help to see what I can do.
```

### Internal error (e.g. Firestore unavailable)

```text
Something went wrong, please try again.
```

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| Container fails to start, port binding timeout | `firebaseaccount.json` or `venues.json` missing from the build — check `.gcloudignore` |
| `FileNotFoundError: firebaseaccount.json` in logs | File excluded from upload via `.gitignore` fallback — add an empty `.gcloudignore` |
| `RuntimeError: This event loop is already running` | Should not occur with the current webhook server implementation in `main.py`; if seen, confirm you're not calling `application.run_webhook()` directly |
| `gcloud.run.deploy unrecognized arguments` | A space after a comma in `--set-env-vars`, or an unreplaced placeholder like `<INSERT URL>` |
| Webhook not registered, bot doesn't respond | Redeploy with `WEBHOOK_URL` set — it must be included on every deploy or it gets unset |
