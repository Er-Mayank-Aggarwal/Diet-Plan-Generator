from fastapi import FastAPI
from app.core.middleware import jwt_middleware

from app.routers.users import router as users_router
from app.routers.intake import router as intake_router
from app.routers.plan import router as plan_router
from app.routers.foods import router as foods_router
from app.routers.favorites import router as favorites_router

app = FastAPI(title="Diet Planner API")

app.middleware("http")(jwt_middleware)

app.include_router(users_router, prefix="/api/user")
app.include_router(intake_router, prefix="/api/intake")
app.include_router(plan_router, prefix="/api/plan")
app.include_router(foods_router, prefix="/api/foods")
app.include_router(favorites_router, prefix="/api/favorites")
