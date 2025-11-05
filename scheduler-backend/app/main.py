from fastapi import HTTPException, FastAPI, Depends, WebSocket
from sqlalchemy.orm import Session
from app import models, database, schemas
from fastapi.middleware.cors import CORSMiddleware
from app.auth import hash_password, verify_password, create_token, get_current_user_id, decode_token
from fastapi.security import HTTPBearer
from app.ws_manager import manager



models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization", "authorization"],

)


@app.get("/")
def root():
    return {"message": "Scheduler API working!"}


@app.post("/users/")
def create_user(name: str, email: str, db: Session = Depends(database.get_db)):
    new_user = models.User(name=name, email=email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/signup/")
def signup(name: str, email: str, password: str, db: Session = Depends(database.get_db)):
    hashed = hash_password(password)
    new_user = models.User(name=name, email=email, password_hash=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Signup successful"}

@app.post("/login/")
def login(email: str, password: str, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_token(user.id)
    return {"token": token, "user_id": user.id}


@app.post("/events/")
def create_event(event: schemas.EventCreate,
                 db: Session = Depends(database.get_db),
                 user_id: int = Depends(get_current_user_id)):
    new_event = models.Event(
        user_id=user_id,
        title=event.title,
        start_time=event.start_time,
        end_time=event.end_time,
        status=models.EventStatus.BUSY.value
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event


@app.get("/events/my")
def my_events(db: Session = Depends(database.get_db),
              user_id: int = Depends(get_current_user_id)):
    return db.query(models.Event).filter(models.Event.user_id == user_id).all()


@app.patch("/events/{event_id}/status")
def update_event_status(event_id: int,
                        data: schemas.EventUpdateStatus,
                        db: Session = Depends(database.get_db),
                        user_id: int = Depends(get_current_user_id)):
    event = db.query(models.Event).filter(models.Event.id == event_id, models.Event.user_id == user_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if data.status not in [s.value for s in models.EventStatus]:
        raise HTTPException(status_code=400, detail="Invalid status")

    event.status = data.status
    db.commit()
    db.refresh(event)
    return event

@app.get("/swappable-slots")
def swappable_slots(db: Session = Depends(database.get_db), user_id: int = Depends(get_current_user_id)):
    return db.query(models.Event).filter(
        models.Event.status == models.EventStatus.SWAPPABLE.value,
        models.Event.user_id != user_id    # exclude own events
    ).all()


@app.post("/swap-request")
async def create_swap_request(my_slot_id: int, their_slot_id: int,
                        db: Session = Depends(database.get_db),
                        user_id: int = Depends(get_current_user_id)):

    my_slot = db.query(models.Event).filter(models.Event.id == my_slot_id).first()
    their_slot = db.query(models.Event).filter(models.Event.id == their_slot_id).first()

    if not my_slot or not their_slot:
        raise HTTPException(status_code=404, detail="One or both slots not found")

    if my_slot.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not own your selected slot")

    if my_slot.status != models.EventStatus.SWAPPABLE.value or their_slot.status != models.EventStatus.SWAPPABLE.value:
        raise HTTPException(status_code=400, detail="Both slots must be SWAPPABLE")

    swap = models.SwapRequest(
        requester_user_id=user_id,
        responder_user_id=their_slot.user_id,
        my_slot_id=my_slot_id,
        their_slot_id=their_slot_id,
        status=models.SwapStatus.PENDING.value
    )

    my_slot.status = models.EventStatus.SWAP_PENDING.value
    their_slot.status = models.EventStatus.SWAP_PENDING.value

    db.add(swap)
    db.commit()
    db.refresh(swap)

    await manager.send(their_slot.user_id, "You received a new swap request!")

    return {"message": "Swap request sent", "request_id": swap.id}


@app.get("/swap-requests/incoming")
def incoming_requests(db: Session = Depends(database.get_db),
                      user_id: int = Depends(get_current_user_id)):
    return db.query(models.SwapRequest).filter(
        models.SwapRequest.responder_user_id == user_id,
        models.SwapRequest.status == models.SwapStatus.PENDING.value
    ).all()


@app.get("/swap-requests/outgoing")
def outgoing_requests(db: Session = Depends(database.get_db),
                      user_id: int = Depends(get_current_user_id)):
    return db.query(models.SwapRequest).filter(
        models.SwapRequest.requester_user_id == user_id
    ).all()


@app.post("/swap-response")
async def swap_response(request_id: int, accept: bool,
                  db: Session = Depends(database.get_db),
                  user_id: int = Depends(get_current_user_id)):

    req = db.query(models.SwapRequest).filter(models.SwapRequest.id == request_id).first()

    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    if req.responder_user_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    my_slot = db.query(models.Event).filter(models.Event.id == req.my_slot_id).first()
    their_slot = db.query(models.Event).filter(models.Event.id == req.their_slot_id).first()

    if accept:
        my_slot.user_id, their_slot.user_id = their_slot.user_id, my_slot.user_id
        my_slot.status = models.EventStatus.BUSY.value
        their_slot.status = models.EventStatus.BUSY.value
        req.status = models.SwapStatus.ACCEPTED.value

        db.commit()

        await manager.send(req.requester_user_id, "Your swap request was ACCEPTED!")

        return {"message": "Swap accepted"}

    else:
        my_slot.status = models.EventStatus.SWAPPABLE.value
        their_slot.status = models.EventStatus.SWAPPABLE.value
        req.status = models.SwapStatus.REJECTED.value

        db.commit()

        await manager.send(req.requester_user_id, "Your swap request was REJECTED.")

        return {"message": "Swap rejected"}


@app.delete("/events/{event_id}")
def delete_event(event_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(database.get_db)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed to delete another user's event")
    if event.status == models.EventStatus.SWAP_PENDING.value:
        raise HTTPException(status_code=400, detail="Cannot delete event during a pending swap")

    db.delete(event)
    db.commit()
    return {"message": "Event deleted"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token") 
    if not token:
        await websocket.close()
        return

    try:
        user_id = decode_token(token)["user_id"]
    except:
        await websocket.close()
        return

    await manager.connect(user_id, websocket)

    try:
        while True:
            await websocket.receive_text()
    except:
        manager.disconnect(user_id)












