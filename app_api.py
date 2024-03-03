# SPDX-FileCopyrightText: Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
import os 
from flask import Flask, jsonify, request
from trt_llama_apiv2 import TrtLlmAPI
from utils_api  import messages_to_prompt, completion_to_prompt, ChatMessage, MessageRole, DEFAULT_SYSTEM_PROMPT

local_app_data = os.getenv('LOCALAPPDATA')
DATABASE_PATH = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "sshcommander.db")
# Define file paths
CHAT_LOGS = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "chat_logs.jsonl")

# Hardcoded paths
trt_engine_path = "./model/mistral/mistral7b_int4_engine/"
trt_engine_name = "llama_float16_tp1_rank0.engine"
tokenizer_dir_path = "./model/mistral/mistral7b_hf/"
verbose = False
host = '127.0.0.1'
port = 8081
no_system_prompt = True 

# create trt_llm engine object
llm = TrtLlmAPI(
    model_path=trt_engine_path,
    engine_name=trt_engine_name,
    tokenizer_dir=tokenizer_dir_path,
    temperature=0.1,
    max_new_tokens=2048,
    context_window=2048,
    messages_to_prompt=messages_to_prompt,
    completion_to_prompt=completion_to_prompt,
    verbose=False
)

app = Flask(__name__)

@app.route('/models/Llama2', methods=['POST', 'GET'])
@app.route('/v1/models/Llama2', methods=['POST', 'GET'])
def models():
    resData = {
        "id": "Llama2",
        "object": "model",
        "created": 1675232119,
        "owned_by": "Meta"
    }
    return jsonify(resData)

@app.route('/models', methods=['POST', 'GET'])
@app.route('/v1/models', methods=['POST', 'GET'])
def modelsLlaMA():
    resData = {
        "object": "list",
        "data": [
            {
                "id": "Llama2",
                "object": "model",
                "created": 1675232119,
                "owned_by": "Meta"
            },
        ],
    }
    return jsonify(resData)

# Routes for chat completions
@app.route('/chat/completions', methods=['POST'])
@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    assert request.headers.get('Content-Type') == 'application/json'
    body = request.get_json()
    stream = False
    temperature = 1.0
    if "stream" in body:
        stream = body["stream"]
    if "temperature" in body:
        temperature = body["temperature"]
    formatted = False
    if verbose:
        print("/chat/completions called with stream=" + str(stream))

    prompt = ""
    if "messages" in body:
        messages = []
        for item in body["messages"]:
            chat = ChatMessage()
            if "role" in item:
                if item["role"] == 'system':
                    chat.role = MessageRole.SYSTEM
                elif item["role"] == 'user':
                    chat.role = MessageRole.USER
                elif item["role"] == 'assistant':
                    chat.role = MessageRole.ASSISTANT
                elif item["role"] == 'function':
                    chat.role = MessageRole.FUNCTION
                else:
                    print("Missing handling role in message:" + item["role"])
            else:
                print("Missing role in message")

            chat.content = item["content"]
            messages.append(chat)

        system_prompt = ""
        if not no_system_prompt:
            system_prompt = DEFAULT_SYSTEM_PROMPT

        prompt = messages_to_prompt(messages, system_prompt)

        formatted = True
    elif "prompt" in body:
        prompt = body["prompt"]

    if verbose:
        print("INPUT SIZE: " + str(len(prompt)))
        print("INPUT: " + prompt)

    if not stream:
        return llm.complete_common(prompt, True, temperature=temperature, formatted=formatted)
    else:
        return llm.stream_complete_common(prompt, True, temperature=temperature, formatted=formatted)

# Routes for completions
@app.route('/completions', methods=['POST'])
@app.route('/v1/completions', methods=['POST'])
def completion():
    assert request.headers.get('Content-Type') == 'application/json'
    stream = False
    temperature = 1.0
    body = request.get_json()
    if "stream" in body:
        stream = body["stream"]
    if "temperature" in body:
        temperature = body["temperature"]

    stop_strings = []
    if "stop" in body:
        stop_strings = body["stop"]

    if verbose:
        print("/completions called with stream=" + str(stream))

    prompt = ""
    if "prompt" in body:
        prompt = body["prompt"]

    if stream:
        f = open("prompts.txt", "a")
        f.write("\n---------\n")
        f.write("Completion Input stream:" + prompt)
        f.close()

    if not no_system_prompt:
        prompt = completion_to_prompt(prompt)

    formatted = True

    if not stream:
        return llm.complete_common(prompt, False, temperature=temperature, formatted=formatted, stop_strings=stop_strings)
    else:
        return llm.stream_complete_common(prompt, False, temperature=temperature, formatted=formatted, stop_strings=stop_strings)

if __name__ == '__main__':
    app.run(host, port=port, debug=True, use_reloader=False, threaded=False)
