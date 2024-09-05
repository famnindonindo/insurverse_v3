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
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCr/jY2QvbB/M0q\nIGHLhzyz2dIwVHTRk3NL7gamfwfbEycfuFvsRgrO/gHb8XsZXJaic/eJW9JkqvlV\n5p3XwGCu6FyehzbzMaxiZZu3/scqOA4scswgIvBFtQOE0JnwXe39L+kD85boUW6C\nB/dEIHl/spxoHQpgnIz6WbBbjU58IMZp2INlAt+NdTzKPdxhVExv27iJDk+TMSuS\nTmJAWd02y87JdFNWw1e9ak4BrMVpuGDat/hNLnOHhgYpQkfjQ3rrG4oTXMTEALRA\nENr44YWDemcbptCbrD3Yibr3iUF/iOPGjzFBU8cI2aoXCo9wgG65JyX6ipmoj3Dz\nawGYyhlZAgMBAAECggEAEpup3NwI23sQ7W5cdks255R4966jhusnjb7+bDQRMwQS\n9w0YsOrxD20O4W9ybI+GYqQeU3eiPy76U+9kA2w2aaYNIz+o0837gxfQLat8e9Zd\nvjRbXly5Vyla7JsvFIDtFzgAQ2Ou34qz5JCdEXtb+dNmtaLytPorDIj4micjJy2t\nE6uEMgNR6w26tpgoRVzyLL62ykMt/ZRI6korAnImolaVDQYev3eB7RPIv7yInnHH\np7cfNl04ylJn8bdZ2pzKqxO45lEO8Y3/SJ9bX1g1FJPC0Ozz4+0w2qG8KKg0Rfjb\nWjlEwCbKFIVw8ylHYR1fpjVpFDrMjHRC+9EJTX/HAwKBgQDhmc4sfqi0bSON5raV\ny+wM2HGmk0ognK5FEMT//e0OB9v2IQZ+nzF+KT2YUzWTbJS8fQIE93DdE8uvfFQG\na97dOxmGDZ7Hf9r1gc2d/6mtbHA5elpkpPg0X9I2xjV8SS1ooeOq2GHMbC50h+WL\ndRl/sCnfH/Mmg+VoaC7oQX82RwKBgQDDKy7meAiuyVHRZKSwFKZ0kXFqiysgcIRc\n4/R1m4Ho2qks7B57LKXbEvdxjSF88V9tgVYF6UjbFd3kXSD2UN02oa2j1pdLNkkP\nr32jO467jpskaqmYrwO6VilYBcWcXyICPnHCLx9IK+5mqGQ7u0DHlns3qrQEPRiI\nrSwi7OzjXwKBgQDc5SaVNqelkr+fb+oTnopQwZX2jn2klQWmJpdeOJnmhReBVjDv\nxpxFdcgT4FWzNjwkmxphFo9ySLHF8Cyt5O1hHT8OnUN8/9m7Tg+wxuazIlx4Sy87\nILTPQ4unikhQm65Upz8ux5Rq/vo1q+K8vDntZuZ4zOXeLoNvyaM0Uv1mfQKBgQCt\naVY/01GrtBdtnSYzifWox35ls4g7R55kRut0ABt6wabl0lr3COHJeN3B2Ct0L6eh\nzfSYRgLFH3XMLe9WzNzxaNC3Lbm6S165gC169zVIc1poDhnpH0CJtXsAyggee+zk\n34UGjAYYg2hNcLu20xeo/402FgfjaEG/V1dLJQcKswKBgGk6eGA6OJMaQwnQXvND\nS+fV+CRDH3rjXIKtmO1ak+65VXgVEJ2zY1AVoQQfsh0y1ZPv+4ciHG5NBQZR1PE4\nkC6Zfnj9bWbDFLBC8Gd+gHnG80m8T/VxUS/4OAWvtZsX8wS+5trc7LdzkwLfRD1z\nsJHMNZfBmC9BEehHVlSyE4h0\n-----END PRIVATE KEY-----\n",
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

genai.configure(api_key="AIzaSyDiji5U1OleJzLMM4mqYPh5w6vPga0VjmA")
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
    st.experimental_rerun()


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
            st.chat_message("model").write(response.text)

    generate_response()

#print("total_tokens: ", model.count_tokens(PROMPT_INSURVERSE))
#response = model.generate_content(file_content)
#print(response.usage_metadata)




