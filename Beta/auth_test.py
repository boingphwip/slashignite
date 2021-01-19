#!/usr/bin/env python
# connect with discord server
import os
import discord
import datetime as dt
# for registering/edititng/responding to global slash commands in discord
import requests

#for timezone name detection and daylight savings time detection
import pytz
#for loading environmental variables
from dotenv import load_dotenv


# authorize link to add app and bot to the server
# https://discord.com/api/oauth2/authorize?client_id=798030290865750046&permissions=2147352535&scope=applications.commands%20bot



# https://discord.com/api/oauth2/authorize?response_type=code&client_id=157730590492196864&scope=identify%20guilds.join&state=15773059ghq9183habn&redirect_uri=https%3A%2F%2Fnicememe.website&prompt=consent

load_dotenv('../ignitebeta_app.env')


client_app_id = os.getenv('CLIENT_ID')
client_app_secret = os.getenv('CLIENT_SECRET')
client_app_public = os.getenv('CLIENT_PUBLIC')
client_app_redirect_uri = os.getenv('REDIRECT_URI')
client_auth_token = None

API_ENDPOINT = 'https://discord.com/api/v8'
CLIENT_ID = client_app_id
CLIENT_SECRET = client_app_secret
REDIRECT_URI = client_app_redirect_uri

# NB if this was ever deployed to a server,
# would require different oauth2 process which would include a refresh token.
# see https://discord.com/developers/docs/topics/oauth2#authorization-code-grant



def get_token():
    data = {
        'grant_type': 'client_credentials',
        'scope': 'applications.commands.update'
        }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        }
    r = requests.post('%s/oauth2/token' % API_ENDPOINT, data=data, headers=headers, auth=(client_app_id, client_app_secret))
    r.raise_for_status()
    return r.json()

auth_response = get_token()
print(auth_response)
client_auth_token = auth_response['access_token']
print(client_auth_token)


