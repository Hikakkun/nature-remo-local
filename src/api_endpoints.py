from model import IRSignal, IRSignalTable
from sqlmodel import Session
from sqlalchemy.engine.base import Engine
from fastapi import FastAPI, HTTPException, status
from nature_locak_api_client import NatureLocalAPIClient
import requests


def create_or_update_ir_signal(engine: Engine, name: str, ir_signal: IRSignal):
    with Session(engine) as session:
        ir_signal_table = session.get(IRSignalTable, name)
        if ir_signal_table:
            # 更新
            ir_signal_table.update(ir_signal)
            session.add(ir_signal_table)
            session.commit()
            session.refresh(ir_signal_table)
            return {"message": f"IR signal '{name}' updated successfully."}
        else:
            # 新規作成
            new_ir_signal_table = IRSignalTable.new(name, ir_signal)
            session.add(new_ir_signal_table)
            session.commit()
            session.refresh(new_ir_signal_table)
            return {"message": f"IR signal '{name}' created successfully."}


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


def include_routes(app: FastAPI, engine: Engine, client: NatureLocalAPIClient):
    @app.get("/nature.remo.local/{name}", response_model=IRSignal)
    async def get_ir_signal_endpoint(name: str):
        return get_ir_signal(engine, name)

    @app.post("/nature.remo.local/{name}", status_code=status.HTTP_204_NO_CONTENT)
    async def send_ir_signal_endpoint(name: str):
        send_ir_signal(engine, name, client)

    @app.put("/nature.remo.local/{name}", status_code=status.HTTP_201_CREATED)
    async def create_or_update_ir_signal_endpoint(name: str, ir_signal: IRSignal):
        return create_or_update_ir_signal(engine, name, ir_signal)

    @app.delete("/nature.remo.local/{name}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_ir_signal_endpoint(name: str):
        delete_ir_signal(engine, name)
