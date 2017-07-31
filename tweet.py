import datetime
import os
import tweepy
import dwx

post_time = datetime.time(7, 30)
post_time_tol_seconds = 5 * 60


def post_time_today(dt):
    """Return today's post_time as a fully qualified datetime."""
    return dt.replace(hour=post_time.hour,
                      minute=post_time.minute,
                      second=0, microsecond=0)


def get_times():
    """Return time in server timezone, local time in location timezone, and
    target post_time in location timezone."""
    server = datetime.datetime.now().astimezone()
    local = server.astimezone(dwx.dwx_tz())
    target = post_time_today(local)
    return {'server': server, 'local': local, 'target': target}


def check_time():
    """Return True if within post_time_tol_seconds of post_time in timezone of
    location."""
    times = get_times()
    time_difference = abs((times['local'] - times['target']).total_seconds())
    return time_difference < post_time_tol_seconds


def make_api():
    auth = tweepy.OAuthHandler(os.environ['TW_CONSUMERKEY'],
                               os.environ['TW_CONSUMERKEYSECRET'])
    auth.set_access_token(os.environ['TW_ACCESSTOKEN'],
                          os.environ['TW_ACCESSTOKENSECRET'])
    return tweepy.API(auth)


def post(tweet):
    api = make_api()
    api.update_status(tweet)


def format_times(times):
    return {k: str(v) for k, v in times.items()}


def check_time_and_post():
    print(format_times(get_times()))
    if check_time():
        tweet = dwx.describe_wx()
        post(tweet)
    else:
        print('Not time yet.')
