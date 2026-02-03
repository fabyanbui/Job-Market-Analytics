import streamlit as st
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4
# from io import BytesIO
# import base64
# import pandas as pd
# import google.generativeai as genai
# from langchain.schema import HumanMessage, AIMessage
from huggingface_hub import InferenceClient
from IPython.display import Markdown, display
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("HUGGINGFACE_API_KEY")
client = InferenceClient(api_key=api_key)

# Function to generate content from a user question
def generate_content(question):
    messages = [
        {
            "role": "user",
            "content": question
        }
    ]
    completion = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3.2", 
        messages=messages, 
        max_tokens=20000
    )
    return completion.choices[0].message.content

def tab_3():
    st.header("Q&A")

    # Conversation history storage
    base_prompt = f"Given a dataset below\n" + str(pd.read_csv("processed_data.csv")) + "\n\n"
    # response = generate_content(base_prompt)

    # if "chat_history" not in st.session_state:
    #     st.session_state["chat_history"] = [{"user": base_prompt, "bot": response}]
    
    # Display complete chat history first
    # chat = st.session_state["chat_history"]
    # for i in range(len(chat)):
    #     if i==0:
    #         continue
    #     st.markdown(f'''
    #         <div style="text-align: left; padding: 10px; background-color: #F1F1F1; border-radius: 15px; margin-bottom: 5px;">
    #             {chat[i]["user"]}
    #         </div>
    #     ''', unsafe_allow_html=True)
    #     st.markdown(f'''
    #         <div style="text-align: left; padding: 10px; background-color: #D1E8E2; border-radius: 15px; margin-bottom: 5px;">
    #             {chat[i]["bot"]}
    #         </div>
    #     ''', unsafe_allow_html=True)

    user_input = st.text_input("👤: Ask about data!", placeholder="Input new question here...")
    
    if user_input:
        # Generate response using custom function
        # response = generate_content("History of conversation:\n" + str(st.session_state["chat_history"]) + "\n\n" + user_input)
        response = generate_content(base_prompt + user_input + ".Please give the answer base in dataset instead of giving the way to find it.")
        # Store input and response in session state
        # st.session_state["chat_history"].append({"user": user_input, "bot": response})
        st.markdown(f'''
            <div style="text-align: left; padding: 10px; background-color: #D1E8E2; border-radius: 15px; margin-bottom: 5px;">
                {response}
            </div>
        ''', unsafe_allow_html=True)