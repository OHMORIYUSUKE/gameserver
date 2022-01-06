import json
import uuid
from enum import Enum, IntEnum
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import NoResultFound
from sqlalchemy.sql.expression import true

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
    value: int

    class Config:
        orm_mode = True


class WaitRoomStatus(BaseModel):
    value: int

    class Config:
        orm_mode = True


########################################################################3


class RoomInfo(BaseModel):
    room_id: int
    live_id: int
    joined_user_count: int
    max_user_count: int
    is_active: bool

    class Config:
        orm_mode = True


class RoomUser(BaseModel):
    room_id: int
    user_id: int
    name: str
    leader_card_id: int
    select_difficulty: int
    is_me: bool
    is_host: bool

    class Config:
        orm_mode = True


class ResultUser(BaseModel):
    room_id: int
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


def room_create(live_id: int, select_difficulty: int, user_id: int) -> int:
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "INSERT INTO `room_info` (live_id, max_user_count,joined_user_count, is_active) VALUES (:live_id, :max_user_count,:joined_user_count,:is_active)"
            ),
            {
                "live_id": live_id,
                "max_user_count": 4,
                "joined_user_count": 1,
                "is_active": True,
            },
        )
        room_id = result.lastrowid
        # uidからカード取得
        result = conn.execute(
            text("SELECT * FROM `user` WHERE `id`=:user_id"), dict(user_id=user_id)
        )
        row = result.one()
        user_name = row[1]
        leader_card_id = row[3]
        result_user_in_room = conn.execute(
            text(
                "INSERT INTO `user_in_room` (select_difficulty, room_id,user_id, is_host, is_me, leader_card_id, name) VALUES (:select_difficulty, :room_id, :user_id, :is_host, :is_me, :leader_card_id, :name)"
            ),
            {
                "select_difficulty": select_difficulty,
                "room_id": room_id,
                "user_id": user_id,
                "is_host": True,
                "is_me": True,
                "leader_card_id": leader_card_id,
                "name": user_name,
            },
        )
        # print(result)
        return int(room_id)


def room_list(live_id: int) -> list[RoomInfo]:
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "SELECT * FROM `room_info` WHERE `live_id`=:live_id AND is_active=True"
            ),
            dict(live_id=live_id),
        )
        room_infos = []
        try:
            rows = result.all()
            for row in rows:
                room_infos.append(RoomInfo.from_orm(row))
        except NoResultFound:
            return None
        return {"room_info_list": room_infos}


def room_join(room_id: int, select_difficulty: int, user_id: int) -> JoinRoomResult:
    with engine.begin() as conn:
        # Roomに人が4人以上いたらDBに変更を加える(is_active=False)
        result = conn.execute(
            text("SELECT * FROM `user_in_room` WHERE `room_id`=:room_id"),
            dict(room_id=room_id),
        )
        rows = result.all()
        print(rows)
        count = 0
        for row in rows:
            print(row)
            count += 1
        if count >= 4:
            # Roomに人が4人以上いたらDBに変更を加える(is_active=False)
            result = conn.execute(
                text(
                    "UPDATE `room_info` SET is_active = :is_active WHERE `room_id`=:room_id"
                ),
                dict(is_active=False, room_id=room_id),
            )
            return {"value": 2}
        # 人数更新
        result = conn.execute(
            text(
                "UPDATE `room_info` SET joined_user_count = joined_user_count + 1 WHERE `room_id`=:room_id"
            ),
            dict(room_id=room_id),
        )
        # 人追加
        result = conn.execute(
            text("SELECT * FROM `user` WHERE `id`=:user_id"), dict(user_id=user_id)
        )
        row = result.one()
        name = row[1]
        leader_card_id = row[3]
        #
        result = conn.execute(
            text(
                "INSERT INTO `user_in_room` (room_id,user_id,name,leader_card_id,select_difficulty,is_me,is_host) VALUES (:room_id,:user_id,:name,:leader_card_id,:select_difficulty,:is_me,:is_host)"
            ),
            dict(
                room_id=room_id,
                user_id=user_id,
                name=name,
                leader_card_id=leader_card_id,
                select_difficulty=select_difficulty,
                is_me=True,
                is_host=False,
            ),
        )
        # print(result)
        return {"value": 1}


def room_wait_status(room_id: int) -> int:
    with engine.begin() as conn:
        result_ok = conn.execute(
            text(
                "SELECT * FROM `room_info` WHERE `room_id`=:room_id AND `is_active`=:is_active"
            ),
            dict(room_id=room_id, is_active=True),
        )
        if result_ok.first():
            return 1
        else:
            return 2


def room_wait_list(room_id: int) -> list[RoomUser]:
    with engine.begin() as conn:
        result = conn.execute(
            text("SELECT * FROM `user_in_room` WHERE `room_id`=:room_id"),
            dict(room_id=room_id),
        )
        try:
            rows = result.all()
            room_users = []
            for row in rows:
                room_users.append(RoomUser.from_orm(row))
            return room_users
        except NoResultFound:
            return None


def room_start(room_id: int) -> None:
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "UPDATE `room_info` SET `is_active`=:is_active WHERE `room_id`=:room_id"
            ),
            dict(is_active=False, room_id=room_id),
        )
    return None


def room_end(
    room_id: int, judge_count_list: list[int], score: int, user_id: int
) -> None:
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "INSERT INTO `user_result` (room_id, user_id, judge_count_list, score) VALUES (:room_id, :user_id, :judge_count_list, :score)"
            ),
            {
                "room_id": room_id,
                "user_id": user_id,
                "judge_count_list": json.dumps(judge_count_list),
                "score": score,
            },
        )
        return None


def room_result(room_id: int, user_id: int) -> list[ResultUser]:
    with engine.begin() as conn:
        result = conn.execute(
            text("SELECT * FROM `user_result` WHERE `room_id`=:room_id"),
            {"room_id": room_id},
        )
        rows = result.all()
        room_users_result = []
        room_users_result_ini = []
        # バグ
        i = 0
        for row in rows:
            print(row)
            print(i)
            if i == 2:
                room_users_result_ini.append(row[2])
                continue
            room_users_result_ini.append(row)
            i += 1

        for row in room_users_result_ini:
            print(row)
            room_users_result.append(ResultUser.from_orm(row))
    return room_users_result
