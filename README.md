# 🤖 E-commerce Customer Service Chatbot

A powerful conversational AI system for e-commerce customer service built with FastAPI, React, and MongoDB Atlas. This chatbot provides intelligent responses for order inquiries, product searches, inventory management, and customer support.

## 🚀 Features

- **🔍 Advanced ID-Based Search**: Search by specific inventory, product, order, or user IDs
- **🛍️ Product Discovery**: Natural language product search and recommendations
- **📦 Order Management**: Order tracking, status updates, and history
- **📊 Inventory Queries**: Real-time inventory information and availability
- **💬 Natural Language Processing*Understands various query formats and intents
- ***: 🎨 Modern UI**: Beautiful, responsive React frontend with real-time chat
- **⚡ Fast API**: High-performance FastAPI backend with async operations
- **☁️ Cloud Database**: MongoDB Atlas integration for scalable data storage

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │◄──►│  FastAPI Backend │◄──►│  MongoDB Atlas  │
│   (Port 5173)   │    │   (Port 8000)   │    │   (Cloud DB)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
ecommerce-chatbot/
├── backend/                 # FastAPI backend
│   ├── main.py             # FastAPI application entry point
│   ├── chatbot_service.py  # Chatbot logic and AI responses
│   ├── database.py         # MongoDB connection and config
│   ├── models.py           # Pydantic data models
│   ├── csv_parser.py       # Data loading utilities
│   ├── data/              # CSV data files
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── App.tsx        # Main chat interface
│   │   ├── App.css        # Modern UI styles
│   │   └── main.tsx       # React entry point
│   ├── package.json       # Node.js dependencies
│   └── vite.config.ts     # Vite configuration
└── README.md              # This file
```

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- MongoDB Atlas account

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install Python dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Configure MongoDB connection:**
   - Update the MongoDB URL in `database.py` with your Atlas credentials

4. **Load CSV data (optional):**
   ```bash
   python3 load_order_items_only.py  # Load missing data
   # OR
   python3 data_loader_api.py        # Load all data
   ```

5. **Start the backend server:**
   ```bash
   python3 main.py
   ```
   Server will run on `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```
   Frontend will run on `http://localhost:5173`

## 🐳 Docker Setup (Recommended)

**The easiest way to run the application locally is using Docker!** This method handles all dependencies and configurations automatically.

### Prerequisites
- Docker Desktop installed and running
- Git (to clone the repository)

### Quick Start with Docker

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd ecommerce-chatbot
   ```

2. **Make scripts executable:**
   ```bash
   chmod +x docker-build.sh docker-run.sh
   ```

3. **Build Docker images:**
   ```bash
   ./docker-run.sh build
   ```
   This will build both frontend and backend Docker images.

4. **Start the application:**
   ```bash
   # For development
   ./docker-run.sh dev
   
   # For production
   ./docker-run.sh prod
   ```

5. **Access your application:**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs

### Docker Commands Reference

```bash
# Build images
./docker-run.sh build

# Start development environment
./docker-run.sh dev

# Start production environment
./docker-run.sh prod

# Stop all containers
./docker-run.sh stop

# Clean up containers and volumes
./docker-run.sh clean

# View container logs
./docker-run.sh logs
```

### Manual Docker Commands

If you prefer to use Docker Compose directly:

```bash
# Development mode
docker-compose up -d

# Production mode
docker-compose -f docker-compose.prod.yml up -d

# Stop containers
docker-compose down

# View logs
docker-compose logs -f

# Rebuild and restart
docker-compose up --build -d
```

### Docker Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   React App     │    │   FastAPI       │
│   Port: 3000    │◄──►│   Port: 8000    │
│   (Frontend)    │    │   (Backend)     │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────────────────┘
                   │
         ┌─────────────────┐
         │  MongoDB Atlas  │
         │   (Database)    │
         └─────────────────┘
```

### Environment Configuration

The Docker setup uses the following configuration:

- **Backend**: FastAPI server running on port 8000
- **Frontend**: React development server on port 3000
- **Database**: MongoDB Atlas (cloud-hosted)
- **Networking**: Internal Docker network for service communication

### Troubleshooting Docker

**Container won't start:**
```bash
# Check container status
docker ps -a

# View container logs
docker logs ecommerce-chatbot-backend
docker logs ecommerce-chatbot-frontend
```

**Port conflicts:**
```bash
# Stop any existing containers
./docker-run.sh stop

# Check what's using the ports
lsof -i :3000
lsof -i :8000
```

**Clean restart:**
```bash
# Complete cleanup and restart
./docker-run.sh clean
./docker-run.sh build
./docker-run.sh dev
```

## 💬 Chatbot Capabilities

### 🔍 **ID-Based Searches**

#### Inventory Queries:
- `inventory_id:67971`
- `give me inventory_items with inventory_id:67971`
- `show inventory item 67971`
- `find inventory_item_id:12345`

#### Product Queries:
- `product_id:123`
- `show me product_id:456`
- `find product 789`

#### Order Queries:
- `order_id:12345`
- `show me order 67890`
- `find order_id:11111`

#### User Queries:
- `user_id:1`
- `show me user_id:2345`
- `find user 6789`

### 🛍️ **General E-commerce Queries**

#### Product Searches:
- `search for shoes`
- `find electronics`
- `show me Nike products`
- `look for laptops`

#### Order Management:
- `show my orders` (when user_id is provided)
- `my order history`
- `recent purchases`

#### Inventory Browsing:
- `show me inventory`
- `search inventory`
- `find inventory items`

#### Order Tracking:
- `track my order`
- `order status`
- `where is my package`
- `delivery status`

#### Returns & Support:
- `return policy`
- `how to return`
- `refund request`
- `exchange item`

#### General Help:
- `hello`
- `hi there`
- `help me`
- `what can you do`

## 🔌 API Endpoints

### Chat Endpoints
- `POST /chat` - Send message to chatbot
- `GET /chat/history/{session_id}` - Get chat history

### Data Endpoints
- `GET /data/stats` - Get database statistics
- `GET /users/{user_id}/orders` - Get user orders
- `GET /products/search?q={query}` - Search products

### Health Check
- `GET /` - API health status

## 📊 Database Schema

The system uses MongoDB with the following collections:

- **distribution_centers**: Warehouse locations
- **products**: Product catalog
- **users**: Customer information
- **orders**: Order records
- **inventory_items**: Stock items
- **order_items**: Individual items in orders
- **chat_messages**: Conversation history

## 🧪 Testing Examples

1. **Test Inventory Search:**
   ```
   User: inventory_id:67971
   Bot: 📦 Inventory Item #67971
        • Product: [Product Name] by [Brand]
        • Category: [Category]
        • Price: $XX.XX
        • Status: Available
   ```

2. **Test Product Search:**
   ```
   User: search for shoes
   Bot: I found 5 product(s) matching your search:
        • Nike Air Max - $120.00 (Footwear)
        • Adidas Sneakers - $95.00 (Footwear)
   ```

3. **Test Order Tracking:**
   ```
   User: order_id:12345
   Bot: 📋 Order #12345
        • Status: Shipped
        • Items: 2 item(s)
        • Shipped: 2025-01-20
   ```



## 🆘 Support

If you encounter any issues or have questions:
1. Check the API health endpoint: `http://localhost:8000/`
2. Verify MongoDB connection in the backend logs
3. Ensure all dependencies are installed correctly

---

**Built with ❤️ using FastAPI, React, and MongoDB Atlas**