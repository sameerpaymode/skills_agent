from agent_framework import Skill
from datetime import datetime

time_skill = Skill(
    name="time-skill",
    description="get current time and date",
    content="Use the get_current_datetime script to get the current time and date.",
)


import json

@time_skill.script(name="get_current_datetime", description="get the current time and date")
def get_current_datetime() -> str:
    """Return the current date and time."""
    
    now = datetime.now()

    return json.dumps({
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S")
    })