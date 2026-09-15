from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.db.database import engine
from app.db.models import Indices, IndexValue, IndexDaily
from schemas.indices import IndexReponse
from datetime import datetime

router = APIRouter()


router.get("/indices", response_model=list[IndexReponse])
def get_indices():
    try:
        with Session(engine) as db:
            indices = db.query(Indices).filter(Indices.status == "active").all()
            return indices

    except Exception as e:
        print(f"error in db query")  




router.get("/indices/{indexId}")
def get_index(indexId:int):
    try:
        with Session(engine) as db:
            index = db.query(IndexValue).filter(
                IndexValue.index_id == indexId).order_by(
                    IndexValue.timestamp.desc()
                ).first()  

            daily = db.query(IndexDaily).filter(
                IndexDaily.index_id == indexId).order_by(IndexDaily.date.desc()).first()

            previous_daily = db.query(IndexDaily).filter(
                IndexDaily.index_id == indexId, IndexDaily.date < daily.date
                ).order_by(IndexDaily.date.desc() ).first()

              
            return {
                "index_value": index.index_value,
                "timestamp": index.timestamp,
                "open": daily.open,
                "previous_close": previous_daily.close,
                "high": daily.high,
                "low": daily.low,
                "change": daily.close - previous_daily.close,
                "change_percent": ((daily.close - previous_daily.close) / previous_daily.close) * 100
            }

    except Exception as e:
        print(f"")  




connected_clients = {}

@router.websocket("/indices/{indexId}/live")
async def index_live(websocket: WebSocket, indexId: int):
    await websocket.accept()

    if indexId not in connected_clients:
        connected_clients[indexId] = set()

    connected_clients[indexId].add(websocket)

    print(f"Client connected to index {indexId}")
    print(f"Connected clients: {len(connected_clients[indexId])}")

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        connected_clients[indexId].remove(websocket)

        if not connected_clients[indexId]:
            del connected_clients[indexId]

        print(f"Client disconnected from index {indexId}")
        print(f"Connected clients: {len(connected_clients.get(indexId, set()))}")                  

