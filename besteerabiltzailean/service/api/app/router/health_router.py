from fastapi import APIRouter
from fastapi import status



router = APIRouter(prefix="/api/v1")


@router.get("/health",
            tags=["health"],
            status_code=status.HTTP_200_OK,)
def health_check():
    """
    ## Only to check api health

    ### Args
    The app can receive next fields by url data
    - username: Your username or email

    ### Returns
    - Api status
    """
    return {"status": "healthy"}