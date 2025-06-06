from model import IRSignal, IRSignalTable, IRSignalNames
from sqlmodel import Session, select
from sqlalchemy.engine.base import Engine
from fastapi import FastAPI, HTTPException, status
from nature_locak_api_client import NatureLocalAPIClient
import requests


def create_signal(engine: Engine, name: str, ir_signal: IRSignal):
    with Session(engine) as session:
        ir_signal_table = session.get(IRSignalTable, name)
        if ir_signal_table is None:
            new_ir_signal_table = IRSignalTable.new(name, ir_signal)
            session.add(new_ir_signal_table)
            session.commit()
            session.refresh(new_ir_signal_table)
            return {"message": f"IR signal '{name}' created successfully."}
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"IR signal with name '{name}' already exists.",
            )


def update_ir_signal(engine: Engine, name: str, ir_signal: IRSignal):
    with Session(engine) as session:
        ir_signal_table = session.get(IRSignalTable, name)
        if ir_signal_table:
            ir_signal_table.update(ir_signal)
            session.add(ir_signal_table)
            session.commit()
            session.refresh(ir_signal_table)
            return {"message": f"IR signal '{name}' updated successfully."}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"IR signal with name '{name}' not found.",
            )


def delete_ir_signal(engine: Engine, name: str):
    with Session(engine) as session:
        ir_signal_table = session.get(IRSignalTable, name)
        if ir_signal_table:
            session.delete(ir_signal_table)
            session.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"IR signal with name '{name}' not found.",
            )


def get_ir_signal(engine: Engine, name: str) -> IRSignal:
    with Session(engine) as session:
        ir_signal_table = session.get(IRSignalTable, name)
        if ir_signal_table:
            return ir_signal_table.convert_ir_signal()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"IR signal with name '{name}' not found.",
            )


def send_ir_signal(engine: Engine, name: str, client: NatureLocalAPIClient):
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Nature Remo IP address not configured.",
        )

    with Session(engine) as session:
        ir_signal_table = session.get(IRSignalTable, name)
        if ir_signal_table:
            try:
                client.send_ir_signal(ir_signal_table.convert_ir_signal())
            except requests.exceptions.RequestException as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error sending IR signal to Nature Remo: {e}",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"IR signal with name '{name}' not found.",
            )


def get_all_ir_signal_names(engine: Engine) -> IRSignalNames:
    with Session(engine) as session:
        ir_signal_names = session.exec(select(IRSignalTable.name)).all()
        return IRSignalNames(names=list(ir_signal_names))


def include_routes(app: FastAPI, engine: Engine, client: NatureLocalAPIClient):
    @app.get("/signals", response_model=IRSignalNames)
    async def get_all_ir_signal_names_endpoint():
        return get_all_ir_signal_names(engine)

    @app.get("/signals/{name}", response_model=IRSignal)
    async def get_ir_signal_endpoint(name: str):
        return get_ir_signal(engine, name)

    @app.post(
        "/signals/{name}/send", status_code=status.HTTP_204_NO_CONTENT
    )
    async def send_ir_signal_endpoint(name: str):
        send_ir_signal(engine, name, client)

    @app.put("/signals/{name}", status_code=status.HTTP_200_OK)
    async def update_ir_signal_endpoint(name: str, ir_signal: IRSignal):
        return update_ir_signal(engine, name, ir_signal)

    @app.post("/signals/{name}", status_code=status.HTTP_201_CREATED)
    async def create_signal_endpoint(name: str, ir_signal: IRSignal):
        return create_signal(engine, name, ir_signal)

    @app.delete(
        "/signals/{name}", status_code=status.HTTP_204_NO_CONTENT
    )
    async def delete_ir_signal_endpoint(name: str):
        delete_ir_signal(engine, name)
