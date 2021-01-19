#!/usr/bin/env python
# connect with discord server
import os
import discord
import datetime as dt

#for timezone name detection and daylight savings time detection
import pytz

#for loading environmental variables
from dotenv import load_dotenv

# load environment variables
load_dotenv('ignitebeta.env')

# grab discord bot token for access
discord_token = os.getenv('DISCORD_TOKEN')

# client connection object


#NB to allow bot to look at members, we have to specify that intent 
# it first has to be enabled on developer portal (done)
# same for reactions aparently (intent only, dont think it needs dev portal permission)
intents = discord.Intents.default()
intents.members=True
intents.reactions = True
client = discord.Client(intents = intents)

# function to detect if daylight savings is active
# assumes hosted in Matts timezone.
# returns true if DST active, Fa;se if inactive
zonename = 'Australia/Melbourne'

# set this flag to true for bot to be very verbose to assist in dev / troubleshooting.
troubleshooting_flag = False

def is_dst(zonename):
    tz = pytz.timezone(zonename)
    now = pytz.utc.localize(dt.datetime.utcnow())
    return now.astimezone(tz).dst() != dt.timedelta(0)


#function to extract message info (author, message id, potentially role_mentions, creation time)
def msg_deets(message):
    message_details_dict = {}
    message_details_dict['message_id'] = message.id
    message_details_dict['author'] = message.author
    message_details_dict['author_id'] = message.author.id
    message_details_dict['creation_time'] = message.created_at
    message_details_dict['content'] = message.content
    message_details_dict['channel'] = message.channel
    message_details_dict['roles_mentioned'] = message.role_mentions
  
    return message_details_dict


#create log of active events
# key = event message id
# value = boolean (TRUE if event active, FALSE if inactive)
event_status_dict = {}

all_events_dict = {}

empty_edict = {
    'can_attend':[],
    'cannot_attend':[],
    'unsure':[],
    'no_response':[]
}



def get_message_from_id(message_id, channel):
    #placehodler
    #message = await message.
    return None

# initial connection confirmation
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

# reaction on basic message event
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!!hello'):
        await message.channel.send('Hello!')  

    ###### USER Roles reporting ######
    # self top role
    if message.content.startswith('!!mypowerlevel'):
        author_obj  = message.author
        author_id = message.author.id
        author_top_role = author_obj.top_role
        await message.channel.send(str(author_top_role))
    
    # self all roles
    if message.content.startswith('!!myroles'):
        author_obj  = message.author
        author_id = message.author.id

        #grab all names of roles into a list, as long as they are NOT the 'everyone' role.
        author_roles_list = [role.name for role in author_obj.roles if role != message.guild.default_role]

        # show the list of roles (joined as a string)
        num_roles = len(author_roles_list)
        await message.channel.send(content = message.author.name+ ' is a member of '+str(num_roles)+ ' roles: '+', '.join(author_roles_list), allowed_mentions = discord.AllowedMentions(everyone = False))

    # other user top role
        #placeholder
    # other user all roles
        #placeholder


    ###### ROLES lists of members ######
    if message.content.startswith('!!whodey'):
        who_dey = msg_deets(message)
    ## list of users for given roles
    if message.content.startswith('!!whodey'):
        who_dey = msg_deets(message)
        
        for role in who_dey['roles_mentioned']:
            role_members = role.members
            member_names_list  = [item.name for item in role_members]
            role_members_str = ", ".join(member_names_list)
            num_members = len(member_names_list)
            await message.channel.send('Role '+str(role)+' includes '+ str(num_members) + ' members: ' + role_members_str)
    
    # list of users for given role, NON TAGGED
    # i.e. if the role is just plain text after a particular role, match the role name and return the 'whodey'

    if message.content.startswith('!!whodey'):
        who_dey = msg_deets(message)
        
        for role in who_dey['roles_mentioned']:
            role_members = role.members
            member_names_list  = [item.name for item in role_members]
            role_members_str = ", ".join(member_names_list)
            num_members = len(member_names_list)
            await message.channel.send('Role '+str(role)+' includes '+ str(num_members) + ' members: ' + role_members_str)

    #get self details
    if message.content.startswith('!!whodis'):
        who_was = msg_deets(message)
        await message.channel.send('dis was '+ str(who_was['author'])+' at '+ str(who_was['creation_time'])+' with msg id of '+str(who_was['message_id'])+ ' author ID = '+str(who_was['author'].id))
    
    ## shows details of previous message in the channel
    if message.content.startswith('!!whodat'):
        channel = message.channel
        dat_was_message = await channel.history(limit=2).flatten()
        dat_was = msg_deets(dat_was_message[1])
        await message.channel.send('dat was '+ str(dat_was['author'])+' at '+ str(dat_was['creation_time'])+' with msg id of '+str(dat_was['message_id']))


    if message.content.startswith('!!time'):
        time = dt.datetime.now()
        dst_flag = is_dst(zonename)
        if dst_flag == True:
            await message.channel.send(str(time)+" (daylight savings active)")
        elif dst_flag == False:
            await message.channel.send(str(time)+" (no  daylight savings active)")
        

    # decent reaction monitoring and tracking users into groups will require embedding a message

    ## embed testing commences here



    if message.content.startswith('!!event_test'):
        msg_variables = msg_deets(message)
        #suggest limiting title length to n characters.
        title_string = str(message.content.replace('!!event_test',''))
        
        # need to grab group members of a message
        # add all users to a list
        initial_list = []
        if len(msg_variables['roles_mentioned']) == 0:
            initial_list = [msg_variables['author'].name]
        # grab all users for any roles tagged an put them in initial list for no response
        else:
            for group_tagged in msg_variables['roles_mentioned']:
                role_members = group_tagged.members
                member_names_list  = [item.name for item in role_members]
                title_string = str(title_string.replace(group_tagged.mention,''))
                initial_list.extend(member_names_list)
        
        embed=discord.Embed(title=title_string, description="a new event", color=0xFF5733)
        embed.add_field(name = 'Can attend', value = 0, inline = True)
        embed.add_field(name = 'Cannot attend', value = 0, inline = True )
        embed.add_field(name = 'Unsure', value = 0, inline = True)
        embed.add_field(name = 'No response', value = ", ".join(initial_list), inline = False)

        embed_message = await message.channel.send(embed=embed)    

        # troubleshooting
        if troubleshooting_flag == True:
            await message.channel.send('Event ID is: '+str(embed_message.id))

        # have bot setup reactions to its own event
        await embed_message.add_reaction("🇾")
        await embed_message.add_reaction("🇳")
        await embed_message.add_reaction("❓")
        await embed_message.add_reaction("⏩")
        await embed_message.add_reaction("⏪")        
        
        # add to active events list
        event_status_dict[embed_message.id] = True
        all_events_dict[str(embed_message.id)] = empty_edict
        all_events_dict[str(embed_message.id)]['no_response'] = initial_list
        all_events_dict[str(embed_message.id)]['event_message'] = embed_message
        ## create a dictionary specifically for this event

        #### old way
        # exec("edict_"+str(embed_message.id)+" = empty_edict")
        # exec("edict_"+str(embed_message.id)+ "['no_response'] = initial_list")


        
        #await embed_message.wait_for_reaction(['\N{SMILE}', custom_emoji], msg1)
        #await bot.say("You responded with {}".format(reaction.emoji))


# this one only works if the reaction is in cache of messages (basically messages that have occurred while the bot is active.)

# we could have it track messages not in cache, however this would also imply storage of event management in a file rather than in memory.
# means would have to load from file backup if needed.


# emojis can be altered to other unicode emojis
# however suggest leaving 'no_reaction' as it is hardcoded later. 
# 'no_reaction' string  was chosen over 'none'.
emoji_reaction_actions = {
    '🇾':'can_attend',
    '🇳':'cannot_attend',
    '❓':'unsure',
    'no_reaction':'no_response',
    '⏩':'later',
    '⏪':'earlier'
}

core_attendance_reactions = {
    '🇾':'can_attend',
    '🇳':'cannot_attend',
    '❓':'unsure'
}

event_field_idx_lookup = {
    'can_attend':0,
    'cannot_attend':1,
    'unsure':2,
    'no_response':3
}


#### When a user reacts to an event ####
@client.event
async def on_reaction_add(reaction, user):
    if user.name != 'IgnitionBot':
        # report reaction detected

        # troubleshooting
        if troubleshooting_flag == True:
            await reaction.message.channel.send('message id that was reacted to: '+str(reaction.message.id)+'by user: '+user.name)

        # check if reaction message is an event
        if reaction.message.id in event_status_dict.keys():
            # check reaction is a tracked reaction
            if str(reaction.emoji) in emoji_reaction_actions.keys():

                # get the category of the tracked reaction
                update_type = emoji_reaction_actions[str(reaction.emoji)]

                # store updated category in event entry
                value_update = all_events_dict[str(reaction.message.id)][update_type]

                ## check to see if list was had no one in it 
                if len(value_update) == 0:
                    value_update.append(user.name)

                elif value_update[0] == 'no one':
                    value_update.remove('no one')
                    value_update.append(user.name)
                else:
                    value_update.append(user.name)
                # replace dictionary entry for that category after removal
                all_events_dict[str(reaction.message.id)][update_type] = value_update

                #message to display what bot is doing
                # troubleshooting
                if troubleshooting_flag == True:
                    await reaction.message.channel.send('update ' + update_type + ' to now include ' + str(user.name))

                # lookup matching message id and grab the message embed
                new_embed = all_events_dict[str(reaction.message.id)]['event_message'].embeds[0]

                # select the correct index for the field that matches our update type
                idx_event_field = event_field_idx_lookup[update_type]

                # grab the existing name of the field that we are indexing
                name_field = new_embed.fields[idx_event_field].name

                # collect what we are replacing
                # set the field to the required, updated value
                new_embed.set_field_at(index = idx_event_field, name = name_field, value = ", ".join(value_update))
                
                # check if user was in no response category
                # get category
                update_type = emoji_reaction_actions['no_reaction']
                #check if username in category
                if user.name in all_events_dict[str(reaction.message.id)][update_type]:
                    
                    # grab category list
                    value_update = all_events_dict[str(reaction.message.id)][update_type]
                    # remove user
                    value_update.remove(user.name)
                    # if no user left in no response category, add placeholder 'no one'
                    if len(value_update) == 0:
                        value_update.append('no one')
                    
                    #update dict
                    all_events_dict[str(reaction.message.id)][update_type] = value_update

                    # now update the embed for the no response field
                    # get field index
                    idx_event_field = event_field_idx_lookup[update_type]
                    # get field name
                    name_field = new_embed.fields[idx_event_field].name
                    # set the field to the required, updated value
                    new_embed.set_field_at(index = idx_event_field, name = name_field, value = ", ".join(value_update))

                # update the event post
                await all_events_dict[str(reaction.message.id)]['event_message'].edit(embed = new_embed)

                



        pass
    
#### When a user removes a reaction to an event ####
@client.event
async def on_reaction_remove(reaction, user):
    if user.name != 'IgnitionBot':
        # report reaction detected
        # troubleshooting
        if troubleshooting_flag == True:
            await reaction.message.channel.send('message id that was reacted to: '+str(reaction.message.id)+'by user: '+user.name)

        # check if reaction message is an event
        if reaction.message.id in event_status_dict.keys():
            # check reaction is a tracked reaction 
            if str(reaction.emoji) in emoji_reaction_actions.keys():

                # get the category of the tracked reaction
                update_type = emoji_reaction_actions[str(reaction.emoji)]

                # get current value for that category
                value_update = all_events_dict[str(reaction.message.id)][update_type]
                # remove user from that category
                value_update.remove(user.name)

                ## check to see if list is now empty
                if len(value_update) == 0:
                    value_update.append('no one')
                else:
                    pass

                # replace dictionary entry for that category after removal
                all_events_dict[str(reaction.message.id)][update_type] = value_update

                # message to display what bot is doing
                # troubleshooting
                if troubleshooting_flag == True:
                    await reaction.message.channel.send('update ' + update_type + ' to now remove ' + str(user.name))

                # lookup matching message id and grab the message embed
                new_remove_embed = all_events_dict[str(reaction.message.id)]['event_message'].embeds[0]

                # select the correct index for the field that matches our update type
                idx_event_field = event_field_idx_lookup[update_type]

                # grab the existing name of the field that we are indexing
                name_field = new_remove_embed.fields[idx_event_field].name

                # collect what we are replacing
                # set the field to the required, updated value
                new_remove_embed.set_field_at(index = idx_event_field, name = name_field, value = ", ".join(value_update))

                # check if user has any other reponses (to the key tracked reaction categories)
                # get list of all reactions
                all_users_attendance_reacted = []
                for tracked_reaction in core_attendance_reactions.keys():
                    #get the category
                    category = emoji_reaction_actions[tracked_reaction]
                    # get the list of reactions for that category
                    list_category_reactions = all_events_dict[str(reaction.message.id)][category]
                    # add all users reacting to category to  to 'all user reactions' list
                    all_users_attendance_reacted.extend(list_category_reactions)
                
                # if they now dont have a reaction in the attendance reaction set, then put them in 'no response'
                if user.name not in all_users_attendance_reacted:

                    # set the update category
                    update_type = emoji_reaction_actions['no_reaction']

                    #get field index for category
                    idx_event_field = event_field_idx_lookup[update_type]
                    # get field name
                    name_field = new_remove_embed.fields[idx_event_field].name

                    # grab existing 'no reponse' set
                    value_update = all_events_dict[str(reaction.message.id)][update_type]
                    # if no one, remove it
                    if value_update[0] == 'no one':
                        value_update.remove('no one')
                    # add user
                    value_update.append(user.name)
                    # update dict
                    all_events_dict[str(reaction.message.id)][update_type] = value_update
                    
                    # update embed category for no response as well.
                    # the above grabbed embed already included all fields, so we just need to edit the no response field
                    new_remove_embed.set_field_at(index = idx_event_field, name = name_field, value = ", ".join(value_update))
            
                # update the event post
                await all_events_dict[str(reaction.message.id)]['event_message'].edit(embed = new_remove_embed)


        pass



#reaction events can take place from any message using the followed:
# howeve elected not to use this and just use reactions on messages in cache.
# @client.event
# async def on_raw_reaction_add(reaction):
#     if reaction.message_id in event_status_dict.keys():
#         reply  = discord.Message
#         reply.channel
#          await message.channel.send('you reacted to an event')

# consider using raw_reaction add for robustness in future (though likely slower bot).





# should change and remove exec() functions with custom variable object names
# and instead store the objects inside a dictionary called events where the key is the message id
# the value is then another 
    

### future features:
# command for setting bot region
# proper class setup

# should create an event class
    # that way can have events for groups e.g. list of among us events
    # list of active events
    # events can then have better properties, as well as class emthods

# once times are set for events, (via either +3.5 e.g. +3.5 hours from now rounded to nearest 15 min)
# or alternatively with a datetime
# allow the event author to +1 hour via command, or reaction
# alternatively, track the event author clicking on forward and back
# i.e. have the forward and back indicate votes for other people, 
# and change scheduled time by repeat reacitons for the author.

# could add dual reaction feature:
# if user has reacted as both can attend and unsure = probably attend
# if user reacts both cannot and unsure, = probably cannot
# start session
client.run(discord_token)

