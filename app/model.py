import json
import uuid
from enum import Enum, IntEnum
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import NoResultFound

from .db import engine


class InvalidToken(Exception):
    """指定されたtokenが不正だったときに投げる"""


class SafeUser(BaseModel):
    """token を含まないUser"""

    id: int
    name: str
    leader_card_id: int

    class Config:
        orm_mode = True


class LiveDifficulty(BaseModel):
    name: str
    value: int

    class Config:
        orm_mode = True


class JoinRoomResult(BaseModel):
    name: str
    value: int

    class Config:
        orm_mode = True


class WaitRoomStatus(BaseModel):
    name: str
    value: int

    class Config:
        orm_mode = True


########################################################################3


class RoomInfo(BaseModel):
    room_id: int
    live_id: int
    joined_user_count: int
    max_user_count: int

    class Config:
        orm_mode = True


class RoomUser(BaseModel):
    user_id: int
    name: str
    leader_card_id: int
    select_difficulty: LiveDifficulty
    is_me: bool
    is_host: bool

    class Config:
        orm_mode = True


class ResultUser(BaseModel):
    user_id: int
    judge_count_list: list[int]
    score: int

    class Config:
        orm_mode = True


def create_user(name: str, leader_card_id: int) -> str:
    """Create new user and returns their token"""
    token = str(uuid.uuid4())
    # NOTE: tokenが衝突したらリトライする必要がある.
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "INSERT INTO `user` (name, token, leader_card_id) VALUES (:name, :token, :leader_card_id)"
            ),
            {"name": name, "token": token, "leader_card_id": leader_card_id},
        )
        # print(result)
    return token


def _get_user_by_token(conn, token: str) -> Optional[SafeUser]:
    # TODO: 実装
    result = conn.execute(
        text("SELECT `id`, `name`, `leader_card_id` FROM `user` WHERE `token`=:token"),
        dict(token=token),
    )
    try:
        row = result.one()
    except NoResultFound:
        return None
    return SafeUser.from_orm(row)


def get_user_by_token(token: str) -> Optional[SafeUser]:
    with engine.begin() as conn:
        return _get_user_by_token(conn, token)


def _update_user(conn, token: str, name: str, leader_card_id: int) -> None:
    # TODO: 実装
    result = conn.execute(
        text(
            "UPDATE `user` SET name = :name , leader_card_id = :leader_card_id WHERE token = :token"
        ),
        dict(token=token, name=name, leader_card_id=leader_card_id),
    )
    return token
    # pass


def update_user(token: str, name: str, leader_card_id: int) -> None:
    # このコードを実装してもらう
    with engine.begin() as conn:
        # TODO: 実装
        return _update_user(conn, token, name, leader_card_id)
        # pass

# Room

# エラー箇所
"""
- room_id = result.lastrowidでエラーになります。
- INSERT INTO...はできています。
"""
def room_create(live_id: int) -> int:
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "INSERT INTO `room_info` (live_id, max_user_count) VALUES (:live_id, :max_user_count)"
            ),
            {"live_id": live_id, "max_user_count": 4},
        )
        # print(result)
    room_id = result.lastrowid
    return int(room_id)


def room_list(live_id: int) -> list[RoomInfo]:
    with engine.begin() as conn:
        result = conn.execute(
            text("SELECT * FROM `room_info` WHERE `live_id`=:live_id"),
            dict(live_id=live_id),
        )
        try:
            rows = result.all()
            print(rows)
        except NoResultFound:
            return None
        return list[RoomInfo(rows)]
