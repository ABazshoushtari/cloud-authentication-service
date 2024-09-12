from fastapi import Depends, FastAPI, Request, Form, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
import crud.authenticate
from config import get_db
from schemas import schemas

app = FastAPI()


@app.post("/users")
def authenticate_user(
        client_request: Request,
        image1: UploadFile = File(...),
        image2: UploadFile = File(...),
        db: Session = Depends(get_db),
        national_id: str = Form(...),
        email: str = Form(...),
        last_name: str = Form(...)

):
    client_ip = client_request.client.host
    return crud.authenticate.create_user_formfile(image1, image2, client_ip, db, national_id, email, last_name)
    # return crud.authenticate.create_user(db=db, user_in=form_file, client_ip=client_ip)


@app.get("/users/status")
def authenticate_user(
        db: Session = Depends(get_db),
        *,
        request,
        client_request: Request
):
    user = crud.authenticate.get_user_status(db=db, national_id=request)
    status = user.state
    user_id = user.id
    ip = client_request.client.host
    if ip != user.ip:
        return {"message:": "Invalid access"}
    if status == "pending":
        return {"message:": "Your authorization request is processing"}
    elif status == "rejected":
        return {"message:": "Your authorization request is rejected"}
    elif status == "accepted":
        return {"message:": f"Your authorization request with id {user_id} is accepted successfully"}
