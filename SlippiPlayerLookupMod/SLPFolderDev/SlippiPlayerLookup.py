import pandas as pd
import slippi as slp
import os
import re
import requests
from tkinter import *


#Load SLP FILE
gameFile = slp.Game('./Game.slp')

#Parse game file for player dict
players = gameFile.metadata.players
player1 = str(players[0])
player2 = str(players[1])

#regex pattern to get netplay code, inbetween keyword 'code=' and the next ',' character as per gameFile data structure
pattern = r'code=(.*?)(?=,\s*\w+=|\)$)'

# Search for the pattern in each players data
match1 = re.search(pattern, player1, re.DOTALL)
match2 = re.search(pattern, player2, re.DOTALL)

# Extract the value if match is found
if match1:
    player1 = match1.group(1).strip()
else:
    print("Code value not found.")

if match2:
    player2 = match2.group(1).strip()
else:
    print("Code value not found.")    






def GetPlayerData(netPlayName):

#define request headers for Slippi API 
#consider randomzing sec-ch-ua-platform, sec-ch-ua, user-agent 
    headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'apollographql-client-name': 'slippi-web',
    'content-type': 'application/json',
    'origin': 'https://slippi.gg',
    'priority': 'u=1, i',
    'referer': 'https://slippi.gg/',
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    }


#API Query json
    json_data = {
        'operationName': 'AccountManagementPageQuery',
        'variables': {
            'cc': netPlayName,
            'uid': netPlayName,
        },
        'query': 'fragment profileFields on NetplayProfile {\n  id\n  ratingOrdinal\n  ratingUpdateCount\n  wins\n  losses\n  dailyGlobalPlacement\n  dailyRegionalPlacement\n  continent\n  characters {\n    id\n    character\n    gameCount\n    __typename\n  }\n  __typename\n}\n\nfragment userProfilePage on User {\n  fbUid\n  displayName\n  connectCode {\n    code\n    __typename\n  }\n  status\n  activeSubscription {\n    level\n    hasGiftSub\n    __typename\n  }\n  rankedNetplayProfile {\n    ...profileFields\n    __typename\n  }\n  netplayProfiles {\n    ...profileFields\n    season {\n      id\n      startedAt\n      endedAt\n      name\n      status\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery AccountManagementPageQuery($cc: String!, $uid: String!) {\n  getUser(fbUid: $uid) {\n    ...userProfilePage\n    __typename\n  }\n  getConnectCode(code: $cc) {\n    user {\n      ...userProfilePage\n      __typename\n    }\n    __typename\n  }\n}\n',
    }

    #post requests to slippi api w/ headers and json data
    response = requests.post('https://gql-gateway-dot-slippi.uc.r.appspot.com/graphql', headers=headers, json=json_data)

    #200 success
    if response.status_code == 200:
        
        json_response = response.json()
        
        print("DisplayName: " + json_response['data']['getConnectCode']['user']['displayName'])
        print("Rating: " + str(json_response['data']['getConnectCode']['user']['rankedNetplayProfile']['ratingOrdinal']))
        print("Games this season " + str(json_response['data']['getConnectCode']['user']['rankedNetplayProfile']['ratingUpdateCount']))
        print("Wins this season: " + str(json_response['data']['getConnectCode']['user']['rankedNetplayProfile']['wins']))
        print("Losses this season : " + str(json_response['data']['getConnectCode']['user']['rankedNetplayProfile']['losses']))

        playerData = [json_response['data']['getConnectCode']['user']['displayName'],str(json_response['data']['getConnectCode']['user']['rankedNetplayProfile']['ratingOrdinal']),str(json_response['data']['getConnectCode']['user']['rankedNetplayProfile']['ratingUpdateCount']),str(json_response['data']['getConnectCode']['user']['rankedNetplayProfile']['wins']),str(json_response['data']['getConnectCode']['user']['rankedNetplayProfile']['losses'])]
        return playerData
    
    #uhoh
    else:

        print(f"Request failed with status code: {response.status_code}")
        print(response.text)  # Print the response content for debugging

#testing Getplayerdata func
GetPlayerData(player1)
print("######################")
GetPlayerData(player2)

test1 = GetPlayerData(player1)
test2 = GetPlayerData(player2)

#displayname, rank, games this season,wins,losses

user = Tk()
user.title("Application")

# Get screen width and height
w = user.winfo_screenwidth()
h = user.winfo_screenheight()

# Calculate new dimensions (one-fourth of the current screen size)
new_width = w // 2
new_height = h // 2

# Set window size and position
user.geometry("%dx%d+0+0" % (new_width, new_height))

# Configure window attributes for transparency effect
user.attributes('-alpha', 0.8)  # Adjust the alpha value as needed (0.0 to 1.0)

# Increase font size
font_size = 16

# Load images
image1 = PhotoImage(file="rank1.png").subsample(2)  # Subsample for better resolution
image2 = PhotoImage(file="rank1.png").subsample(2)  # Subsample for better resolution

# Create labels with images
label1 = Label(user, image=image1)
label1.grid(row=0, column=0, padx=20, pady=20)

label2 = Label(user, image=image2)
label2.grid(row=0, column=1, padx=20, pady=20)

label3 = Label(user, text="Display Name: " + test1[0], font=("Helvetica", font_size))
label3.grid(row=1, column=0, padx=20, pady=10)

label4 = Label(user, text="Display Name: " + test2[0], font=("Helvetica", font_size))
label4.grid(row=1, column=1, padx=20, pady=10)

label5 = Label(user, text="Ranking: " + test1[1], font=("Helvetica", font_size))
label5.grid(row=2, column=0, padx=20, pady=10)

label6 = Label(user, text="Ranking: " + test2[1], font=("Helvetica", font_size))
label6.grid(row=2, column=1, padx=20, pady=10)

# Center the grid in the middle of the window
user.grid_rowconfigure(0, weight=1)
user.grid_columnconfigure(0, weight=1)
user.grid_rowconfigure(2, weight=1)
user.grid_columnconfigure(2, weight=1)

user.mainloop()