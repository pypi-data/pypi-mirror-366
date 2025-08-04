from typing import Dict, Any

class PromptTemplate:
    """Base class for prompt templates"""
    
    def __init__(self, template: str):
        self.template = template
        
    def format(self, **kwargs: Dict[str, Any]) -> str:
        """Format the template with given variables"""
        return self.template.format(**kwargs)

# Common prompt templates
SYSTEM_PROMPT = PromptTemplate(
    "You are a helpful AI assistant. Answer the user's questions accurately and concisely."
)

QA_PROMPT = PromptTemplate(
    "Context: {context}\n\nQuestion: {question}\n\nAnswer:"
)