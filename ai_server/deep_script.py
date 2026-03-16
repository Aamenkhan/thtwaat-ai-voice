from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")

with open("facts.txt","r",encoding="utf-8") as f:
    facts = f.read()

prompt = f"""
Using these historical facts:

{facts}

Write a cinematic Hindi documentary script.
Narration style like Netflix history documentaries.
"""

response = client.chat.completions.create(
model="gpt-4.1-mini",
messages=[{"role":"user","content":prompt}]
)

script = response.choices[0].message.content

with open("script.txt","w",encoding="utf-8") as f:
    f.write(script)

print("Deep script ready")