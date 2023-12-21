import os 
from retry import retry
import openai
openai.api_key = 'sk-YOUR-OPENAI-API-KEY'

# openai.api_key = os.getenv("OPENAI_API_KEY")
@retry(delay=1, backoff=2, tries=3)
def ask_chatgpt(question):
    print(f'q:{question}')
    try:
        completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        # model="gpt-3.5-turbo-0301",
        # model="gpt-4",
        messages=[{"role": "user", "content":question }]
        )
        answer = completion.choices[0].message["content"]
        print(f'a:\n{answer}')
        return f'{answer}'
    except Exception as e:
        print(e)
        raise e

 