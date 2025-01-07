from pydantic import BaseModel

class WorkatoAssistantBuilderRequest(BaseModel):
    name: str
    description: str
    instructions: str
    
class WorkatoAssistantBuilderResponse(BaseModel):
    success: bool
    message: str