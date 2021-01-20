#!/usr/bin/env python
import os
import time
import discord
import asyncio
import datetime as dt
import requests                     # for registering/edititng/deleting commands with discord
import pytz
import zlib                         # for timezone name detection and daylight savings time detection
import json
from dotenv import load_dotenv      # for loading environmental variables (single file)
from dotenv import dotenv_values    # for loading from multiple .env files
import aiohttp                      # websocket client and rest requests

# set thius flag to True to assist with troubleshooting and dev
# in operation set to false
troubleshooting_flag = True

# this function enables easier printing of 
async def if_troubleshooting_print(*argv):
    if troubleshooting_flag == True:
        print(" ".join(argv))

# load application environment variables
bot_env = '../ignitebeta_bot.env'
app_env = '../ignitebeta_app.env'

# config = {
#     **dotenv_values(bot_env),  # load bot variables and token
#     **dotenv_values(app_env) # load app variables and token
#     }

load_dotenv(app_env)

# grab auth token
bot_token_field = 'BOT_TOKEN'
client_token_field = 'CLIENT_TOKEN'
#########
# last Token update: 12th Jan
# dev token last 7 days, requires manual update
#########

client_auth_token = os.getenv(client_token_field)
bot_auth_token = os.getenv(bot_token_field)

######################################
####### SLASH COMMANDS SECTION #######
####### SLASH COMMANDS SECTION #######
####### SLASH COMMANDS SECTION #######
######################################

# need to setup commands as asynchronous commands
#### GLOBAL COMMANDS #### (None at present)
    # testing setup of global slash commands
    #### for now, work with guild commands only as they update instantly. Once done, migrate to global commands
    #### global commands take circa 1hr to populate and be accessible
    #### will need to delete existing global commands
    # max number of global commands
    # https://discord.com/developers/docs/interactions/slash-commands#a-quick-note-on-limits

#### GUILD SPECIFIC COMMANDS
    # max number of guild commands = 50
    # https://discord.com/developers/docs/interactions/slash-commands#a-quick-note-on-limits

# base access address variables
guild_id = '307062314484629506'
application_id = '798030290865750046'
base_url = 'https://discord.com/api/v8/'
requests_auth_headers = {"Authorization": "Bearer "+ str(client_auth_token)}
bad_upload_command_str_code = 'not_uploaded_correctly'

def upload_all_commands(all_commands_dict):
    # takes a dict which is of format: command_key:json_dict_4_upload_value
    # returns a detailed dict of all commands and their generated id's, and reponses from upload
    # also prints a report of all response codes.
    # examples:

        # example input for 'all_commands_dict':
        #       {
        #       command_1_key:command_1_json_dict,
        #       command_2_key:command_2_json_dict,
        #       ...
        #       command_n_key:command_n_json_dict
        #       }
        # end example input.


        # example output returned:
        # all_guild_commands_dict_example = {
        #   'command_1': {
        #       'command_id': '1234567',                # stores discord unique command_id variable (believe it is string(id_number))
        #       'command_name':'bleppy',                # stores name (string) via which command is accessed (same as json "name" field), must be unique to guild
        #       'json_upload':{...}                     # the json upload (same as input json_dicts)
        #       'requests_response':requests_object     # the reponse object using requests lib, includes reponse code, and command object (json). 
        #       }
        #   'command_2':{...},
        #   ...
        #   'command_n':{...}
        #   }
        # end example output. 

    commands_dict = all_commands_dict
    url_upload = base_url + 'applications/' + application_id + '/guilds/' + guild_id + '/commands'

    # Upload each command and store reponse
    for key in list(commands_dict.keys()):
        # get command details
        commands_dict[key]
        json_payload = commands_dict[key]['json_upload']

        # upload and store response
        commands_dict[key]['request_response'] = requests.post(url_upload, headers = requests_auth_headers, json = json_payload)

        # if correct reponse code, store command_id and name
        if commands_dict[key]['request_response'].status_code == 201:
            commands_dict[key]['command_id'] = commands_dict[key]['request_response'].json()['id']
            commands_dict[key]['command_name'] = commands_dict[key]['request_response'].json()['name']
        # if incorrect, store 'not_uploaded_correctly' to further indicate command not accepted
        else: 
            commands_dict[key]['command_id'] = bad_upload_command_str_code
            commands_dict[key]['command_name'] = bad_upload_command_str_code
    
    # print report for each command: command name, reponse code
    for key in list(commands_dict.keys()):
        print(key + 'response: '+ command_response_report(request_response =  commands_dict[key]['request_response'], desired_reponse_code = 201))  

    return commands_dict

def command_response_report(request_response, desired_response_code):
    # short function for easier reporting on command uploads
    if request_response.status_code == desired_response_code:
         return 'OK: name: ' + request_response.json()['name'] + ' response code: '+ str(request_response.status_code)
    else:
       return 'ERROR: response code: '+ str(request_response.status_code)

def upload_one_command(command_json_dict):
    # if adding single command, can just use this function
    # takes a json_dict, returns a dict with command details and request.response.
    # also prints report from upload
    new_command_dict={'json_upload':command_json_dict}
    url_upload = base_url + 'applications/' + application_id + '/guilds/' + guild_id + '/commands'
    json_payload = command_json_dict
    #upload and store response
    new_command_dict['request_response'] = requests.post(url_upload, headers = requests_auth_headers, json = json_payload)
    
    if new_command_dict['request_response'].status_code == requests.codes.ok:
        new_command_dict['command_id'] = new_command_dict['request_response'].json()['id']
        new_command_dict['command_name'] = new_command_dict['request_response'].json()['name']
    else:
        new_command_dict['command_id'] = bad_upload_command_str_code
        new_command_dict['command_name'] = bad_upload_command_str_code
    print(command_response_report(request_response = new_command_dict['request_response'],desired_response_code = 201))
    return new_command_dict

def get_curr_guild_commands():
    # returns a list of dicts. each dict entry = a command.
    get_guild_commands_url = url_upload = base_url + 'applications/' + application_id + '/guilds/' + guild_id + '/commands'
    headers = {
        "Authorization": "Bearer "+ client_auth_token
    }
    get_commands_response  = requests.get(get_guild_commands_url, headers=headers)
    current_commands = get_commands_response.json()
    return current_commands

# delete all current commands from guild
def delete_all_guild_commands():
    delete_guild_command_url = base_url + 'applications/' + application_id + '/guilds/' + guild_id + '/commands'
    
    # get all guild commands (returns a list of dicts)
    all_guild_commands = get_curr_guild_commands()
    
    for command in all_guild_commands:
        command_id = command['id']
        del_response = requests.delete(delete_guild_command_url + '/' + command_id, headers = requests_auth_headers)
        del_status = del_response.status_code == 204
        print(command_id + ' deleted: '+ str(del_status))
    print('num current guild commands: '+ str(len(get_curr_guild_commands())))

new_command_json = {
    "name": "hello_world",
    "description": "hello world test implementation",
    "options": [{
            "name": "attitude",
            "description": "Do you want to be nice or rude",
            "type": 3,
            "required": True,
            "choices": [{
                    "name": "nice",
                    "value": "animal_dog"
                    },
                    {
                    "name": "rude",
                    "value": "animal_cat"
                    }
                ]
        }]
    }


#############################################
####### DISCORD GATEWAY SETUP SECTION #######
####### DISCORD GATEWAY SETUP SECTION #######
####### DISCORD GATEWAY SETUP SECTION #######
#############################################

# establish gateway class for connecting to discord gateway via websocket

class Gateway:
    # set gateway, choosing to communicate over JSON, and version 6
    DISCORD_GATEWAY = 'wss://gateway.discord.gg/?v=6&encoding=json'

    # gateway op code documentation: https://discord.com/developers/docs/topics/opcodes-and-status-codes#gateway-opcodes
    OP_CODES = {
        ## 'OP_CODE_NAME'      :   INT_CODE   ## CLIENT ACTION        ## DESCRIPTION
        'DISPATCH'             :   0,         # Receive               # An event was dispatched.
        'HEARTBEAT'            :   1,         # Send/receive          # Fired periodically by the client to keep the connection alive.
        'IDENTIFY'             :   2,         # Send                  # Starts a new session during the initial handshake.
        'PRESENCE'             :   3,         # Send                  # Update the client's presence.
        'VOICE_STATE'          :   4,         # Send                  # Used to join/leave or move between voice channels.
        'VOICE_PING'           :   5,      
        'RESUME'               :   6,         # Send                  # Resume a previous session that was disconnected
        'RECONNECT'            :   7,         # Receive               # You should attempt to reconnect and resume immediately.
        'REQUEST_MEMBERS'      :   8,         # Send                  # Request information about offline guild members in a large guild. 
        'INVALIDATE_SESSION'   :   9,         # Receive               # The session has been invalidated. You should reconnect and identify/resume accordingly.
        'HELLO'                :   10,        # Receive               # Sent immediately after connecting, contains the heartbeat_interval to use.
        'HEARTBEAT_ACK'        :   11,        # Receive               # Sent in response to receiving a heartbeat to acknowledge that it has been received.
        'GUILD_SYNC'           :   12      
        }
    
    OP_CODES_by_action = {
        'send':[1,2,3,4,6,8],
        'receive':[0,1,7,9,10,11]
        }



    def __init__(self, token: str):
        self.token = token
        self.sesh = aiohttp.ClientSession()
        self.hb_interval = None
        self.connected = False
        self._session_id = None
        self.sequence_num = None
        self.heartbeating = False
        self.heartbeat_acked = False
        

        # create event loop (starts paused)
        self.loop = asyncio.get_event_loop()

        # setup handling decompression of binary (zlib-compressed payloads)
        # https://discord.com/developers/docs/topics/gateway#encoding-and-compression

        self._zlib_suffix = b'\x00\x00\xff\xff'
        self._buffer = bytearray()
        self._inflator = zlib.decompressobj()
        
    async def main(self):
        async with self.sesh.ws_connect(Gateway.DISCORD_GATEWAY) as ws:

            # I think this is a class aiohttp.WsMessage
            async for ws_message in ws:
                
                # get the data from from the reponse
                res_payload = ws_message.data

                await if_troubleshooting_print('response received of class:',str(type(res_payload)))

                # if bytes (compressed zlib payload)
                if type(res_payload) is bytes:
                    # decrompress and store as msg
                    msg = await self.depack(response_data = res_payload)

                # if str (json)
                if type(res_payload) is str:
                    #load json to dict
                    # use aiohttp as the function receive_json is a coroutine
                    msg = ws_message.json()

                await if_troubleshooting_print('reponse payload:',str(msg))
               
                op = msg['op']

                ### handle the different gateway op codes:
                # handle gateway op for discord guild event
                if op == 0:

                    event_name = msg.get('t')
                    event_hander(event=event_name)
                    pass
                
                # handle other RECEIVED gateway websocket operations (setup, identify, resume, heartbeats etc)
                elif op in Gateway.OP_CODES_by_action['receive']:
                    #initial connection establishment:
                        # the initial flow on establishing a connections per the docs: https://discord.com/developers/docs/topics/gateway#connecting-to-the-gateway
                            # receive OPcode = 10 Hello
                            # extract heartbeat_interval from opcode10 hello msg
                            # commence sending opcode1 heartbeats every heartbeat_interval milliseconds
                                # NB: gateway may also request heartbeat, if received should send a heartbeat on request as well.
                            # client should send opcode 2 Identify

                    if op == Gateway.OP_CODES['HELLO']:
                        # receive only code
                        await if_troubleshooting_print('HELLO received')
                        
                        self.hb_interval = msg['d']['heartbeat_interval']

                        await if_troubleshooting_print('heartbeat interval set to:', str(self.hb_interval))

                        # start heartbeat service
                        # ensure_future required to protect against while loop from blocking.
                        asyncio.ensure_future(self.heartbeat_service(hb_interval = self.hb_interval, ws_response = ws))
                        #await self.heartbeat_service(hb_interval = self.hb_interval, ws_response = ws)

                    
                    if op == Gateway.OP_CODES['HEARTBEAT_ACK']:
                        # receive only code
                        # gateway message confirming it received heartbeat
                        await if_troubleshooting_print('heartbeat ACK received, setting heartbeat_acked to True')
                        self.heartbeat_acked = True

                    if  op == Gateway.OP_CODES['HEARTBEAT']:
                        # SEND OR RECEIVE
                        # gateway has requested a heartbeat,
                        # immediately send heartbeat
                        pass

                    if op == Gateway.OP_CODES['RECONNECT']:
                        # Receive only code
                        # You should attempt to reconnect and resume immediately.
                        pass

                    if op == Gateway.OP_CODES['INVALIDATE_SESSION']:
                        # Receive only code
                        # session invalidated
                        # should reconnect and identify/resume accordingly
                        pass
                    if op == Gateway.OP_CODES['GUILD_SYNC']:
                        # TODO: update send/ receive and ensure in appropriate section
                        # uncertain send / receive status
                        pass

                    if op == Gateway.OP_CODES['VOICE_PING']:
                        # TODO: update send/ receive and ensure in appropriate section
                        # uncertain send / receive status
                        pass

                    if op == Gateway.OP_CODES['RESUME']:
                        # Send only code
                        # Resume a previous session that was disconnected
                        pass

                    if op == Gateway.OP_CODES['REQUEST_MEMBERS']:
                        # Send only code
                        pass



                    if op == Gateway.OP_CODES['IDENTIFY']:
                        # send only code
                        # Starts a new session during the initial handshake.
                        pass

                    if op == Gateway.OP_CODES['PRESENCE']:
                        # Send only code
                        # Update the client's presence
                        pass

                    if op == Gateway.OP_CODES['VOICE_STATE']:
                        # send only code
                        # Used to join/leave or move between voice channels.
                        pass
                
                # invalid op code:
                else:
                    # invalid op code for received message
                    if troubleshooting_flag == True:
                        print('invalid op flag:' + str(op))
                    pass

    async def event_handler(self,event):
        if event == 'READY':
            self.sequence = res_payload['s']
            self.session_id = res_payload['d']['session_id'] 
        if event is None:
            print('No event!')
        pass
    
    async def heartbeat_send(self, ws_response):
        send_opcode = Gateway.OP_CODES['HEARTBEAT']

        last_sequence_received = self.sequence_num
        
        await if_troubleshooting_print('sending heartbeat')
        if last_sequence_received == None:
            last_sequence_received = 'null'
            #from docs:  The inner d key is the last sequence number—s—received by the client. If you have not yet received one, send null. https://discord.com/developers/docs/topics/gateway#heartbeat
        await self.send(op = send_opcode, d = last_sequence_received, ws_response = ws_response)
        self.heartbeat_acked = False
        await if_troubleshooting_print('heartbeat response sent, heartbeat_acked set to False')
    
    async def heartbeat_service(self, hb_interval, ws_response):

        #start heartbeat
        self.heartbeating = True

        # send first heartbeat
        await self.heartbeat_send(ws_response)

        # establish heartbeat loop        
        while self.heartbeating == True:
            
            await if_troubleshooting_print('waiting ', str(self.hb_interval/1000), 'seconds for next heartbeat')
            await asyncio.sleep(self.hb_interval/1000)

            # check last heartbeat was acked:
            if self.heartbeat_acked == True:
                # send next heartbeat
                await if_troubleshooting_print('heartbeat ACK flag is {}, sending next'.format(self.heartbeat_acked))
                await self.heartbeat_send(ws_response = ws_response)
            
            # if last heartbeat was NOT acked, handle zombie connection.
                # TODO
                # https://discord.com/developers/docs/topics/gateway#heartbeating-example-gateway-heartbeat-ack
                # a client does not receive a heartbeat ack between its attempts at sending heartbeats, it should immediately terminate the connection with a non-1000 close code, reconnect, and attempt to resume.
            else:
                await if_troubleshooting_print('no heartbeat ack received, zombied connection')
                self.heartbeating = False
                await if_troubleshooting_print("heartbeating status set to {}".format(self.heartbeating))

    async def send(self, op: int, d: int or dict or str, s: int = None, t: str = None, ws_response = None):
        # Payloads: https://discord.com/developers/docs/topics/gateway#payloads
            #
            # Gateway Payload Structure
            #
            # Field	Type	Description
            # +----------------------------------------------------------------------+
            # op	       integer	opcode for the payload
            # d	?mixed      (any JSON value)	event data
            # s	?integer *	sequence number, used for resuming sessions and heartbeats
            # t	?string *   the event name for this payload
            #
            # * s and t are null when op is not 0 (Gateway Dispatch Opcode).
            # Example Gateway Dispatch
                # {
                #   "op": 0,
                #   "d": {},
                #   "s": 42,
                #   "t": "GATEWAY_EVENT_NAME"
                # }
        
        payload = {
            "op": op,
            "d": d
        }

        if s:
            payload['s'] = s
        if t:
            payload['t'] = t
        
        await if_troubleshooting_print('payload prepared for sending:', str(payload))
        await ws_response.send_json(data = payload)

    async def depack(self, response_data):
        self._buffer.extend(response_data)

        if len(response_data) < 4 or response_data[-4] != self._zlib_suffix:
            return

        decompressed_response_data = self._inflator.decompress(self._buffer)
        self._buffer = bytearray()

        return decompressed_response_data

    def run(self):
        # initializes event loop
        try:
            self.loop.run_until_complete(self.main())
        finally:
            self.loop.close()

      

if __name__ == '__main__':
    gatewayClient = Gateway(client_auth_token)
    gatewayClient.run()
        

################################
####### BOT CODE SECTION #######
####### BOT CODE SECTION #######
####### BOT CODE SECTION #######
################################ 

# NB to allow bot to look at members, we have to specify that intent 
# it first has to be enabled on developer portal (done)
# same for reactions aparently (intent only, dont think it needs dev portal permission)

# consider using discord.py
intents = discord.Intents.default()
intents.members=True
intents.reactions = True
client = discord.Client(intents = intents)

# function to detect if daylight savings is active
# assumes hosted in Matts timezone.
# returns true if DST active, False if inactive
zonename = 'Australia/Melbourne'

# set this flag to true for bot to be very verbose to assist in dev / troubleshooting.



# define a custome event class for the bot to use:
# extract and stor specific components from the booking message for easier reference



# create class for holding default bot settings / custom settings for a discord server
class bot_settings:
    # should be initialized with a discord server (guild) object, bot_server = discord.guild object
    # https://discordpy.readthedocs.io/en/latest/api.html#guild
    def __init__(self, bot_server= None):
        self.region = self.bot_server.region
        # might be able to extract zone from guild.region, leave as hardcoded for now.
        self.timezone_name = 'Australia/Melbourne'
        # edict = "event dict"
        self.empty_edict = {
            'can_attend':[],
            'cannot_attend':[],
            'unsure':[],
            'no_response':[]
            }
        self.all_events_dict = {}
        self.event_status_dict = {}
        self.dst_flag = False
    
    def is_dst(zonename):
        tz = pytz.timezone(zonename)
        now = pytz.utc.localize(dt.datetime.utcnow())
        return now.astimezone(tz).dst() != dt.timedelta(0)

class event_booking:

        # should be initialized with a unique event id, and a discord message object
        # https://discordpy.readthedocs.io/en/latest/api.html#message

        def __init__(self, event_id=0, event_message= None):
            self.message_id = self.event_message.id
            self.message_content = self.event_message.content
            self.creation_time = self.event_message.created_at
            self.author = self.event_message.author
            
            self.server = self.event_message.guild
            self.channel = self.event_message.channel
            self.roles_mentioned = self.event_message.role_mentions
            self.event_listing = None












