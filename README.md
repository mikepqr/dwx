# ∂wx

Today's weather compared to yesterday.

See [@dwxnyc](https://twitter.com/dwxnyc) and
[@dwxdtla](https://twitter.com/dwxdtla) for examples.

## Requirements

 - Python 3.6+, pytz, requests
 - For local use: Dark Sky API access
 - For deployment as a Twitter bot on AWS Lambda
   - AWS profile
   - Twitter account, application, and consumer key and access token
   - zappa, tweepy

## Local use

 - _Optional but recommended_: create a Python 3.6+ virtualenv, e.g.
   ```bash
   python3 -m virtualenv venv
   source venv/bin/activate
   ```
 - Install `pytz` and `requests` (e.g. `pip install -r requirements.txt`)
 - Sign up for the [Dark Sky API](https://darksky.net/dev/)
 - Add your Dark Sky API, and the latitude, longitude and timezone of the location to your environment, e.g. for Central Park
   ```bash
   export DS_KY="..."
   export DWX_LATITUDE="40.782222"
   export DWX_LONGITUDE="-73.965278"
   export DWX_TZ="US/Eastern"
   ```
 - Then run:
   ```bash
   $ python dwx.py
   Saturday. Mostly cloudy until evening. High of 75 (a little cooler than yesterday).
   ```

## Deployment of a Twitter bot that posts daily on AWS Lambda with zappa

AWS Lambda is an inexpensive way to post the output of `dwx.describe_weather()`
to Twitter once per day. zappa simplifies Lambda deployment.

 - _Required for zappa_: create a Python 3.6+ virtualenv (see above) and `pip
   install -r requirements.txt`
 - Install [zappa](https://github.com/Miserlou/Zappa) and tweepy (`pip
   install zappa tweepy`)
 - Create `zappa_settings.json`, e.g.
   ```json
   {
       "dev": {
           "profile_name": "default",
           "s3_bucket": "zappa-abcdefg123",
           "events": [{
              "function": "tweet.check_time_and_post",
              "expression": "cron(30 * * * ? *)"
           }]
           "environment_variables": {
               "DS_KEY": "...",
               "TW_CONSUMERKEY": "...",
               "TW_CONSUMERKEYSECRET": "...",
               "TW_ACCESSTOKEN": "...-...",
               "TW_ACCESSTOKENSECRET": "...",
               "DWX_LATITUDE": "40.782222",
               "DWX_LONGITUDE": "-73.965278",
               "DWX_TZ": "US/Eastern"
           }
       }
   }
   ```
   Set `profile_name` to the name of your AWS profile (see
   `~/.aws/credentials`). Set `s3_bucket` to something unique. This bucket is
   used for uploading the application but is otherwise left empty. Configure
   the environment variables using your API keys and location.
 - If you want to tweet at a local time other than 07:30am, edit `post_time` in
   `tweet.py` and set the first number in the cron schedule to the minute of
   your chosen time. E.g. if you want to tweet at 9:11 every day, set `
   "expression": "cron(11 * * * ? *)"`
 - Deploy and monitor with zappa
   ```bash
   $ zappa deploy dev
   ...
   $ zappa tail dev
   ```
