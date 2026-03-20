import os
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

messages = []

def add_user_message(text):
    messages.append({
        "role": "user",
        "parts": [{"text": text}]
    })

def add_model_message(text):
    messages.append({
        "role": "model",
        "parts": [{"text": text}]
    })

try:
    # first prompt
    add_user_message("why is my website down?")

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=messages,
        config={
            "max_output_tokens": 100
        }
    )

    answer = response.text
    print(answer)

    add_model_message(answer)

except KeyError:
    print("API key not found.")

except Exception as e:
    print("Something went wrong:", e)
