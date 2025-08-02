"""
ONQL Extension SDK - Go-style functions with shared state
"""
import asyncio
import json
import uuid
import nats
from typing import Dict, Callable, Any, Optional


# Shared state
_connection = None
_keyword = None
_subscriptions = {}
_pending_requests = {}


async def init(keyword: str, nats_url: str = "nats://localhost:4222"):
    """Initialize SDK with keyword and connect to NATS"""
    global _connection, _keyword
    
    _keyword = keyword
    _connection = await nats.connect(nats_url)
    
    # Subscribe to listen channel for responses
    await _connection.subscribe(f"{keyword}.listen", _handle_response)
    
    return True


async def _handle_response(msg):
    """Handle incoming responses"""
    try:
        data = json.loads(msg.data.decode())
        if data.get("type") == "response":
            rid = data.get("rid")
            if rid in _pending_requests:
                future = _pending_requests.pop(rid)
                if not future.done():
                    future.set_result(data)
    except Exception:
        pass


async def request(target: str, payload: Any, timeout: int = 30) -> Dict[str, Any]:
    """Send request to target extension"""
    rid = str(uuid.uuid4())
    
    req = {
        "id": _keyword,
        "rid": rid,
        "target": target,
        "payload": payload,
        "type": "request"
    }
    
    # Create future for response
    future = asyncio.Future()
    _pending_requests[rid] = future
    
    # Send request
    await _connection.publish(f"{target}.send", json.dumps(req).encode())
    
    # Wait for response
    try:
        response = await asyncio.wait_for(future, timeout=timeout)
        return response
    except asyncio.TimeoutError:
        _pending_requests.pop(rid, None)
        return {"type": "timeout", "rid": rid}


async def response(req_data: Dict[str, Any], data: Any):
    """Send response back to requester"""
    res = {
        "id": _keyword,
        "target": req_data["id"],
        "rid": req_data["rid"],
        "payload": req_data["payload"],
        "data": data,
        "type": "response"
    }
    
    await _connection.publish(f"{req_data['id']}.send", json.dumps(res).encode())


def subscribe(channel: str, callback: Callable) -> str:
    """Subscribe to channel and return subscription ID"""
    sub_id = str(uuid.uuid4())
    
    async def handler(msg):
        try:
            data = json.loads(msg.data.decode())
            await callback(data)
        except Exception:
            pass
    
    # Store subscription
    _subscriptions[sub_id] = {
        "channel": channel,
        "callback": callback,
        "handler": handler
    }
    
    # Subscribe to NATS
    asyncio.create_task(_connection.subscribe(channel, handler))
    
    return sub_id


async def unsubscribe(sub_id: str):
    """Unsubscribe using subscription ID"""
    if sub_id in _subscriptions:
        del _subscriptions[sub_id]


def OnRequest(callback: Callable):
    """Subscribe to listen for incoming requests"""
    async def handler(msg):
        try:
            data = json.loads(msg.data.decode())
            if data.get("type") == "request":
                await callback(data)
        except Exception:
            pass
    
    # Subscribe to the send channel for this extension
    asyncio.create_task(_connection.subscribe(f"{_keyword}.send", handler))


async def close():
    """Close connection"""
    if _connection:
        await _connection.close()
        