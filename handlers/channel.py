from aiogram import Router
from aiogram.types import ChatJoinRequest
from db.crud import db


router = Router()


@router.chat_join_request()
async def handle_join_request(join_request: ChatJoinRequest):
    user_id = join_request.from_user.id
    
    if await db.is_user_subscription_active(user_id):
        await join_request.approve()
    else:
        await join_request.decline()