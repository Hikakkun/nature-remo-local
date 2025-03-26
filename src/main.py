import os
from pathlib import Path
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine
from fastapi import FastAPI
from nature_locak_api_client import NatureLocalAPIClient
from contextlib import asynccontextmanager
from api_endpoints import include_routes


db_file = Path("./ir_signals.db")
db_url = f"sqlite:///{db_file}"
engine = create_engine(db_url)
load_dotenv()
client = NatureLocalAPIClient(os.getenv("NATURE_IP"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("startup event")
    SQLModel.metadata.create_all(engine)
    yield
    print("shutdown event")


app = FastAPI(lifespan=lifespan)
include_routes(app, engine, client)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
