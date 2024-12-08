from fastapi import APIRouter, Depends, Body
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import status

from api.schema import user_schema
from api.service import user_service
from api.utils.db import get_db
from api.schema.user_schema import User
from api.service.auth_service import get_current_user
from api.schema.token_schema import Token
from api.service import auth_service

from fastapi import Query
from fastapi import Path

from typing import List, Optional


router = APIRouter(prefix="/api/v1")

@router.get(
    "/user/{username}",
    tags=["users"],
    status_code=status.HTTP_200_OK,
    response_model=user_schema.User,
    dependencies=[Depends(get_db)]
)
def get_user(
    username: str = Path(),
    current_user: User = Depends(get_current_user)
):
    """
    ## Get user information

    ### Args
    The app can receive next fields by url data
    - username: Your username or email

    ### Returns
    - user information
    """
    return user_service.get_user(username, current_user)

@router.post(
    "/login",
    tags=["users"],
    response_model=Token
)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    ## Login for access token

    ### Args
    The app can receive next fields by form data
    - username: Your username or email
    - password: Your password

    ### Returns
    - access token and token type
    """
    access_token = auth_service.generate_token(form_data.username, form_data.password)
    return Token(access_token=access_token, token_type="bearer")