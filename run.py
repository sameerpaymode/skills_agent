import asyncio
from agent_framework import Message
import json
import sys
from agent import agent
async def chat():
    messages = [
    ]

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        messages.append(Message("user", [user_input]))

        print("Assistant: ", end="", flush=True)

        text_buffer = ""
        skill_buffer = ""

        async for update in agent.run(messages, stream=True):
            if update.contents:
                content = update.contents[0]

                if content.type == "function_call":
                    try:
                        skill_buffer += content.arguments
                        skill_name = json.loads(skill_buffer).get("skill_name", "Skill")
                        print(f"\n[Using Skill: {skill_name}...]\nAssistant: ", end="", flush=True)
                    except:
                        pass

                elif content.type == "function_result":
                    print("\n[Skill Completed]\nAssistant: ", end="", flush=True)

            if update.text:
                print(update.text, end="", flush=True)
                text_buffer += update.text

        print()
        messages.append(Message("assistant", [text_buffer]))

# 🔥 run it
asyncio.run(chat())