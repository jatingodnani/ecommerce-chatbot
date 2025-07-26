from database import get_database
from models import ChatMessage
from datetime import datetime
import logging
import re

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
        
        # Check for specific ID-based queries first
        id_response = await self._handle_id_based_query(message)
        if id_response:
            return id_response
        
        # Order-related queries
        if any(word in message_lower for word in ['order', 'purchase', 'buy', 'bought']):
            if user_id:
                return await self._handle_order_query(user_id)
            else:
                return "I can help you with your orders! Please provide your user ID or email to look up your order history."
        
        # Inventory-related queries
        elif any(word in message_lower for word in ['inventory', 'inventory_item', 'stock']):
            return await self._handle_inventory_query(message)
        
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

    async def _handle_id_based_query(self, message: str) -> str:
        """Handle specific ID-based queries like 'inventory_id:67971' or 'product_id:123'"""
        try:
            # Pattern to match various ID formats
            patterns = [
                r'inventory_id[:\s]+([0-9]+)',
                r'inventory[\s_]item[\s_]id[:\s]+([0-9]+)',
                r'product_id[:\s]+([0-9]+)',
                r'order_id[:\s]+([0-9]+)',
                r'user_id[:\s]+([0-9]+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, message.lower())
                if match:
                    id_value = int(match.group(1))
                    
                    if 'inventory' in pattern:
                        return await self._search_inventory_by_id(id_value)
                    elif 'product' in pattern:
                        return await self._search_product_by_id(id_value)
                    elif 'order' in pattern:
                        return await self._search_order_by_id(id_value)
                    elif 'user' in pattern:
                        return await self._search_user_by_id(id_value)
            
            return None  # No ID pattern found
            
        except Exception as e:
            logger.error(f"Error handling ID-based query: {e}")
            return "I encountered an error while searching for that ID. Please try again."
    
    async def _search_inventory_by_id(self, inventory_id: int) -> str:
        """Search for inventory item by inventory_id"""
        try:
            inventory_collection = self.db.inventory_items
            item = await inventory_collection.find_one({"inventory_id": inventory_id})
            
            if not item:
                return f"I couldn't find any inventory item with ID {inventory_id}. Please check the ID and try again."
            
            # Format the response with inventory details
            response = f"📦 **Inventory Item #{inventory_id}**\n\n"
            response += f"• **Product**: {item.get('product_name', 'N/A')} by {item.get('product_brand', 'N/A')}\n"
            response += f"• **Category**: {item.get('product_category', 'N/A')}\n"
            response += f"• **Department**: {item.get('product_department', 'N/A')}\n"
            response += f"• **SKU**: {item.get('product_sku', 'N/A')}\n"
            response += f"• **Cost**: ${item.get('cost', 0):.2f}\n"
            response += f"• **Retail Price**: ${item.get('product_retail_price', 0):.2f}\n"
            response += f"• **Product ID**: {item.get('product_id', 'N/A')}\n"
            response += f"• **Distribution Center**: {item.get('product_distribution_center_id', 'N/A')}\n"
            
            if item.get('sold_at'):
                response += f"• **Status**: Sold on {item.get('sold_at')}\n"
            else:
                response += f"• **Status**: Available\n"
            
            response += f"• **Created**: {item.get('created_at', 'N/A')}\n"
            
            return response
            
        except Exception as e:
            logger.error(f"Error searching inventory by ID: {e}")
            return f"I encountered an error while searching for inventory item {inventory_id}. Please try again."
    
    async def _search_product_by_id(self, product_id: int) -> str:
        """Search for product by product_id"""
        try:
            products_collection = self.db.products
            product = await products_collection.find_one({"product_id": product_id})
            
            if not product:
                return f"I couldn't find any product with ID {product_id}. Please check the ID and try again."
            
            response = f"🛍️ **Product #{product_id}**\n\n"
            response += f"• **Name**: {product.get('name', 'N/A')}\n"
            response += f"• **Brand**: {product.get('brand', 'N/A')}\n"
            response += f"• **Category**: {product.get('category', 'N/A')}\n"
            response += f"• **Department**: {product.get('department', 'N/A')}\n"
            response += f"• **Cost**: ${product.get('cost', 0):.2f}\n"
            response += f"• **Retail Price**: ${product.get('retail_price', 0):.2f}\n"
            response += f"• **SKU**: {product.get('sku', 'N/A')}\n"
            response += f"• **Distribution Center**: {product.get('distribution_center_id', 'N/A')}\n"
            
            return response
            
        except Exception as e:
            logger.error(f"Error searching product by ID: {e}")
            return f"I encountered an error while searching for product {product_id}. Please try again."
    
    async def _search_order_by_id(self, order_id: int) -> str:
        """Search for order by order_id"""
        try:
            orders_collection = self.db.orders
            order = await orders_collection.find_one({"order_id": order_id})
            
            if not order:
                return f"I couldn't find any order with ID {order_id}. Please check the ID and try again."
            
            response = f"📋 **Order #{order_id}**\n\n"
            response += f"• **Status**: {order.get('status', 'N/A')}\n"
            response += f"• **User ID**: {order.get('user_id', 'N/A')}\n"
            response += f"• **Items**: {order.get('num_of_item', 0)} item(s)\n"
            response += f"• **Created**: {order.get('created_at', 'N/A')}\n"
            
            if order.get('shipped_at'):
                response += f"• **Shipped**: {order.get('shipped_at')}\n"
            if order.get('delivered_at'):
                response += f"• **Delivered**: {order.get('delivered_at')}\n"
            if order.get('returned_at'):
                response += f"• **Returned**: {order.get('returned_at')}\n"
            
            return response
            
        except Exception as e:
            logger.error(f"Error searching order by ID: {e}")
            return f"I encountered an error while searching for order {order_id}. Please try again."
    
    async def _search_user_by_id(self, user_id: int) -> str:
        """Search for user by user_id"""
        try:
            users_collection = self.db.users
            user = await users_collection.find_one({"user_id": user_id})
            
            if not user:
                return f"I couldn't find any user with ID {user_id}. Please check the ID and try again."
            
            response = f"👤 **User #{user_id}**\n\n"
            response += f"• **Name**: {user.get('first_name', '')} {user.get('last_name', '')}\n"
            response += f"• **Email**: {user.get('email', 'N/A')}\n"
            response += f"• **Age**: {user.get('age', 'N/A')}\n"
            response += f"• **Gender**: {user.get('gender', 'N/A')}\n"
            response += f"• **Location**: {user.get('city', 'N/A')}, {user.get('state', 'N/A')}\n"
            response += f"• **Country**: {user.get('country', 'N/A')}\n"
            response += f"• **Traffic Source**: {user.get('traffic_source', 'N/A')}\n"
            response += f"• **Created**: {user.get('created_at', 'N/A')}\n"
            
            return response
            
        except Exception as e:
            logger.error(f"Error searching user by ID: {e}")
            return f"I encountered an error while searching for user {user_id}. Please try again."
    
    async def _handle_inventory_query(self, message: str) -> str:
        """Handle general inventory queries"""
        try:
            # Check if it's a specific search query
            if any(word in message.lower() for word in ['search', 'find', 'show', 'get']):
                inventory_collection = self.db.inventory_items
                
                # Get some sample inventory items
                items = await inventory_collection.find({}).limit(5).to_list(length=5)
                
                if not items:
                    return "I couldn't find any inventory items in the database. The inventory might be empty or still loading."
                
                response = "📦 **Sample Inventory Items:**\n\n"
                for item in items:
                    response += f"• **ID {item.get('inventory_id')}**: {item.get('product_name', 'N/A')} - ${item.get('product_retail_price', 0):.2f}\n"
                
                response += "\n💡 **Tip**: You can search for specific items by asking:\n"
                response += "• \"inventory_id:67971\" - to find a specific inventory item\n"
                response += "• \"show me inventory for product_id:123\" - to find inventory for a product\n"
                
                return response
            else:
                return "I can help you with inventory queries! Try asking:\n• \"inventory_id:67971\" to find a specific item\n• \"show me inventory\" to see sample items\n• \"search inventory\" to browse available items"
                
        except Exception as e:
            logger.error(f"Error handling inventory query: {e}")
            return "I'm having trouble accessing inventory information right now. Please try again in a moment."
    
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
