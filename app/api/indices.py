from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.db.database import engine
from app.db.models import Indices, IndexValue, IndexDaily, IndexConstituent
from datetime import datetime
from app.schemas.indices import IndexReponse

router = APIRouter()


@router.get("/indices", response_model=list[IndexReponse])
def get_indices():
    try:
        with Session(engine) as db:
            indices = db.query(Indices).filter(Indices.status == "active").all()
            return indices

    except Exception as e:
        print(f"error in db query")  




@router.get("/indices/{indexId}")
def get_index(indexId: int):
    try:
        with Session(engine) as db:
            index = db.query(IndexValue).filter(
                IndexValue.index_id == indexId
            ).order_by(
                IndexValue.timestamp.desc()
            ).first()

            if index is None:
                return {"error": "Index value not found"}

            daily = db.query(IndexDaily).filter(
                IndexDaily.index_id == indexId
            ).order_by(
                IndexDaily.date.desc()
            ).first()

            if daily is None:
                return {
                    "index_value": index.index_value,
                    "timestamp": index.timestamp,
                    "open": None,
                    "previous_close": None,
                    "high": None,
                    "low": None,
                    "change": None,
                    "change_percent": None
                }

            previous_daily = db.query(IndexDaily).filter(
                IndexDaily.index_id == indexId,
                IndexDaily.date < daily.date
            ).order_by(
                IndexDaily.date.desc()
            ).first()

            return {
                "index_value": index.index_value,
                "timestamp": index.timestamp,
                "open": daily.open,
                "previous_close": previous_daily.close,
                "high": daily.high,
                "low": daily.low,
                "change": daily.close - previous_daily.close,
                "change_percent": (
                    (daily.close - previous_daily.close)
                    / previous_daily.close
                ) * 100
            }

    except Exception as e:
        print(
            f"[GET_INDEX] Failed for index_id={indexId}: {e}",
            flush=True
        )



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


@router.get("/indices/{indexId}/constituents")
def get_index_constituents(indexId: int):
    try:
        with Session(engine) as db:
            constituents = db.query(IndexConstituent).filter(
                IndexConstituent.index_id == indexId
            ).all()

            return [
                {
                    "security_id": constituent.security_id,
                    "symbol": constituent.security.symbol,
                    "company_name": constituent.security.company_name,
                    "weight": constituent.weight
                }
                for constituent in constituents
            ]

    except Exception as e:
        print(
            f"[GET_CONSTITUENTS] Failed for index_id={indexId}: {e}",
            flush=True
        )
        return {
            "error": "Failed to retrieve index constituents"
        }