from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.database import get_db
from app.users.router import auth_router, users_router
from app.products.router import router as products_router
from app.recipes.router import router as recipes_router
from app.meals.router import router as meals_router
from app.leaderboard.router import router as leaderboard_router

load_dotenv()

app = FastAPI(title="Nutrition App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# test endpoint
@app.get("/")
def root(db=Depends(get_db)):
    return {"message": db.cursor()}


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(products_router)
app.include_router(recipes_router)
app.include_router(meals_router)
app.include_router(leaderboard_router)
