# Discord bot
Discord bot with economy, shop and stats of each member of the server.

## Requirements
* Python 3.14.2
* VPS (server for run the bot)
* ``` requirements.txt``` 
* Api key of webhook and setup necessary permissions for run.

Setup your environment variables ``.env``:
```
DISCORD_TOKEN=<Your webhook discord token>
GUILD_ID=<Your guild id of your discord server>
CURRENCY_NAME=<Your bot discord name>
CURRENCY_SYMBOL=<Symbol of your coins>
DATABASE_URL=<Postgresql database url>
```
## Instructions
1. Clone the repositorie.
2. Setup your webhook api and set on permissions:
```
Presence Intent
Server Members Intent
Message Content Intent
```
And in Outh2:
```
Scope: bot
```
And whatever you want

3. In Outh2 copy the link and configure your web api en your discord server.
4. Setup your environment variables.
5. Execute 
```python
python main.py
```
Once done, your bot is running.
6. Check the commands putting `/` and select the icon of your webhook.
