import bisect
import datetime
import os
import pytz
import requests

ds_key = os.environ['DS_KEY']
ds_url = 'https://api.darksky.net/forecast'
ds_apiparams = {'exclude': 'hourly,alerts,minutely', 'units': 'auto'}


def dwx_tz():
    return pytz.timezone(os.environ['DWX_TZ'])


def find_adjective(adjectives, cuts, number):
    return adjectives[bisect.bisect(cuts, number)]


def describe_temperature_change(today, yesterday, ystring='yesterday'):
    temp_adjectives = ['much cooler than', 'a little cooler than',
                       'about the same as', 'a little warmer than',
                       'much warmer than']
    if today['units'] == 'us':
        temp_cuts = [-10.0, -5.0, 5.0, 10.0]
    else:
        temp_cuts = [-5.5, -2.5, 2.5, 5.5]
    deltat = today['temperatureMax'] - yesterday['temperatureMax']
    return f"{find_adjective(temp_adjectives, temp_cuts, deltat)} {ystring}"


def describe_temperature(today, yesterday):
    return (f"High of {round(today['temperatureMax'])} " +
            f"({describe_temperature_change(today, yesterday)})")


def get_wx(date=None, offset=0):
    if not date:
        date = datetime.datetime.now()
    if offset:
        date += datetime.timedelta(days=offset)
    url_args = [os.environ['DWX_LATITUDE'],
                os.environ['DWX_LONGITUDE'],
                str(round(date.timestamp()))]
    url = f"{ds_url}/{ds_key}/{','.join(url_args)}"
    wx = requests.get(url, params=ds_apiparams).json()
    return dict(
        wx['daily']['data'][0],
        **{'units': wx['flags']['units']}
    )


def make_sentence(st):
    """Capitalize and add a full stop to a string."""
    st = st.strip().capitalize()
    return st + ('' if st.endswith('.') else '.')


def local_dow_from_ts(ts, tz):
    """Return string day of the week given epoch timestamp and timezone."""
    return (datetime.datetime.fromtimestamp(ts)
            .astimezone(tz)
            .strftime('%A'))


def describe_wx():
    wx_yesterday = get_wx(offset=-1)
    wx_today = get_wx()
    facts = [local_dow_from_ts(wx_today['time'], dwx_tz()),
             wx_today['summary'],
             describe_temperature(wx_today, wx_yesterday)]
    return ' '.join(map(make_sentence, facts))


if __name__ == '__main__':
    print(describe_wx())
