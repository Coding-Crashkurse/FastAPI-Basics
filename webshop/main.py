from datetime import datetime, timedelta
from typing import List, Optional
from jose import JWTError, jwt

from fastapi import Depends, FastAPI, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import models
from .crud import create_user, get_user_by_username, get_users
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from . import models, schemas

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


from pydantic import BaseModel

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@app.post("/register")
async def register_user(user: schemas.User, db: Session = Depends(get_db)):
    user_if_exists = get_user_by_username(db=db, username=user.username)
    if user_if_exists:
        raise HTTPException(
            status_code=409, detail=f"{user.email} is already in database"
        )
    return create_user(db=db, user=user)


@app.post("/login")
async def login(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db=db, username=data.username)
    if not pwd_context.verify(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/")
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = get_users(db, skip=skip, limit=limit)
    return users


@app.get("/authonly/", dependencies=[Depends(oauth2_scheme)])
def read_users(response: Response):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    response.set_cookie("token", "muh", httponly=True)
    #payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    #username: str = payload.get("sub")
    #if username is None:
        #raise credentials_exception
    return True
