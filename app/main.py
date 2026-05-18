from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from app.database import get_db
from app.users.router import router as users_router
from app.products.router import router as products_router

load_dotenv()

app = FastAPI()


# test endpoint
@app.get("/")
def root(db=Depends(get_db)):
    return {"message": db.cursor()}


app.include_router(users_router)
app.include_router(products_router)
