#!/usr/bin/env python3
"""
InvestByYourself API WebSocket Endpoints
Tech-028: API Implementation

WebSocket endpoints for real-time data streaming.
"""

from fastapi import APIRouter

router = APIRouter()

from typing import List

from fastapi import Depends, WebSocket, WebSocketDisconnect


# In-memory connection manager for demonstration purposes
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


connect_manager = ConnectionManager()
portfolio_manager = ConnectionManager()
market_manager = ConnectionManager()
alerts_manager = ConnectionManager()


@router.websocket("/ws/connect")
async def websocket_connect(websocket: WebSocket):
    await connect_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo received data for demonstration
            await connect_manager.send_personal_message(f"Received: {data}", websocket)
    except WebSocketDisconnect:
        connect_manager.disconnect(websocket)


@router.websocket("/ws/portfolio")
async def websocket_portfolio(websocket: WebSocket):
    await portfolio_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Here you would handle portfolio update logic
            await portfolio_manager.send_personal_message(
                f"Portfolio update: {data}", websocket
            )
    except WebSocketDisconnect:
        portfolio_manager.disconnect(websocket)


@router.websocket("/ws/market")
async def websocket_market(websocket: WebSocket):
    await market_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Here you would handle market data logic
            await market_manager.send_personal_message(
                f"Market data: {data}", websocket
            )
    except WebSocketDisconnect:
        market_manager.disconnect(websocket)


@router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await alerts_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Here you would handle alert logic
            await alerts_manager.send_personal_message(f"Alert: {data}", websocket)
    except WebSocketDisconnect:
        alerts_manager.disconnect(websocket)
