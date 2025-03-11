import json
import uuid
import logging
import requests
from requests.auth import HTTPBasicAuth
from utils import get_file_id
import streamlit as st

logging.basicConfig(level=logging.INFO)

DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]


def get_access_token() -> str:
    # Для DeepSeek обычно используется прямой API ключ в заголовках
    return DEEPSEEK_API_KEY


def upload_file(file, access_token: str) -> str:
    url = "https://api.deepseek.com/v1/files"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    files = {'file': (file.name, file.getvalue(), file.type)}
    payload = {'purpose': 'assistants'}
    try:
        response = requests.post(url, headers=headers, data=payload, files=files)
        if response.status_code == 200:
            return response.json().get("id")
        else:
            raise Exception(f"File upload error: {response.text}")
    except Exception as e:
        logging.error(f"Error: {e}")
        raise


def send_prompt(messages: list, access_token: str, attachments: list = None):
    url = "https://api.deepseek.com/v1/chat/completions"
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.7
    }

    if attachments:
        payload["messages"][-1]["file_ids"] = attachments

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"API error: {response.text}")


def sent_prompt_and_get_response(msg: str, access_token: str, messages=None, attachments=None):
    if messages is None:
        messages = [{"role": "user", "content": msg}]

    res = send_prompt(messages, access_token, attachments)
    file_id, is_image = get_file_id(res)

    messages.append({"role": "assistant", "content": file_id, "is_image": is_image})
    return file_id, is_image


def get_image(file_id: str, access_token: str):
    url = f"https://api.deepseek.com/v1/files/{file_id}/content"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Error fetching image: {response.text}")