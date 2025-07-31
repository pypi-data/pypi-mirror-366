import requests


# 生成文本补全
def generate(prompt, model="qwen3:8b"):
    url = "http://localhost:11434/api/generate"
    data = {"model": model, "prompt": prompt, "stream": False, "temperature": 0.7}
    response = requests.post(url, json=data)
    return response.json()["response"]


# 多轮对话
def chat(messages, model="qwen3:8b"):
    url = "http://localhost:11434/api/chat"
    data = {"model": model, "messages": messages}
    response = requests.post(url, json=data)
    return response.json()["message"]["content"]
