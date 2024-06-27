import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import slippi as slp
import re
import requests
from tkinter import *


# Global references to images to prevent garbage collection
playerOneRank = None
playerTwoRank = None


# Returns players netplay codes from slp file
def getNetplayCodes(gameFilePath):
    netplayCodes = []

    while True:
        try:
            gameFile = slp.Game(gameFilePath)
            break
        except Exception as e:
            print("Waiting for game to finish...")
            time.sleep(5)

    # Parse game file for player dict
    players = gameFile.metadata.players
    player1 = str(players[0])
    player2 = str(players[1])

    # regex pattern to get netplay code, in between keyword 'code=' and the next ',' character as per gameFile data structure
    pattern = r'code=(.*?)(?=,\s*\w+=|\)$)'

    # Search for the pattern in each player's data
    match1 = re.search(pattern, player1, re.DOTALL)
    match2 = re.search(pattern, player2, re.DOTALL)

    # Extract the value if match is found
    if match1:
        netplayCodes.append(match1.group(1).strip())
    else:
        print("Code value not found.")

    if match2:
        netplayCodes.append(match2.group(1).strip())
    else:
        print("Code value not found.")

    return netplayCodes

# Function to fetch player data from Slippi API
def getPlayerData(netPlayName):
    # Headers for Slippi API request
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

    # API Query json
    json_data = {
        'operationName': 'AccountManagementPageQuery',
        'variables': {
            'cc': netPlayName,
            'uid': netPlayName,
        },
        'query': 'fragment profileFields on NetplayProfile {\n  id\n  ratingOrdinal\n  ratingUpdateCount\n  wins\n  losses\n  dailyGlobalPlacement\n  dailyRegionalPlacement\n  continent\n  characters {\n    id\n    character\n    gameCount\n    __typename\n  }\n  __typename\n}\n\nfragment userProfilePage on User {\n  fbUid\n  displayName\n  connectCode {\n    code\n    __typename\n  }\n  status\n  activeSubscription {\n    level\n    hasGiftSub\n    __typename\n  }\n  rankedNetplayProfile {\n    ...profileFields\n    __typename\n  }\n  netplayProfiles {\n    ...profileFields\n    season {\n      id\n      startedAt\n      endedAt\n      name\n      status\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery AccountManagementPageQuery($cc: String!, $uid: String!) {\n  getUser(fbUid: $uid) {\n    ...userProfilePage\n    __typename\n  }\n  getConnectCode(code: $cc) {\n    user {\n      ...userProfilePage\n      __typename\n    }\n    __typename\n  }\n}\n',
    }

    # Post requests to Slippi API with headers and json data
    response = requests.post('https://gql-gateway-dot-slippi.uc.r.appspot.com/graphql', headers=headers, json=json_data)

    # Check if request was successful (status code 200)
    if response.status_code == 200:
        json_response = response.json()
        playerData = [
            json_response['data']['getConnectCode']['user']['displayName'],
            str(json_response['data']['getConnectCode']['user']['rankedNetplayProfile']['ratingOrdinal']),
            str(json_response['data']['getConnectCode']['user']['rankedNetplayProfile']['ratingUpdateCount']),
            str(json_response['data']['getConnectCode']['user']['rankedNetplayProfile']['wins']),
            str(json_response['data']['getConnectCode']['user']['rankedNetplayProfile']['losses'])
        ]
        return playerData
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(response.text)  # Print the response content for debugging
        return None

def get_rank(elo):
    ranks = [
        (0, "Bronze 1"),(765, "Bronze 1"),(766, "Bronze 2"),(913, "Bronze 2"), (914, "Bronze 3"),(1054, "Bronze 3"),
        (1055, "Silver 1"),(1188, "Silver 1"),(1189, "Silver 2"),(1315, "Silver 2"), (1316, "Silver 3"),(1436, "Silver 3"),
        (1436, "Gold 1"),(1546, "Gold 1"), (1549, "Gold 2"),(1654, "Gold 2"), (1654, "Gold 3"),(1751, "Gold 3"),
        (1752, "Platinum 1"),(1842, "Platinum 1"), (1843, "Platinum 2"),(1927, "Platinum 2"), (1928, "Platinum 3"),(2003, "Platinum 3"),
        (2004, "Diamond 1"),(2074, "Diamond 1"), (2074, "Diamond 2"),(2136, "Diamond 2"), (2137, "Diamond 3"),(2191, "Diamond 3"),
        (2192, "Master 1"),(2274, "Master 1"), (2275, "Master 2"),(2350, "Master 2"), (2350, "Master 3"),(2350, "Master 3"),
        (float('inf'), "Grandmaster")
    ]

    for threshold, rank in ranks:
        if elo <= threshold:
            return rank

def get_player_ranks(elo1, elo2):
    rank1 = get_rank(elo1)
    rank2 = get_rank(elo2)
    return rank1, rank2

def get_rank_image(elo):
    images = [
        (0, "Bronze.png"),(1054, "Bronze.png"),
        (1055, "Silver.png"),(1436, "Silver.png"),
        (1436, "Gold.png"),(1751, "Gold.png"),
        (1752, "Platinum.png"),(2003, "Platinum.png"),
        (2004, "Diamond.png"),(2191, "Diamond.png"),
        (2192, "Masters.png"),(2350, "Masters.png"),
        (float('inf'), "Grandmaster.png")
    ]

    for threshold, rank in images:
        if elo <= threshold:
            return "./RankIcons/"+ rank

def get_player_rank_images(elo1, elo2):
    rank1 = get_rank_image(elo1)
    rank2 = get_rank_image(elo2)
    return rank1, rank2

# Function to update GUI labels with player data
def update_data(player1, player2):
    global playerOneRank, playerTwoRank  # Ensure we keep references to these images
    rankImages = get_player_rank_images(int(float(player1[1])), int(float(player2[1])))
    rank = get_player_ranks(int(float(player1[1])), int(float(player2[1])))
    # Load images
    playerOneRank = PhotoImage(file=rankImages[0]).subsample(2)  # Subsample for better resolution
    playerTwoRank = PhotoImage(file=rankImages[1]).subsample(2)  # Subsample for better resolution   
    
    
    # Update labels with new data
    label1.config(image=playerOneRank)
    label2.config(image=playerTwoRank)
    label3.config(text="Display Name: " + player1[0])
    label4.config(text="Display Name: " + player2[0])
    label5.config(text="Ranking: " + player1[1])
    label6.config(text="Ranking: " + player2[1])
    label7.config(text="Rank: " + rank[0])
    label8.config(text="Rank: " + rank[1])

# Function to start the GUI
def startGui():
    global user, label1, label2, label3, label4, label5, label6, label7, label8

    # Create the main window
    user = Tk()
    user.title("Slippi Player Monitor")

    # Set window size
    window_width = 800
    window_height = 600

    # Calculate screen center
    screen_width = user.winfo_screenwidth()
    screen_height = user.winfo_screenheight()

    # Calculate offsets for centering window with even spacing on both sides
    x_offset = (screen_width - window_width) // 2
    y_offset = (screen_height - window_height) // 2

    # Position window at center with even spacing on both sides
    user.geometry(f"{window_width}x{window_height}+{x_offset}+{y_offset}")

    # Create a Canvas widget to hold the background image
    canvas = Canvas(user, width=window_width, height=window_height)
    canvas.grid(row=0, column=0, columnspan=3, rowspan=5, sticky=(N, S, E, W))

    # Load background image with transparency and center it on the canvas
    bg_image = PhotoImage(file="background.png").subsample(2, 2)  # Resize if necessary
    bg_width = bg_image.width()
    bg_height = bg_image.height()
    bg_x = (window_width - bg_width) // 2
    bg_y = (window_height - bg_height) // 2
    canvas.create_image(bg_x, bg_y, image=bg_image, anchor="nw")

    # Set canvas transparency (optional)
    canvas.configure(bg='black', highlightthickness=0)  # Set canvas background color for transparency effect

    # Configure window attributes for transparency effect
    user.attributes('-alpha', 0.9)  # Adjust the alpha value as needed (0.0 to 1.0)

    # Increase font size
    font_size = 16  # Adjust font size based on preference

    # Create labels for player icons and vs image
    label1 = Label(user)
    label1.grid(row=1, column=0, padx=20, pady=10)

    vs_image = PhotoImage(file="./vs.png")
    vs_image = vs_image.subsample(2, 2)  # Resize vs_image to half
    vs_label = Label(user, image=vs_image)
    vs_label.grid(row=1, column=1, padx=10, pady=10)

    label2 = Label(user)
    label2.grid(row=1, column=2, padx=20, pady=10)

    # Player info labels (centered under images)
    label3 = Label(user, text="Player 1:", font=("Helvetica", font_size))
    label3.grid(row=2, column=0, padx=10, pady=5)

    label4 = Label(user, text="Player 2:", font=("Helvetica", font_size))
    label4.grid(row=2, column=2, padx=10, pady=5)

    label5 = Label(user, text="Ranking:", font=("Helvetica", font_size))
    label5.grid(row=3, column=0, padx=10, pady=5)

    label6 = Label(user, text="Ranking:", font=("Helvetica", font_size))
    label6.grid(row=3, column=2, padx=10, pady=5)

    label7 = Label(user, text="Rank:", font=("Helvetica", font_size))
    label7.grid(row=4, column=0, padx=10, pady=5)

    label8 = Label(user, text="Rank:", font=("Helvetica", font_size))
    label8.grid(row=4, column=2, padx=10, pady=5)

    
    player1_image = PhotoImage(file="./RankIcons/Silver.png")
    player1_image = player1_image.subsample(2, 2)  # Resize player1_image to half
    player2_image = PhotoImage(file="./RankIcons/Silver.png")
    player2_image = player2_image.subsample(2, 2)  # Resize player2_image to half

    label1.config(image=player1_image)
    label2.config(image=player2_image)

    user.mainloop()

def run_with_retry(func, *args, **kwargs):
    """
    Runs a function with the provided arguments and keyword arguments.
    If the function raises an exception, it will wait for 5 seconds and retry.
    
    :param func: The function to be executed.
    :param args: Positional arguments for the function.
    :param kwargs: Keyword arguments for the function.
    """
    while True:
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            print("Waiting for match to finish...")
            time.sleep(5)


# Define a custom event handler by subclassing FileSystemEventHandler
class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return  # Ignore directories
        print(f"New Game: {event.src_path}")

        path = event.src_path.replace("\\", "/")
        # Fetch netplay codes from SLP file
        time.sleep(3)  # Simulate processing delay (you can remove this in production)

        netPlayCodes = getNetplayCodes(path)

        if len(netPlayCodes) == 2:
            player1 = getPlayerData(netPlayCodes[0])
            player2 = getPlayerData(netPlayCodes[1])
            

            
            
            if player1 and player2:
                # Update GUI with player data
                user.after(0, update_data, player1, player2)  # Use after() to update GUI from non-GUI thread

def monitor_directory(directory):
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=directory, recursive=False)
    observer.start()
    print(f"Monitoring directory '{directory}' for new games...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Function to run directory monitoring in a separate thread
def run_monitoring(directory):
    threading.Thread(target=monitor_directory, args=(directory,), daemon=True).start()

if __name__ == "__main__":

    directory_to_watch = "./SLPFolderDev"  # Change this to slippie slp folder EX: C:Users/199x/Documents/Slippi

    run_monitoring(directory_to_watch)
    startGui()
