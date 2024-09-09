import os
import google.generativeai as genai
import pandas as pd
import streamlit as st
from prompt import PROMPT_INSURVERSE,PROMPT_INSURVERSE_2
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from datetime import datetime,timedelta,timezone

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint as pp


creds_dict = {
  "type": "service_account",
  "project_id": "swift-drive-434602-b7",
  "private_key_id": "94d052ad1cb890cee0af44cbd85d7d20d523aebb",
  "private_key": st.secrets["private_key"],
  "client_email": "pythonsheets@swift-drive-434602-b7.iam.gserviceaccount.com",
  "client_id": "115023323336387356135",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/pythonsheets%40swift-drive-434602-b7.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
#creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json",scope)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict,scope)


client = gspread.authorize(creds)
sheet = client.open("log_insurverse").sheet1   
sheet_2 = client.open("log_insurverse").worksheet('Sheet2')


def Message_date():
    # Get current UTC time
    now_utc = datetime.now(timezone.utc) 
    # Add 7 hours to convert to UTC+7
    now_utc_plus_7 = now_utc + timedelta(hours=7)
    # Print the current time in UTC+7
    return now_utc_plus_7.strftime(("%d/%m/%y %H:%M:%S"))

genai.configure(api_key= st.secrets["api_key"])
generation_config = {
    "temperature": 0.1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
    }

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    safety_settings=SAFETY_SETTINGS,
    generation_config=generation_config,
    system_instruction=PROMPT_INSURVERSE_2
    ,)


def clear_history():
    
    st.session_state["messages"] = [
        {"role": "model", "content": "อินชัวร์เวิร์ส สวัสดีค่ะ คุณลูกค้า สอบถามข้อมูลประกันเรื่องใดคะ"}
    ]
    st.rerun()


with st.sidebar:
    if st.button("Clear History"):
        clear_history()

st.title("💬 Insurverse  สวัสดีค่ะ")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "model",
            "content": "อินชัวร์เวิร์ส สวัสดีค่ะ คุณลูกค้า สอบถามข้อมูลประกันเรื่องใดคะ",
        }
    ]

file_path = "insurverse_p1 (5).xlsx"
try:
    df = pd.read_excel(file_path)
    file_content = df.to_string(index=False)
except Exception as e:
    st.error(f"Error reading file: {e}")
    st.stop()



for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    def typewriter(text,delay=0.02):
        container = st.empty()
        displayed_text = ""
        for char in text:
            displayed_text += char
            container.markdown(displayed_text)
            time.sleep(delay)
  
    def generate_response():
        history = [
            {"role": msg["role"], "parts": [{"text": msg["content"]}]}
            for msg in st.session_state["messages"]
        ]
        if prompt.lower().startswith("add") or prompt.lower().endswith("add"):
            sheet_2.append_row([len(sheet_2.get_all_values()),str(prompt),"user",Message_date()])
            st.chat_message("model").write("ขอบคุณสำหรับคำแนะนำค่ะ 😊")
            st.session_state["messages"].append({"role": "model", "content": "ขอบคุณสำหรับคำแนะนำค่ะ 😊"})
        else:
            history.insert(1, {"role": "user", "parts": [{"text": file_content}]})
            sheet.append_row([len(sheet.get_all_values()),str(prompt),"user",Message_date()])
        
            chat_session = model.start_chat(history=history)
            response = chat_session.send_message(prompt)
            sheet.append_row([len(sheet.get_all_values()),str(response.text),"AI",Message_date()])
            st.session_state["messages"].append({"role": "model", "content": response.text})
            st.chat_message("model")
            typewriter(response.text)
          

    generate_response()

#print("total_tokens: ", model.count_tokens(PROMPT_INSURVERSE))
#response = model.generate_content(file_content)
#print(response.usage_metadata)




