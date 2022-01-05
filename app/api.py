from enum import Enum

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from starlette.requests import Request
from starlette.routing import request_response

from . import model
from .model import (
    JoinRoomResult,
    LiveDifficulty,
    ResultUser,
    RoomInfo,
    RoomUser,
    SafeUser,
    WaitRoomStatus,
)

app = FastAPI()

# Sample APIs


@app.get("/")
async def root():
    return {"message": "Hello World"}


# User APIs


class UserCreateRequest(BaseModel):
    user_name: str
    leader_card_id: int


class UserCreateResponse(BaseModel):
    user_token: str


# Room APIs


class RoomCreateRequest(BaseModel):
    select_difficulty: int
    live_id: int


class RoomCreateResponse(BaseModel):
    room_id: int


class RoomListRequest(BaseModel):
    live_id: int


class RoomListResponse(BaseModel):
    room_info_list: list[RoomInfo]


class RoomJoinRequest(BaseModel):
    room_id: int
    select_difficulty: LiveDifficulty


class RoomJoinResponse(BaseModel):
    join_room_result: JoinRoomResult


class RoomWaitRequest(BaseModel):
    room_id: int


class RoomWaitResponse(BaseModel):
    status: WaitRoomStatus
    room_user_list: list[RoomUser]


class RoomStartRequest(BaseModel):
    room_id: int


class RoomStartResponse(BaseModel):
    pass


class RoomEndRequest(BaseModel):
    room_id: int
    judge_count_list: list[int]
    score: int


class RoomEndResponse(BaseModel):
    pass


class RoomResultRequest(BaseModel):
    room_id: int


class RoomResultResponse(BaseModel):
    result_user_list: list[ResultUser]


@app.post("/user/create", response_model=UserCreateResponse)
def user_create(req: UserCreateRequest):
    """新規ユーザー作成"""
    token = model.create_user(req.user_name, req.leader_card_id)
    return UserCreateResponse(user_token=token)


bearer = HTTPBearer()


def get_auth_token(cred: HTTPAuthorizationCredentials = Depends(bearer)) -> str:
    assert cred is not None
    if not cred.credentials:
        raise HTTPException(status_code=401, detail="invalid credential")
    return cred.credentials


@app.get("/user/me", response_model=SafeUser)
def user_me(token: str = Depends(get_auth_token)):
    user = model.get_user_by_token(token)
    if user is None:
        raise HTTPException(status_code=404)
    # print(f"user_me({token=}, {user=})")
    return user


class Empty(BaseModel):
    pass


@app.post("/user/update", response_model=Empty)
def update(req: UserCreateRequest, token: str = Depends(get_auth_token)):
    """Update user attributes"""
    # print(req)
    model.update_user(token, req.user_name, req.leader_card_id)
    return {}


"""Room APIs"""


@app.post("/room/create", response_model=RoomCreateResponse)
def room_create(req: RoomCreateRequest):
    room_id = model.room_create(req.live_id, req.select_difficulty)
    if room_id is None:
        raise HTTPException(status_code=500)
    # print(f"user_me({token=}, {user=})")
    return RoomCreateResponse(room_id=room_id)


@app.post("/room/list", response_model=RoomListResponse)
def room_list(req: RoomListRequest):
    list_room = model.room_list(req.live_id)
    if list_room is None:
        raise HTTPException(status_code=404)
    # print(f"user_me({token=}, {user=})")
    return list_room


@app.post("/room/join", response_model=RoomJoinResponse)
def room_join(req: RoomJoinRequest):
    result = model.room_join(req.room_id, req.select_difficulty)
    if result is None:
        raise HTTPException(status_code=404)
    # print(f"user_me({token=}, {user=})")
    return result


@app.post("/room/wait", response_model=RoomWaitResponse)
def room_wait(req: RoomWaitRequest):
    result_status = model.room_wait_status(req.room_id)
    if result_status is None:
        raise HTTPException(status_code=404)
    print(result_status)
    result_list = model.room_wait_list(req.room_id)
    if result_list is None:
        raise HTTPException(status_code=404)
    print(result_list)
    # print(f"user_me({token=}, {user=})")
    res = {"status": result_status, "room_user_list": result_list}
    return res
