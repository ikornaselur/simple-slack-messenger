from typing import List, TypedDict


class Text(TypedDict):
    type: str
    text: str


class Block(TypedDict):
    type: str
    text: Text


class PayloadBase(TypedDict):
    channel: str


class Payload(PayloadBase, total=False):
    blocks: List[Block]
    text: str
    ts: str
