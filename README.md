# UA Embassy Appointment Checker

Ukraine's appointment system is not the best. It requires citizens
to constantly check for appointments available. This becomes
burdersome in every day life, so we created this Telegram
bot that can do the checks in behalf of a person
and notify the user when an appointment opens.

Currently we only support passport pick-up appointment checks.

## Development

You need three main dependencies:

1. Docker
2. Python3.10+
3. Poetry

Installing Python3.10 and Poetry is platform dependent. In general,
we recommend installing the same version of Poetry that the Dockerfile
specifies, which is 1.6.1.

Poetry is sometimes a pain to work with to be honest. They recommend
[installing it](https://python-poetry.org/docs/#installing-with-pipx)
using pipx, but using pip seems to work okay.


## Running the telegram bot

Telegram bots use bot tokens in order for Telegram to dispatch the events to the right bot.

We have our Telegram bot, so ask Christofer for the token.

Then, in order to run, simply do

```code
export TELEGRAM_BOT_TOKEN=<my_token> && docker compose up --build
```

This will run the bot in the current shell, attached. If you want to run it in detached mode, use the `-d` flag to the docker compose command:

```code
docker compose up -d --build
```

