import os
from pathlib import Path
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine
from fastapi import FastAPI
from nature_locak_api_client import NatureLocalAPIClient
from contextlib import asynccontextmanager
from api_endpoints import include_routes
import argparse  # argparseモジュールを追加


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

    parser = argparse.ArgumentParser(description="FastAPI application with configurable port.")
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port number to run the application on (default: 8001)",
    )
    args = parser.parse_args()
    uvicorn.run(app, host="0.0.0.0", port=args.port)
