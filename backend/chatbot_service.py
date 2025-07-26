from database import get_database
from models import ChatMessage
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ChatbotService:
    def __init__(self):
        self.db = None
    
    async def initialize(self):
        """Initialize database connection"""
        self.db = get_database()
    
    async def process_message(self, message: str, session_id: str, user_id: int = None) -> str:
        """Process user message and generate response"""
        try:
            # Simple rule-based responses for now
            response = await self._generate_response(message, user_id)
            
            # Save chat history
            await self._save_chat_history(session_id, message, response, user_id)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "I'm sorry, I encountered an error. Please try again."
    
    async def _generate_response(self, message: str, user_id: int = None) -> str:
        """Generate chatbot response based on message content"""
        message_lower = message.lower()
        
        # Order-related queries
        if any(word in message_lower for word in ['order', 'purchase', 'buy', 'bought']):
            if user_id:
                return await self._handle_order_query(user_id)
            else:
                return "I can help you with your orders! Please provide your user ID or email to look up your order history."
        
        # Product-related queries
        elif any(word in message_lower for word in ['product', 'item', 'search', 'find']):
            return await self._handle_product_query(message)
        
        # Status queries
        elif any(word in message_lower for word in ['status', 'track', 'tracking', 'shipped', 'delivered']):
            return "I can help you track your order status. Please provide your order ID or let me know which recent order you'd like to check."
        
        # Return/refund queries
        elif any(word in message_lower for word in ['return', 'refund', 'exchange']):
            return "I can assist you with returns and refunds. Our return policy allows returns within 30 days of delivery. Would you like me to help you initiate a return?"
        
        # Greeting
        elif any(word in message_lower for word in ['hello', 'hi', 'hey', 'help']):
            return "Hello! I'm your customer service assistant. I can help you with orders, product information, tracking, returns, and more. How can I assist you today?"
        
        # Default response
        else:
            return "I'm here to help! I can assist you with orders, product searches, order tracking, returns, and general customer service questions. What would you like to know?"
    
    async def _handle_order_query(self, user_id: int) -> str:
        """Handle order-related queries"""
        try:
            # Get recent orders for user
            orders_collection = self.db.orders
            recent_orders = await orders_collection.find(
                {"user_id": user_id}
            ).sort("created_at", -1).limit(5).to_list(length=5)
            
            if not recent_orders:
                return "I couldn't find any orders for your account. If you believe this is an error, please contact our support team."
            
            response = f"I found {len(recent_orders)} recent order(s) for you:\n\n"
            for order in recent_orders:
                status = order.get('status', 'Unknown')
                order_id = order.get('order_id', 'N/A')
                created_at = order.get('created_at', 'Unknown')
                num_items = order.get('num_of_item', 0)
                
                response += f"• Order #{order_id}: {status} - {num_items} item(s) - Placed on {created_at}\n"
            
            response += "\nWould you like more details about any specific order?"
            return response
            
        except Exception as e:
            logger.error(f"Error handling order query: {e}")
            return "I'm having trouble accessing your order information right now. Please try again in a moment."
    
    async def _handle_product_query(self, message: str) -> str:
        """Handle product search queries"""
        try:
            # Extract potential product keywords
            words = message.lower().split()
            search_terms = [word for word in words if len(word) > 3 and word not in ['product', 'item', 'search', 'find', 'looking', 'want']]
            
            if not search_terms:
                return "I can help you find products! Please tell me what you're looking for - for example, 'shoes', 'electronics', or a specific brand name."
            
            # Search products in database
            products_collection = self.db.products
            search_query = {"$or": []}
            
            for term in search_terms[:3]:  # Limit to first 3 terms
                search_query["$or"].extend([
                    {"name": {"$regex": term, "$options": "i"}},
                    {"brand": {"$regex": term, "$options": "i"}},
                    {"category": {"$regex": term, "$options": "i"}},
                    {"department": {"$regex": term, "$options": "i"}}
                ])
            
            products = await products_collection.find(search_query).limit(5).to_list(length=5)
            
            if not products:
                return f"I couldn't find any products matching '{' '.join(search_terms)}'. Try different keywords or browse our categories."
            
            response = f"I found {len(products)} product(s) matching your search:\n\n"
            for product in products:
                name = product.get('name', 'Unknown')
                brand = product.get('brand', 'Unknown')
                price = product.get('retail_price', 0)
                category = product.get('category', 'Unknown')
                
                response += f"• {name} by {brand} - ${price:.2f} ({category})\n"
            
            response += "\nWould you like more details about any of these products?"
            return response
            
        except Exception as e:
            logger.error(f"Error handling product query: {e}")
            return "I'm having trouble searching for products right now. Please try again in a moment."
    
    async def _save_chat_history(self, session_id: str, user_message: str, bot_response: str, user_id: int = None):
        """Save chat interaction to database"""
        try:
            chat_collection = self.db.chat_messages
            chat_doc = {
                "session_id": session_id,
                "user_message": user_message,
                "bot_response": bot_response,
                "timestamp": datetime.utcnow(),
                "user_id": user_id
            }
            await chat_collection.insert_one(chat_doc)
        except Exception as e:
            logger.error(f"Error saving chat history: {e}")

    async def get_chat_history(self, session_id: str, limit: int = 10):
        """Get chat history for a session"""
        try:
            chat_collection = self.db.chat_messages
            history = await chat_collection.find(
                {"session_id": session_id}
            ).sort("timestamp", -1).limit(limit).to_list(length=limit)
            
            return list(reversed(history))  # Return in chronological order
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            return []
