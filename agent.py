import os
from pathlib import Path
from agent_framework import SkillsProvider
from agent_framework.openai import OpenAIChatCompletionClient
from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime


from pathlib import Path
from agent_framework import Skill, SkillScript, SkillsProvider

def my_runner(skill: Skill, script: SkillScript, args: dict | None = None) -> str:
    """Run a file-based script as a subprocess."""
    import subprocess, sys
    cmd = [sys.executable, str(Path(skill.path) / script.path)]
    if args:
        for key, value in args.items():
            if value is not None:
                cmd.extend([f"--{key}", str(value)])
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.stdout.strip()

# Code-defined scripts
from Skills_code.timeskill import time_skill
from Skills_code.docskill import document_skill
from Skills_code.enquiry_skill import enquiry_skill

skills_provider = SkillsProvider(
    skill_paths=Path(__file__).parent / "all-skills",
    script_runner=my_runner,
    skills=[time_skill, document_skill, enquiry_skill],
)

    
agent = OpenAIChatCompletionClient(
    model=os.environ["MODEL"], 
    api_key=os.environ["GROQ_API_KEY"],
    base_url= os.environ["BASE_URL"],
    
).as_agent(
    name="SkillsAgent",
    instructions="""You are a helpful assistant. use skills when appropriate to answer the user's question.
          Skills are tools that you can use to get information or perform actions. 
          You should use skills when you need to get information that you don't have or when you need to perform an action on behalf of the user. 
          When you use a skill, you should call it with the appropriate arguments and wait for the result before responding to the user.""",
    context_providers=[skills_provider],
)

