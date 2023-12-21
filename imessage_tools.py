import sqlite3
import datetime
import subprocess
import os

# db.py 

# Connect to
import sqlite3
import os 
import datetime
import math
import pytz

# Works for mac Catalina
home = os.environ['HOME']
db_path = f'{home}/Library/Messages/chat.db'
conn = sqlite3.connect(db_path, uri=True)
cursor = conn.cursor()
    
def clean_up():
    if conn:
        conn.close()


def get_chat_mapping():
    global cursor
    cursor.execute("SELECT room_name, display_name FROM chat")
    result_set = cursor.fetchall()
    mapping = {room_name: display_name for room_name, display_name in result_set}
    return mapping

def read_messages(n=10, self_number='Me', human_readable_date=True):
    global cursor
    query = """
    SELECT message.ROWID, message.date, message.text, message.attributedBody, handle.id, message.is_from_me, message.cache_roomnames
    FROM message
    LEFT JOIN handle ON message.handle_id = handle.ROWID
    """

    if n is not None:
        query += f" ORDER BY message.date DESC LIMIT {n}"

    results = cursor.execute(query).fetchall()
    messages = []

    for result in results:
        rowid, date, text, attributed_body, handle_id, is_from_me, cache_roomname = result

        if handle_id is None:
            phone_number = self_number
        else:
            phone_number = handle_id

        if text is not None:
            body = text
        elif attributed_body is None:
            continue
        else:
            attributed_body = attributed_body.decode('utf-8', errors='replace')

            if "NSNumber" in str(attributed_body):
                attributed_body = str(attributed_body).split("NSNumber")[0]
                if "NSString" in attributed_body:
                    attributed_body = str(attributed_body).split("NSString")[1]
                    if "NSDictionary" in attributed_body:
                        attributed_body = str(attributed_body).split("NSDictionary")[0]
                        attributed_body = attributed_body[6:-12]
                        body = attributed_body

        if human_readable_date:
            date_string = '2001-01-01'
            mod_date = datetime.datetime.strptime(date_string, '%Y-%m-%d')
            unix_timestamp = int(mod_date.timestamp())*1000000000
            new_date = int((date+unix_timestamp)/1000000000)
            date = datetime.datetime.fromtimestamp(new_date).strftime("%Y-%m-%d %H:%M:%S")

        mapping = get_chat_mapping()

        try:
            mapped_name = mapping[cache_roomname]
        except:
            mapped_name = None

        messages.append(
            {"rowid": rowid, "date": date, "body": body, "phone_number": phone_number, "is_from_me": is_from_me,
             "cache_roomname": cache_roomname, 'group_chat_name' : mapped_name})

    return messages


def read_unreply_messages():
    global cursor
    query = """
    SELECT message.ROWID,guid,reply_to_guid,text,is_from_me,handle.id AS phone_number
    FROM message
    LEFT JOIN handle ON message.handle_id = handle.ROWID
    WHERE guid NOT IN (
    SELECT reply_to_guid
    FROM message
    WHERE reply_to_guid IS NOT NULL 
    ) AND is_from_me=0;
    """
    results = cursor.execute(query).fetchall()
    # get query field name 
    field_names = [i[0] for i in cursor.description]

    messages = []
    for result in results:
        result_dict = {}
        for i in range(len(result)):
            result_dict[field_names[i]] = result[i]
        messages.append(result_dict)
    return messages


def send_message(phone_number, message, group_chat = False):
    # creating a file - note: text files end up being sent as normal text messages, so this is handy for
    # sending messages that osascript doesn't like due to strange formatting or characters
    # file_path = os.path.abspath('imessage_tmp.txt')

    # with open(file_path, 'w') as f:
    #     f.write(message)

    if not group_chat:
        command = f'tell application "Messages" to send "{message}" to buddy "{phone_number}"'
    else:
        command = f'tell application "Messages" to send "{message}" to chat "{phone_number}"'

    subprocess.run(['osascript', '-e', command])

    # print(f"Sent message to {phone_number}:\n{message}")



