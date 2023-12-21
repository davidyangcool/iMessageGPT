from time import sleep
from pprint import pprint
from imessage_tools import *
from chatgpt import ask_chatgpt

def schedule_all():
    while True:
        unreply_messages = read_unreply_messages()
        if unreply_messages:
            print(f'need to reply {len(unreply_messages)} messages !')
        for msg in unreply_messages:
            phone_number = msg["phone_number"]
            question = msg["text"]
            answer = ask_chatgpt(question)
            send_message(phone_number,answer)
        sleep(5)
    
    
if __name__=='__main__':
    schedule_all()
        

