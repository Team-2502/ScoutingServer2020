# Scouting Server 2020

The server for the scouting system used by Team 2502 during Infinite Recharge


Currently requires the serial numbers of the tablets you will be using to send the match schedule


## Usage

###Requirements
1. On school Macs install Homebrew locally and then install Heroku via Homebrew, otherwise follow instructions on Heroku website

### Deploying to Heroku

1. Create a new branch called prod-heroku and commit sensitiveInfo.py with Slack/TBA/Firebase API keys and other info

2. Deploy to Heroku with `git push heroku prod-heroku:master`

### Running code via Heroku

1. Run Python using `heroku run python3 [file]`

2. Run bash using `heroku run bash`

3. Check active dynos (processes) using `heroku ps`

4. Kill all active dynos using `heroku ps:stop run` or a particular dyno using `heroku ps:stop run.[number]`

## Other

[Pyrebase API reference](https://github.com/thisbejim/Pyrebase)

[tbapy API reference](https://github.com/AndrewLester/tbapy)
