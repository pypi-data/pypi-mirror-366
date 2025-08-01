import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.models.model  import Model

llm = Model(model_name="doubao-1-5-pro-32k-250115", model_provider="doubao", api_key="a7217dc9-1a7d-4dbc-8a3c-c7eed07a1335")

print(llm("hi"))

t = """
# system
You r a helpful math teacher
# user 
1+1=?
"""

t2 = """
# System
You r a helpful math teacher
# User 
1+1=?
"""

print(llm(t))
print(llm(t2))