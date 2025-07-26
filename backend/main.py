from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
from datetime import datetime

from database import connect_to_mongo, close_mongo_connection, get_database
from models import ChatRequest, ChatResponse, ChatMessage
from chatbot_service import ChatbotService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize chatbot service
chatbot_service = ChatbotService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    await chatbot_service.initialize()
    logger.info("Application startup complete")
    yield
    # Shutdown
    await close_mongo_connection()
    logger.info("Application shutdown complete")

app = FastAPI(
    title="E-commerce Chatbot API",
    description="Conversational AI backend for customer service chatbot",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "E-commerce Chatbot API is running",
        "timestamp": datetime.utcnow(),
        "status": "healthy"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint for processing user messages"""
    try:
        response = await chatbot_service.process_message(
            message=request.message,
            session_id=request.session_id,
            user_id=request.user_id
        )
        
        return ChatResponse(
            response=response,
            session_id=request.session_id,
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str, limit: int = 10):
    """Get chat history for a session"""
    try:
        history = await chatbot_service.get_chat_history(session_id, limit)
        return {"session_id": session_id, "history": history}
    
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/data/stats")
async def get_data_stats():
    """Get statistics about the loaded data"""
    try:
        db = get_database()
        
        stats = {}
        collections = [
            "distribution_centers", "products", "users", 
            "orders", "inventory_items", "order_items"
        ]
        
        for collection_name in collections:
            collection = db[collection_name]
            count = await collection.count_documents({})
            stats[collection_name] = count
        
        return {"data_statistics": stats, "timestamp": datetime.utcnow()}
    
    except Exception as e:
        logger.error(f"Error getting data stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/users/{user_id}/orders")
async def get_user_orders(user_id: int, limit: int = 10):
    """Get orders for a specific user"""
    try:
        db = get_database()
        orders_collection = db.orders
        
        orders = await orders_collection.find(
            {"user_id": user_id}
        ).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        # Convert ObjectId to string for JSON serialization
        for order in orders:
            if "_id" in order:
                order["_id"] = str(order["_id"])
        
        return {
            "user_id": user_id,
            "orders": orders,
            "count": len(orders)
        }
    
    except Exception as e:
        logger.error(f"Error getting user orders: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/products/search")
async def search_products(q: str, limit: int = 10):
    """Search products by name, brand, or category"""
    try:
        db = get_database()
        products_collection = db.products
        
        search_query = {
            "$or": [
                {"name": {"$regex": q, "$options": "i"}},
                {"brand": {"$regex": q, "$options": "i"}},
                {"category": {"$regex": q, "$options": "i"}},
                {"department": {"$regex": q, "$options": "i"}}
            ]
        }
        
        products = await products_collection.find(search_query).limit(limit).to_list(length=limit)
        
        # Convert ObjectId to string for JSON serialization
        for product in products:
            if "_id" in product:
                product["_id"] = str(product["_id"])
        
        return {
            "query": q,
            "products": products,
            "count": len(products)
        }
    
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
