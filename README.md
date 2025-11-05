# SlotSwapper

SlotSwapper is a peer-to-peer time-slot trading application.  
Users create events in their schedule and mark them as **swappable**.  
Other users can view available swap-offers and request to exchange one of their own swappable slots for another user’s slot.

The receiving user can **accept** or **reject**. If accepted → ownership of both slots is exchanged.

This project demonstrates:

- Full-stack architecture (React + FastAPI + PostgreSQL)
- JWT Authentication & protected APIs
- State management and dynamic UI updates
- Real-time notifications using WebSockets
- Clean business logic for event swap transactions

---

## Tech Stack

| Layer | Technology |
|------|------------|
| Frontend | React |
| Backend | FastAPI (Python) |
| Database | PostgreSQL |
| Authentication | JWT Bearer Tokens |
| Realtime Notifications | WebSockets |

---

## Project Structure
```
SlotSwapper/
│
├── scheduler-backend/            # FastAPI backend
│   ├── app/
│   │   ├── main.py               # Entry point for FastAPI
│   │   ├── models.py             # SQLAlchemy models
│   │   ├── schemas.py            # Pydantic schemas
│   │   ├── auth.py               # Authentication & JWT logic
│   │   ├── database.py           # Database connection setup
│   │   └── ws_manager.py         # WebSocket manager for real-time updates
│   └── requirements.txt          # Python dependencies
│
└── scheduler-frontend/           # React frontend
    └── src/
        └── App.js                # Main React component
```

---

## Setup Instructions (Important)

### 1. Clone Repository

```sh
git clone https://github.com/ParidhiShrivastava0406/SlotSwapper.git
cd SlotSwapper
```

### 2. Backend Setup (FastAPI)

```sh
cd scheduler-backend
python -m venv venv
venv\Scripts\activate
```

- Install dependencies:
  pip install -r requirements.txt
- Create .env file:
  DATABASE_URL=""
- Run backend:
  
```sh
uvicorn app.main:app --reload
```
Backend runs at → http://127.0.0.1:8000

### 3. Frontend Setup (React)

```sh
cd ../scheduler-frontend
npm install
npm start
```
Frontend runs at → http://localhost:3000

---

## API Endpoints

---

### **Authentication**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/signup/` | Create a new user |
| POST   | `/login/`  | Login and receive an authentication token |

---

### **Events**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/events/` | Create a new event |
| GET    | `/events/my` | Get events of the logged-in user |
| PATCH  | `/events/{event_id}/status` | Mark an event as **SWAPPABLE** |
| DELETE | `/events/{event_id}` | Delete own event |

---

### **Marketplace**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/swappable-slots` | View swappable events created by other users |

---

### **Swap Operations**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/swap-request` | Request a swap (requires `mySlot` + `theirSlot`) |
| GET    | `/swap-requests/incoming` | View swap requests **you need to respond to** |
| GET    | `/swap-requests/outgoing` | View swap requests **you have sent** |
| POST   | `/swap-response` | Accept or reject a swap request |

---

## Design Decisions

- Implemented event states: **BUSY**, **SWAPPABLE**, and **SWAP_PENDING** to maintain clear event lifecycle and avoid conflicts.
- All swap ownership logic is handled **securely on the backend** to prevent unauthorized modifications.
- **WebSockets** are used to send real-time updates, ensuring users see changes instantly **without needing to refresh**.

---

## Assumptions

- The system **does not currently validate overlapping events**.
- Only **direct 1-to-1 event swaps** are supported at this stage.
- **Only authenticated (logged-in) users** can create, view, or swap events.

---

## Challenges Faced

- Ensuring correct and consistent **state transitions** during swap operations.
- Keeping the **UI synced in real-time** without manual refresh.
- Managing **secure authentication for WebSocket connections**.

---

## Future Improvements

- Replace table-based display with a **full interactive calendar UI**.
- Add **email or mobile push notifications** for swap requests/updates.
- **Deploy to cloud platforms** like Render, Railway, or Vercel for production use.




  
