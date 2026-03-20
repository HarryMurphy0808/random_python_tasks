import os
import wikipedia
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

page_title = input("Enter a Wikipedia page to summarize: ")

def get_text(resp):
    if getattr(resp, "text", None):
        return resp.text
    try:
        return resp.candidates[0].content.parts[0].text
    except Exception:
        return ""

try:
    page = wikipedia.page(page_title, auto_suggest=False)
    content = page.content[:2000]
    prompt = (
        "Summarize the text below in EXACTLY 5 bullet points.\n"
        "Rules:\n"
        "- Start each line with '- '\n"
        "- No intro sentence\n"
        "- If you don't know something, still summarize what's there\n\n"
        "TEXT:\n"
        f"{content}\n\n"
        "BULLETS:\n"
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    output = get_text(response).strip()
    
    if len(output) < 40 or "-" not in output:
        content = page.content[:1000]
        prompt = prompt.replace(page.content[:2000], content)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        output = get_text(response).strip()

    print(output)

except KeyError:
    print("No API key found.")

except wikipedia.exceptions.PageError:
    print("Page not found.")

except Exception as e:
    print("Something went wrong:")
    print(e)
    
finally:
    os.system("pause")
    
