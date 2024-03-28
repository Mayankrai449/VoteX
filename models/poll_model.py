from pydantic import BaseModel
from datetime import time
from typing import List
from fastapi import Form

class PollForm(BaseModel):
    title: str
    description: str
    age: int
    name: List[str]
    end_date: str
    end_time: str
    
    @classmethod
    def form(cls,
                title: str = Form(...),
                description: str = Form(...),
                age: int = Form(...),
                name: List[str] = Form(...),
                end_date: str = Form(...),
                end_time: str = Form(...)
    ):
        return cls(
            title=title,
            description=description,
            age=age,
            name=name,
            end_date=end_date,
            end_time=end_time
        )