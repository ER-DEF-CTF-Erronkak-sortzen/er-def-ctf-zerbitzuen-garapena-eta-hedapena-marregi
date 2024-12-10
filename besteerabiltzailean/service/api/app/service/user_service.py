from fastapi import HTTPException, status

from app.model.user_model import User as UserModel
from app.schema import user_schema
from app.service.auth_service import get_password_hash


def get_user(username: str, current_user: user_schema.User):

    def check_user_is_current_user(username: str, current_user: user_schema.User):
        # TODO change to True
        # return username == current_user.email or username == current_user.username
        return True
    
    user = UserModel.filter((UserModel.email == username) | (UserModel.username == username)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if check_user_is_current_user(username, current_user):

        return user_schema.User(
            id = user.id,
            username = user.username,
            email = user.email,
            flag = user.flag,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You cant get this resource with this credentials"
        )