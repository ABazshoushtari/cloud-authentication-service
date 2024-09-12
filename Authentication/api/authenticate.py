from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

import crud.authenticate
from config import get_db
from schemas import schemas

app = FastAPI()


@app.post("/users", response_model=schemas.AuthenticationResponse)
def authenticate_user(
        db: Session = Depends(get_db),
        *,
        request: schemas.AuthenticationRequest,
):
    return crud.authenticate.create_user(db=db, user_in=request)
