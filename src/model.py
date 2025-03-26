from pydantic import BaseModel, Field
from typing import List
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON

class IRSignal(BaseModel):
    """
    赤外線信号を表すモデル。

    Attributes:
        freq (int): IRサブキャリアの周波数 (kHz単位)。30kHzから80kHzの範囲で、デフォルトは38kHzです。
        data (List[int]): IR信号のオン・オフの時間間隔のリスト (マイクロ秒単位)。赤外線を受信する際、Remoはオンからオフ、オフからオンへの時間間隔を計測し、そのシーケンスを記録します。赤外線を送信する際、Remoはこの時間間隔シーケンスに従ってサブキャリア周波数をオン・オフします。
        format (str): `data`配列内の値のフォーマットと単位。`us`に固定されており、各整数値はマイクロ秒を表します。
    """

    freq: int = Field(ge=30, le=80, default=38,)
    data: List[int] = Field(
        ...,
    )
    format: str = Field(
        default="us",
    )

# SQLModel モデルの定義
class IRSignalTable(SQLModel, table=True):
    name: str = Field(default=None, primary_key=True)
    freq: int
    data: List[int] = Field(sa_column=Column(JSON))
    format: str = Field(default="us")
    @classmethod
    def new(cls, name: str, ir_signal: IRSignal):
        return cls(
            name=name,
            freq=ir_signal.freq,
            data=ir_signal.data,
            format=ir_signal.format,
        )    
    
    def update(self, ir_signal : IRSignal):
        self.freq = ir_signal.freq
        self.data = ir_signal.data
        self.format = ir_signal.format

        
    def convert_ir_signal(self) -> IRSignal:
        return IRSignal(freq=self.freq, data=self.data, format=self.format)
    
