import gradio as gr
import pandas as pd

from chatgpt_retrieval_plugin_api import ChatGPTRetrievalPluginApi
chat_cli = ChatGPTRetrievalPluginApi()

# app1
def upload_file(file):
    
    status, doc_dict = chat_cli.upsert_file(file)
    
    if status:
        if doc_dict:
            doc_id = list(doc_dict.keys())[0]
            file_name = list(doc_dict.values())[0]
            output = f'Success\nFile Name: {file_name}\nDocument Id: {doc_id}'
        else:
            output = 'Fail'
    else:
        output = 'Fail'
    
    return output

app1 = gr.Interface(
    fn=upload_file,
    inputs=gr.File(file_types=['.pdf']),
    outputs=gr.Textbox(label='Upload Result')
)

# app2
with gr.Blocks() as app2:
    chatbot = gr.Chatbot(label='客服機器人')
    msg = gr.Textbox(label="輸入詢問內容")
    clear = gr.Button("清除聊天記錄")

    def user(user_message, history):
        return "", history + [[user_message, None]]

    def bot(history):
        user_query = history[-1][0]
        related_content = chat_cli.query(user_query)
        gpt_answer = chat_cli.answer(user_query, related_content)
        
        bot_message = gpt_answer
        history[-1][1] = bot_message
        
        return history

    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    clear.click(lambda: None, None, chatbot, queue=False)   
    
# app3
def list_db_file():

    doc_list_map = chat_cli.query_list()
    output = pd.DataFrame({
        'id': list(doc_list_map.values()),
        'document': list(doc_list_map.keys()),
    })
        
    return output

def delete_db_file(id):
    
    response = chat_cli.delete(ids=[id])
    if response.status_code == 200:
        output = 'Success'
    else:
        output = 'Fail'
        
    return output

with gr.Blocks() as app3:
    with gr.Row():
        with gr.Column():
            list_doc_output = gr.Dataframe(
                headers=["id", "document"],
                datatype=["str", "str"],
            )
            list_doc_btn = gr.Button(value='List Documents')
        with gr.Column():
            delete_doc_id_input = gr.Textbox(label='Delete Document Id')
            delete_doc_btn = gr.Button(value='Delete Document')
            delete_doc_output = gr.Textbox(label='Delete Result')
            
    list_doc_btn.click(list_db_file, None, list_doc_output)
    delete_doc_btn.click(delete_db_file, delete_doc_id_input, delete_doc_output)

demo = gr.TabbedInterface([app1, app2, app3], ["Upload", "Chatbot", "File System"])

if __name__ == '__main__':
    demo.launch()
