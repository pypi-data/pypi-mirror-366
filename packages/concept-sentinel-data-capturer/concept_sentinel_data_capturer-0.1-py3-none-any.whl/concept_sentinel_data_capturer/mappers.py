from pydantic import BaseModel, Field
from typing import Optional

class ContextRequest(BaseModel):
    inputPrompt: str = Field(example="Who are the co-founders of Infosys?")
    llmResponse: Optional[str] = Field(example="Infosys was co-founded by Narayana Murthy along with six other engineers: Nandan Nilekani, S. Gopalakrishnan (Kris), S. D. Shibulal, K. Dinesh, N. S. Raghavan, and Ashok Arora. Established in 1981, Infosys started with a modest capital of $250 and has since grown into one of the largest IT services companies in the world. Narayana Murthy, often regarded as the face of Infosys, played a pivotal role in shaping the company's culture and vision, while the combined efforts of all co-founders contributed to its remarkable growth and success in the global IT industry.")
    class config:
        from_attributes = True
from pydantic import BaseModel
from typing import Optional, List, Dict,Any



class env_variables(BaseModel):
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_VERSION: str
    AZURE_DEPLOYMENT_ENGINE: str
    DB_NAME: str
    COSMOS_PATH: str


    
class ContextResponse(BaseModel):
    prompt_context: str = Field(example= "biggest country in the world?")
    response_context: str = Field(example= "biggest country in the world is Russia")
    success_status: bool = Field(example=True)
    
    class Config:
        from_attributes = True
