from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from app.database import get_db_connection
from app.auth.router import router as auth_router

load_dotenv()

app = FastAPI()


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse("static/favicon.ico")


# test endpoint
@app.get("/")
def root(db=Depends(get_db_connection)):
    return {"message": db.cursor()}

app.include_router(auth_router)