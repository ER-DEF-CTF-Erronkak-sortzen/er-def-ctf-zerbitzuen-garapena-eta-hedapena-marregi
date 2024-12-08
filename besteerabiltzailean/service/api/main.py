from fastapi import FastAPI

from service.api.router.user_router import router as user_router
from service.api.router.health_router import router as health_router

from service.api.scripts.create_tables import load_data

#Setup data before app start
load_data()

app = FastAPI()


app.include_router(user_router)
app.include_router(health_router)


