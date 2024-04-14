from pydantic import BaseModel
from datetime import time
from typing import Dict, List
from fastapi import Form


class PollForm(BaseModel):
    title: str
    description: str = "Decentralized Voting"
    age: int = 18
    name: Dict[str, int]
    end_date: str
    end_time: str
    username: str = "Admin"
    poll_id: str = "Admin"
    
    @classmethod
    def form(
        cls,
        title: str = Form(...),
        description: str = Form(...),
        age: int = Form(...),
        name: List[str] = Form(...),
        end_date: str = Form(...),
        end_time: str = Form(...)
    ):
        
        name_dict = {name: 0 for name in name}
        
        return cls(
            title=title,
            description=description,
            age=age,
            name=name_dict,
            end_date=end_date,
            end_time=end_time
        )