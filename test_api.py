import requests
import json 
# Define the base URL for the API
base_url = "http://127.0.0.1:8081"

# Define a function to request chat completions
def request_chat_completion(prompt, system_message="", stream=False, temperature=1.0):
    endpoint = "/chat/completions"
    url = base_url + endpoint
    headers = {"Content-Type": "application/json"}
    data = {
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        "stream": stream,
        "temperature": temperature
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.text)
        return None

# Example usage
if __name__ == "__main__":
    system_message = "You are captain James T. Kirk from the Star Trek "
    prompt = "What is your mission? "
    completion = request_chat_completion(prompt, system_message)
    if completion:
        response_data = completion['choices'][0]['message']['content'].split('* `response`: ')[-1].split('</s>')[0]
        print(response_data)

