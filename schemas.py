from pydantic import BaseModel,Field
class expense(BaseModel):
    title: str = Field(min_length=1)
    amount:float = Field(gt=0)
    category: str = Field(min_length=1)