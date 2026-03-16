from openai import OpenAI

def main(api_key="YOUR_API_KEY"):
    client = OpenAI(api_key=api_key)

    with open("script.txt","r",encoding="utf-8") as f:
        script = f.read()

    prompt = f"""
Break this documentary script into scenes.
Each scene should describe a visual moment.

Script:

{script}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    scenes = response.choices[0].message.content

    with open("scenes.txt","w",encoding="utf-8") as f:
        f.write(scenes)

    print("Scenes ready")


if __name__ == "__main__":
    main()