import os
import json
import requests
import redis
import openai
openai.api_key = os.environ.get('OPENAI_API_KEY')

class ChatGPTRetrievalPluginApi:
    def __init__(self) -> None:
        self.api = 'http://0.0.0.0:8000'
        self.headers = {
            "Authorization": "Bearer 123"
        }
        self.redis_cli = redis.Redis(host='localhost', port=6379, decode_responses=True)  
        
    def upsert_file(self, file_obj):
        
        file_name = os.path.basename(file_obj.name)
        
        files = {
            "file": (file_name, open(file_obj.name, 'rb'), 'application/pdf')
        }
        
        response = requests.post(
            url=os.path.join(self.api, 'upsert-file'),
            headers=self.headers,
            files=files
        )
        
        print(response.text)
        
        status = True if response.status_code == 200 else False
        if status:
            doc_id = json.loads(response.text)["ids"][0]
            if doc_id:
                doc_dict = {
                    doc_id: file_name
                }
                self.redis_cli.set(f'doclist:{doc_id}', file_name)
        else:
            doc_id = ''
            doc_dict = {}
        
        return status, doc_dict
    
    def query_list(self):
        
        doc_key_lists = self.redis_cli.keys(pattern='doclist*')
        doc_list_map = {}
        for key in doc_key_lists:
            file_name = self.redis_cli.get(key)
            doc_list_map[file_name] = key.replace('doclist:', '')
            
        return doc_list_map
    
    def query(self, query: str):

        body = {
            "queries": [
                {
                    "query": query,
                    "top_k": 1
                }
            ]
        }

        response = requests.post(
            url=os.path.join(self.api, 'query'),
            headers=self.headers,
            data=json.dumps(body)
        )
        print(f'Query Response: {response.text}')

        if response.status_code == 200:
            response = json.loads(response.text)
            doc_id = response['results'][0]['results'][0]['id']
            text = response['results'][0]['results'][0]['text']
            score = response['results'][0]['results'][0]['score']
        else:
            text = 'Fail'
        
        return text
    
    def delete(self, ids: list[str] = [], delete_all: bool = False):

        body = {
            "ids": ids,
            "delete_all": delete_all
        }
        
        response = requests.delete(
            url=os.path.join(self.api, 'delete'),
            headers=self.headers,
            data=json.dumps(body)
        )
        print(f'Delete Response: {response.text}')
        
        if response.status_code == 200:
            for x in ids:
                self.redis_cli.delete(f'doclist:{x}')
        
        return response
    
    def answer(self, question, query):
        
        system_msg = '''
        你是一個客服小幫手，主要以繁體中文回覆客戶訊息，回覆字數限制在200字以內。
        '''
        
        user_msg = f'''
        用戶問題: {question},
        資料庫最相關段落內容: {query}
        請依據提供的"資料庫最相關段落內容"針對用戶問題進行回覆
        '''

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            temperature=0,
        )

        response_answer = response['choices'][0]['message']['content']

        return response_answer   
        
if __name__ == '__main__':
    cli = ChatGPTRetrievalPluginApi()
    
    # cli.query('HPV跟癌症的關係')
    
    # s = cli.query_list()
    # print(s)
    
    # DELETE Redis
    # cli.delete(delete_all=True)
        
        
        