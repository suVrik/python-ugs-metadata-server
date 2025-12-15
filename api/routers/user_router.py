from fastapi import APIRouter, Query

from common_utils import CommonUtils
from models.user_model import UserResponse

router = APIRouter()

@router.get("", response_model=UserResponse)
async def get_user(name: str = Query(min_length=1, max_length=128)):
    user_id = await CommonUtils.find_or_add_user(name)
    return UserResponse(Id=user_id)
