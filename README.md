# Bot Indexer

------------------------------------------------
- [Install on server](#install)

- [Bot token and list of allowed users](#private)

- [Json keys](#keys)

- [Logs](#logs)

- [Keyboard in bot interface](#keyboard)

- [Add urls to index queue](#pushUrls)
    
- [Today's log](#getLog)
    
- [Check for urls](#checkUrls)
    
------------------------------------------------


## Install on the server<a name="install"></a>

1. Place the files **bot.py**, **main.py** and **script_mysql.py** on the server
2. Install all necessary libraries:

```
pip install aiogram

pip install requests

```

3. Create a folder json_keys, throw the keys there
4. Create a config.py file (put all private information there, more details [here](#private)).
5. Create an empty log.txt file

## Bot token and list of allowed users<a name="private"></a>


In the **config.py** file you need to add:
* TOKEN = 'bot token string'.
* IDS = [comma separated list of id's of all bot users]

## Json keys<a name="keys"></a>

Create a folder **json_keys,** throw all keys into it 


## Logs<a name="logs"></a>

Logs are created automatically in the _logs_ folder, each log has the name **log_current_date.txt** The log collects information about
about the sent urls, as well as the google api response. Each action is labeled with the time of the request and the username, 
who performed it

## Keyboard in the bot's interface<a name="keyboard"></a>

There are 3 main actions that are performed through the bot:

### Add urls to the indexing queue<a name="pushUrls"></a>

Accepts a list of urls. Limited by message size. Urls can also be sent without protocol, comma separated and in one line,
The bot reads them and converts them into the format needed to write them to a csv table. Each url with a new line is also supported

### Today's log<a name="getLog"></a>

On request, returns a txt file with the list of sent api urls, as well as the response from the api server

### Check for urls<a name="checkUrls"></a>


When any error occurs, all urls are saved in csv table, the script works in such a way that when eliminating errors and repeated access to it, the script sends all urls from csv table for indexing to avoid sending the same ones again.
errors and repeated access to it, the script will send all the urls from the csv table for indexing, to avoid repeated sending of the same
urls you can always check the presence of "hanging" urls, those that were accepted by the bot, but not processed by the script api.
