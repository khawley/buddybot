# -*- coding: utf-8 -*-

import forecastio
import os
import requests
from dotenv import load_dotenv
from slacker import Slacker

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

def get_env_variable(var_name):
    """ Get the environment variable or return exception """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s env variable" % var_name
        raise EnvironmentError(error_msg)

SLACK_API_KEY = get_env_variable('SLACK_API_KEY')
FORECASTIO_KEY = get_env_variable('FORECASTIO_KEY')

LOCALES = [
    {
        'name': 'Alameda, CA', 
        'zip':94501,
        'lat': '37.7712165',
        'lng': '-122.2824021',
    },
    {
        'name': 'Inner Richmond, SF, CA',
        'zip': 94118,
        'lat': '37.7822891',
        'lng': '-122.463708',
    },
    {
        'name': 'Pacifica, CA',
        'zip': 94044,
        'lat': '37.6138',
	    'lng': '-122.4869',
    },
    {
        'name': 'SOMA, SF, CA',
        'zip': 94103,
        'lat': '37.7726402',
        'lng': '-122.4099154',
    },
    {
        'name': 'Sydney, AU',
        'lat': '-33.865143',
        'lng': '151.209900',
    },
]

ICONS = {
    'clear-day': ':sunny:',
    'clear-night': ':full-moon:',
    'rain': ':umbrella:',
    'snow': ':snowflake:',
    'sleet': ':umbrella:+:snowflake:',
    'wind': ':dash:',
    'fog': ':foggy:',
    'cloudy': ':cloud:',
    'partly-cloudy-day': ':partly_sunny:',
    'partly-cloudy-night': ':cloud:',
}

slack = Slacker(SLACK_API_KEY)

def main():
    for locale in LOCALES:
        message = '{}: '.format(locale.get('name'))
        forecast = forecastio.load_forecast(
            FORECASTIO_KEY,
            locale['lat'],
            locale['lng'],
            units='us',
        )
        forecast_si = forecastio.load_forecast(
            FORECASTIO_KEY,
            locale['lat'],
            locale['lng'],
            units='si',
        )
        todays_data = forecast.daily().data[0].d
        todays_data_si = forecast_si.daily().data[0].d
        message += '{} {}, {}° - {}° ({}°C - {}°C)'.format(
            todays_data['summary'],
            ICONS[todays_data['icon']],
            todays_data['temperatureMin'],
            todays_data['temperatureMax'],
            todays_data_si['temperatureMin'],
            todays_data_si['temperatureMax'],
        )
        if todays_data.get('precipType'):
            message += ', {}% chance of {}'.format(
                todays_data['precipProbability'] * 100.0,
                todays_data['precipType'],
            )
        attachments = [
            {
                'fallback': message,
                'text': '{} {}, {}° - {}° ({}°C - {}°C)'.format(
                    todays_data['summary'],
                    ICONS[todays_data['icon']],
                    todays_data['temperatureMin'],
                    todays_data['temperatureMax'],
                    todays_data_si['temperatureMin'],
                    todays_data_si['temperatureMax'],
                )
            }
        ]
        if todays_data.get('precipType'):
            attachments[0]['text'] += '\n{}% chance of {}'.format(
                todays_data['precipProbability'] * 100.0,
                todays_data['precipType'],
            )
        send_buddybot_message(
            'Forecast for {}'.format(locale['name']), 
            attachments=attachments,
            channel='general',
        )


def send_buddybot_message(message, attachments=None, user=None, channel=None):
    if user:
        message_response = slack.chat.post_message(
            "@{}".format(user),
            message,
            attachments=attachments,
            username="BuddyBot",
            icon_emoji=":heart:",
        )
    if channel:
        message_response = slack.chat.post_message(
            "#{}".format(channel),
            message,
            attachments=attachments,
            username="BuddyBot",
            icon_emoji=":heart:",
        )


if __name__ == '__main__':
    main()
