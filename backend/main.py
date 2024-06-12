from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import auth_router, dashboard_router, polls_router


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(polls_router)

    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8004, host="127.0.0.1")