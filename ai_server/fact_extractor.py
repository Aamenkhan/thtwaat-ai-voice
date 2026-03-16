from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")

with open("research.txt","r",encoding="utf-8") as f:
    research = f.read()

prompt = f"""
Extract the most important historical facts from this text.

{research}

Return bullet points.
"""

response = client.chat.completions.create(
model="gpt-4.1-mini",
messages=[{"role":"user","content":prompt}]
)

facts = response.choices[0].message.content

with open("facts.txt","w",encoding="utf-8") as f:
    f.write(facts)

print("Facts ready")