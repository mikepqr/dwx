# ∂wx

Today's weather compared to yesterday.

See [@dwxnyc](https://twitter.com/dwxnyc) and
[@dwxdtla](https://twitter.com/dwxdtla) for examples.

## Requirements

 - Python 3.6+, pytz, requests
 - For local use
   - [Dark Sky API](https://darksky.net/dev/)
 - For deployment as a Twitter bot on AWS Lambda
   - AWS profile
   - Twitter account, application, and consumer key and access token
   - zappa, tweepy

## Local use

 - _Optional but recommended_: create and activate a Python 3.6+ virtualenv,
   e.g.
   ```bash
   python3 -m virtualenv venv
   source venv/bin/activate
   ```
 - Install `pytz` and `requests` (e.g. `pip install -r requirements.txt`)
 - Add your Dark Sky API key, and the latitude, longitude and timezone of the location to your environment, e.g. for Central Park
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

## AWS Lambda/zappa deployment of a Twitter bot that posts daily

AWS Lambda is an inexpensive way to post the output of `dwx.describe_wx()`
to Twitter once per day. [zappa ](https://github.com/Miserlou/Zappa) simplifies
Lambda deployment.

 - _Required for zappa_: create and activate a Python 3.6+ virtualenv (see
   above) and `pip install -r requirements.txt`
 - Install zappa and tweepy to the virtual environment (`pip install zappa
   tweepy`)
 - Create `zappa_settings.json`, e.g.
   ```json
   {
       "dev": {
           "profile_name": "default",
           "s3_bucket": "zappa-abcdefg123",
           "events": [{
              "function": "tweet.check_time_and_post",
              "expression": "cron(30 * * * ? *)"
           }],
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
   `~/.aws/credentials`). Set `s3_bucket` to something unique (this bucket is
   used for uploading the application but is otherwise left empty). Configure
   the environment variables using your API keys and location.
 - If you want to tweet at a local time other than 07:30am, edit `post_time` in
   `tweet.py` and set the first number in the cron schedule to the minute of
   your chosen time. E.g. if you want to tweet at 03:14am every day, set
   `post_time = datetime.time(3, 14)` in `tweet.py` and ` "expression":
   "cron(14 * * * ? *)"` in `zappa_secttings.json`.
 - Deploy and monitor with zappa
   ```bash
   $ zappa deploy dev
   ...
   $ zappa tail dev
   ```

## A note about time zones and daily jobs

Recurring Lambda functions can be scheduled with cron-like syntax. AWS runs in
UT, which means the cron schedules must also be in UT. This is not a problem
for jobs that recur all day. But if a job is supposed to run at a particular
local time each day (or start/stop at a particular time) it makes things
tricky.

The hacky solution is to change to cron configuration every time the clocks go forward
or back.

The slightly less hacky solution, which is what ∂wx does when configured as a
Twitter bot, is to have Lambda run the function hourly, but check the local
time inside the Python application. If it's not the correct local time, the
tweet doesn't get posted. This all happens in
[tweet.py](https://github.com/williamsmj/dwx/blob/master/tweet.py).
