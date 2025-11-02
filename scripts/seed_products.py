"""
Seed script to populate the database with products across all categories.
Run this script to add sample products to your database.

Usage:
    poetry run python scripts/seed_products.py
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.product import Product
from app.core.config import DATABASE_URL

# Sample products data
PRODUCTS = [
    # Featured Products (20 items)
    {
        "name": "Premium Wireless Headphones",
        "price": 299.99,
        "category": "featured",
        "description": "High-quality wireless headphones with active noise cancellation and 30-hour battery life",
        "stock": 50,
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500",
    },
    {
        "name": "Smart Watch Pro",
        "price": 399.99,
        "category": "featured",
        "description": "Advanced fitness tracking, heart rate monitoring, and smartphone notifications",
        "stock": 75,
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500",
    },
    {
        "name": "4K Ultra HD Camera",
        "price": 1299.99,
        "category": "featured",
        "description": "Professional mirrorless camera with 45MP sensor and 8K video recording",
        "stock": 25,
        "image_url": "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=500",
    },
    {
        "name": "Designer Leather Jacket",
        "price": 449.99,
        "category": "featured",
        "description": "Genuine leather jacket with premium craftsmanship and timeless design",
        "stock": 40,
        "image_url": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500",
    },
    {
        "name": "Portable SSD 2TB",
        "price": 179.99,
        "category": "featured",
        "description": "Ultra-fast portable storage with USB-C connectivity and 2000MB/s speeds",
        "stock": 100,
        "image_url": "https://images.unsplash.com/photo-1531492746076-161ca9bcad58?w=500",
    },
    {
        "name": "Gaming Mechanical Keyboard",
        "price": 149.99,
        "category": "featured",
        "description": "RGB backlit mechanical keyboard with Cherry MX switches",
        "stock": 60,
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500",
    },
    {
        "name": "Premium Coffee Maker",
        "price": 249.99,
        "category": "featured",
        "description": "Professional-grade espresso machine with milk frother and programmable settings",
        "stock": 35,
        "image_url": "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=500",
    },
    {
        "name": "Electric Scooter",
        "price": 599.99,
        "category": "featured",
        "description": "Foldable electric scooter with 25-mile range and smartphone app",
        "stock": 20,
        "image_url": "https://images.unsplash.com/photo-1629250344719-5c4b6e26e89b?w=500",
    },
    {
        "name": "Luxury Sunglasses",
        "price": 199.99,
        "category": "featured",
        "description": "Polarized designer sunglasses with UV400 protection",
        "stock": 80,
        "image_url": "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=500",
    },
    {
        "name": "Professional Drone",
        "price": 899.99,
        "category": "featured",
        "description": "4K camera drone with obstacle avoidance and 30-minute flight time",
        "stock": 15,
        "image_url": "https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=500",
    },
    {
        "name": "Smart Home Hub",
        "price": 129.99,
        "category": "featured",
        "description": "Central control for all your smart home devices with voice assistant",
        "stock": 90,
        "image_url": "https://images.unsplash.com/photo-1558089687-e1923e7f8e01?w=500",
    },
    {
        "name": "Fitness Tracker Band",
        "price": 79.99,
        "category": "featured",
        "description": "Water-resistant fitness band with sleep tracking and 7-day battery",
        "stock": 120,
        "image_url": "https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=500",
    },
    {
        "name": "Wireless Charging Pad",
        "price": 39.99,
        "category": "featured",
        "description": "Fast wireless charger compatible with all Qi-enabled devices",
        "stock": 150,
        "image_url": "https://images.unsplash.com/photo-1591290619762-c588828c1cea?w=500",
    },
    {
        "name": "Portable Bluetooth Speaker",
        "price": 89.99,
        "category": "featured",
        "description": "Waterproof speaker with 360° sound and 12-hour battery life",
        "stock": 85,
        "image_url": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=500",
    },
    {
        "name": "USB-C Hub Pro",
        "price": 69.99,
        "category": "featured",
        "description": "7-in-1 USB-C hub with HDMI, USB 3.0, SD card reader, and power delivery",
        "stock": 110,
        "image_url": "https://images.unsplash.com/photo-1625948515291-69613efd103f?w=500",
    },
    {
        "name": "Smart LED Light Bulb 4-Pack",
        "price": 59.99,
        "category": "featured",
        "description": "Color-changing smart bulbs with app and voice control",
        "stock": 140,
        "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500",
    },
    {
        "name": "Ergonomic Office Chair",
        "price": 349.99,
        "category": "featured",
        "description": "Premium mesh office chair with lumbar support and adjustable armrests",
        "stock": 30,
        "image_url": "https://images.unsplash.com/photo-1592078615290-033ee584e267?w=500",
    },
    {
        "name": "Laptop Stand Aluminum",
        "price": 44.99,
        "category": "featured",
        "description": "Adjustable aluminum laptop stand with heat dissipation design",
        "stock": 95,
        "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500",
    },
    {
        "name": "Wireless Gaming Mouse",
        "price": 79.99,
        "category": "featured",
        "description": "High-precision wireless mouse with 16000 DPI and programmable buttons",
        "stock": 70,
        "image_url": "https://images.unsplash.com/photo-1527814050087-3793815479db?w=500",
    },
    {
        "name": "Webcam 1080P HD",
        "price": 69.99,
        "category": "featured",
        "description": "Full HD webcam with auto-focus and built-in noise-canceling microphone",
        "stock": 65,
        "image_url": "https://images.unsplash.com/photo-1587825140708-dfaf72ae4b04?w=500",
    },
    # Electronics (30 items)
    {
        "name": "Laptop 15.6-inch i7",
        "price": 1099.99,
        "category": "electronics",
        "description": "Powerful laptop with Intel i7, 16GB RAM, and 512GB SSD",
        "stock": 45,
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500",
    },
    {
        "name": "Tablet 10-inch",
        "price": 329.99,
        "category": "electronics",
        "description": "Slim tablet with crisp display and all-day battery life",
        "stock": 60,
        "image_url": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=500",
    },
    {
        "name": "Smartphone 5G 128GB",
        "price": 799.99,
        "category": "electronics",
        "description": "Latest 5G smartphone with triple camera system",
        "stock": 55,
        "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500",
    },
    {
        "name": "27-inch 4K Monitor",
        "price": 449.99,
        "category": "electronics",
        "description": "Professional 4K monitor with IPS panel and HDR support",
        "stock": 40,
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500",
    },
    {
        "name": "Wireless Earbuds Pro",
        "price": 199.99,
        "category": "electronics",
        "description": "True wireless earbuds with active noise cancellation",
        "stock": 100,
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500",
    },
    {
        "name": "External Hard Drive 4TB",
        "price": 109.99,
        "category": "electronics",
        "description": "Portable external drive with USB 3.0 for fast file transfers",
        "stock": 75,
        "image_url": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=500",
    },
    {
        "name": "Graphics Card RTX",
        "price": 699.99,
        "category": "electronics",
        "description": "High-performance GPU for gaming and content creation",
        "stock": 20,
        "image_url": "https://images.unsplash.com/photo-1591488320449-011701bb6704?w=500",
    },
    {
        "name": "Motherboard ATX",
        "price": 249.99,
        "category": "electronics",
        "description": "ATX motherboard with latest chipset and RGB lighting",
        "stock": 35,
        "image_url": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=500",
    },
    {
        "name": "RAM 32GB DDR4",
        "price": 139.99,
        "category": "electronics",
        "description": "High-speed 32GB RAM kit for multitasking and gaming",
        "stock": 80,
        "image_url": "https://images.unsplash.com/photo-1541025598-15428ee9ca3d?w=500",
    },
    {
        "name": "Power Supply 750W",
        "price": 119.99,
        "category": "electronics",
        "description": "Modular 80+ Gold certified power supply",
        "stock": 50,
        "image_url": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=500",
    },
    {
        "name": "CPU Cooler RGB",
        "price": 89.99,
        "category": "electronics",
        "description": "Liquid CPU cooler with RGB lighting and quiet fans",
        "stock": 60,
        "image_url": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=500",
    },
    {
        "name": "PC Case Mid Tower",
        "price": 149.99,
        "category": "electronics",
        "description": "Tempered glass mid-tower case with excellent airflow",
        "stock": 45,
        "image_url": "https://images.unsplash.com/photo-1587202372583-49330a15584d?w=500",
    },
    {
        "name": "NVMe SSD 1TB",
        "price": 129.99,
        "category": "electronics",
        "description": "Ultra-fast NVMe M.2 SSD with 3500MB/s read speeds",
        "stock": 90,
        "image_url": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=500",
    },
    {
        "name": "USB Microphone",
        "price": 129.99,
        "category": "electronics",
        "description": "Studio-quality USB microphone for streaming and recording",
        "stock": 55,
        "image_url": "https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=500",
    },
    {
        "name": "Ring Light 18-inch",
        "price": 79.99,
        "category": "electronics",
        "description": "Dimmable LED ring light perfect for photography and video",
        "stock": 70,
        "image_url": "https://images.unsplash.com/photo-1626897505254-e0f811aa9bf7?w=500",
    },
    {
        "name": "Green Screen Backdrop",
        "price": 49.99,
        "category": "electronics",
        "description": "Collapsible green screen for professional video backgrounds",
        "stock": 65,
        "image_url": "https://images.unsplash.com/photo-1585241645927-c7a8e5840c42?w=500",
    },
    {
        "name": "Action Camera 4K",
        "price": 249.99,
        "category": "electronics",
        "description": "Waterproof action camera with 4K video and image stabilization",
        "stock": 40,
        "image_url": "https://images.unsplash.com/photo-1557180295-76eee20ae8aa?w=500",
    },
    {
        "name": "Tripod Professional",
        "price": 89.99,
        "category": "electronics",
        "description": "Aluminum tripod with fluid head for smooth camera movements",
        "stock": 50,
        "image_url": "https://images.unsplash.com/photo-1606986628934-e0b77e5c7c53?w=500",
    },
    {
        "name": "Camera Lens 50mm",
        "price": 399.99,
        "category": "electronics",
        "description": "Prime lens with f/1.8 aperture for beautiful bokeh",
        "stock": 30,
        "image_url": "https://images.unsplash.com/photo-1606986628934-e0b77e5c7c53?w=500",
    },
    {
        "name": "Memory Card 128GB",
        "price": 29.99,
        "category": "electronics",
        "description": "High-speed SD card with UHS-I U3 rating",
        "stock": 150,
        "image_url": "https://images.unsplash.com/photo-1577705998148-6da4f3963bc8?w=500",
    },
    {
        "name": "Gimbal Stabilizer",
        "price": 159.99,
        "category": "electronics",
        "description": "3-axis gimbal for smooth smartphone and camera footage",
        "stock": 35,
        "image_url": "https://images.unsplash.com/photo-1626806819282-2c1dc01a5e0c?w=500",
    },
    {
        "name": "Studio Lighting Kit",
        "price": 199.99,
        "category": "electronics",
        "description": "Complete 3-light studio lighting setup with softboxes",
        "stock": 25,
        "image_url": "https://images.unsplash.com/photo-1626897505254-e0f811aa9bf7?w=500",
    },
    {
        "name": "Video Capture Card",
        "price": 149.99,
        "category": "electronics",
        "description": "4K HDMI capture card for streaming and recording",
        "stock": 40,
        "image_url": "https://images.unsplash.com/photo-1625948515291-69613efd103f?w=500",
    },
    {
        "name": "Streaming Deck",
        "price": 249.99,
        "category": "electronics",
        "description": "Programmable button deck for stream control",
        "stock": 45,
        "image_url": "https://images.unsplash.com/photo-1629900223729-79071da0ffb5?w=500",
    },
    {
        "name": "Cable Management Kit",
        "price": 24.99,
        "category": "electronics",
        "description": "Complete cable management solution for clean desk setup",
        "stock": 200,
        "image_url": "https://images.unsplash.com/photo-1625948515291-69613efd103f?w=500",
    },
    {
        "name": "Surge Protector 12-Outlet",
        "price": 39.99,
        "category": "electronics",
        "description": "Heavy-duty surge protector with USB charging ports",
        "stock": 100,
        "image_url": "https://images.unsplash.com/photo-1591290619762-c588828c1cea?w=500",
    },
    {
        "name": "Monitor Arm Dual",
        "price": 119.99,
        "category": "electronics",
        "description": "Gas spring dual monitor arm with full motion adjustment",
        "stock": 55,
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500",
    },
    {
        "name": "KVM Switch 4-Port",
        "price": 89.99,
        "category": "electronics",
        "description": "Switch between 4 computers with one keyboard and mouse",
        "stock": 40,
        "image_url": "https://images.unsplash.com/photo-1625948515291-69613efd103f?w=500",
    },
    {
        "name": "Desktop Microphone Arm",
        "price": 49.99,
        "category": "electronics",
        "description": "Adjustable boom arm with cable management",
        "stock": 70,
        "image_url": "https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=500",
    },
    {
        "name": "Acoustic Foam Panels 12-Pack",
        "price": 34.99,
        "category": "electronics",
        "description": "Sound dampening panels for recording studios",
        "stock": 85,
        "image_url": "https://images.unsplash.com/photo-1598653222000-6b7b7a552625?w=500",
    },
    # Clothing (30 items)
    {
        "name": "Classic White T-Shirt",
        "price": 24.99,
        "category": "clothing",
        "description": "100% cotton premium white t-shirt with comfortable fit",
        "stock": 200,
        "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500",
    },
    {
        "name": "Slim Fit Jeans",
        "price": 79.99,
        "category": "clothing",
        "description": "Classic blue denim jeans with modern slim fit",
        "stock": 150,
        "image_url": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=500",
    },
    {
        "name": "Hoodie Premium Cotton",
        "price": 59.99,
        "category": "clothing",
        "description": "Comfortable hoodie with kangaroo pocket and drawstring hood",
        "stock": 120,
        "image_url": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=500",
    },
    {
        "name": "Running Shoes Athletic",
        "price": 119.99,
        "category": "clothing",
        "description": "Lightweight running shoes with cushioned sole",
        "stock": 90,
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500",
    },
    {
        "name": "Dress Shirt Formal",
        "price": 69.99,
        "category": "clothing",
        "description": "Elegant dress shirt perfect for business occasions",
        "stock": 80,
        "image_url": "https://images.unsplash.com/photo-1620012253295-c15cc3e65df4?w=500",
    },
    {
        "name": "Casual Sneakers White",
        "price": 89.99,
        "category": "clothing",
        "description": "Versatile white sneakers for everyday wear",
        "stock": 110,
        "image_url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=500",
    },
    {
        "name": "Winter Jacket Insulated",
        "price": 179.99,
        "category": "clothing",
        "description": "Warm insulated jacket with water-resistant exterior",
        "stock": 60,
        "image_url": "https://images.unsplash.com/photo-1544923246-77307d671f9d?w=500",
    },
    {
        "name": "Yoga Pants High-Waist",
        "price": 49.99,
        "category": "clothing",
        "description": "Stretchy yoga pants with moisture-wicking fabric",
        "stock": 140,
        "image_url": "https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=500",
    },
    {
        "name": "Baseball Cap Adjustable",
        "price": 24.99,
        "category": "clothing",
        "description": "Classic baseball cap with adjustable strap",
        "stock": 180,
        "image_url": "https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=500",
    },
    {
        "name": "Cotton Socks 6-Pack",
        "price": 19.99,
        "category": "clothing",
        "description": "Comfortable cotton socks in assorted colors",
        "stock": 250,
        "image_url": "https://images.unsplash.com/photo-1586350977771-b3b0abd50c82?w=500",
    },
    {
        "name": "Sports Bra Seamless",
        "price": 39.99,
        "category": "clothing",
        "description": "Supportive sports bra for high-intensity workouts",
        "stock": 100,
        "image_url": "https://images.unsplash.com/photo-1594223274512-ad4803739b7c?w=500",
    },
    {
        "name": "Chino Pants Khaki",
        "price": 69.99,
        "category": "clothing",
        "description": "Versatile khaki chinos for casual or business casual",
        "stock": 95,
        "image_url": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=500",
    },
    {
        "name": "Polo Shirt Classic",
        "price": 44.99,
        "category": "clothing",
        "description": "Timeless polo shirt with collar and button placket",
        "stock": 130,
        "image_url": "https://images.unsplash.com/photo-1528991435120-e73e05a58897?w=500",
    },
    {
        "name": "Cardigan Sweater",
        "price": 64.99,
        "category": "clothing",
        "description": "Cozy cardigan sweater with button front",
        "stock": 75,
        "image_url": "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=500",
    },
    {
        "name": "Tank Top Athletic 3-Pack",
        "price": 29.99,
        "category": "clothing",
        "description": "Breathable tank tops for gym and active wear",
        "stock": 160,
        "image_url": "https://images.unsplash.com/photo-1622519407650-3df9883f76e0?w=500",
    },
    {
        "name": "Swim Trunks Quick-Dry",
        "price": 39.99,
        "category": "clothing",
        "description": "Quick-drying swim shorts with mesh lining",
        "stock": 85,
        "image_url": "https://images.unsplash.com/photo-1519238263530-99bdd11df2ea?w=500",
    },
    {
        "name": "Flannel Shirt Plaid",
        "price": 54.99,
        "category": "clothing",
        "description": "Warm flannel shirt in classic plaid pattern",
        "stock": 90,
        "image_url": "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=500",
    },
    {
        "name": "Denim Jacket Classic",
        "price": 89.99,
        "category": "clothing",
        "description": "Timeless denim jacket with button front",
        "stock": 70,
        "image_url": "https://images.unsplash.com/photo-1543076659-9380cdf10613?w=500",
    },
    {
        "name": "Shorts Cargo Multi-Pocket",
        "price": 44.99,
        "category": "clothing",
        "description": "Practical cargo shorts with multiple pockets",
        "stock": 105,
        "image_url": "https://images.unsplash.com/photo-1591195853828-11db59a44f6b?w=500",
    },
    {
        "name": "Beanie Winter Hat",
        "price": 19.99,
        "category": "clothing",
        "description": "Warm knit beanie for cold weather",
        "stock": 150,
        "image_url": "https://images.unsplash.com/photo-1576871337632-b9aef4c17ab9?w=500",
    },
    {
        "name": "Scarf Wool Blend",
        "price": 34.99,
        "category": "clothing",
        "description": "Soft wool blend scarf in neutral colors",
        "stock": 120,
        "image_url": "https://images.unsplash.com/photo-1520903920243-00d872a2d1c9?w=500",
    },
    {
        "name": "Gloves Touchscreen Winter",
        "price": 29.99,
        "category": "clothing",
        "description": "Warm gloves with touchscreen-compatible fingertips",
        "stock": 140,
        "image_url": "https://images.unsplash.com/photo-1520903920243-00d872a2d1c9?w=500",
    },
    {
        "name": "Belt Leather Reversible",
        "price": 39.99,
        "category": "clothing",
        "description": "Genuine leather belt reversible to black or brown",
        "stock": 110,
        "image_url": "https://images.unsplash.com/photo-1624222247344-550fb60583bb?w=500",
    },
    {
        "name": "Tie Silk Classic",
        "price": 44.99,
        "category": "clothing",
        "description": "Elegant silk tie for formal occasions",
        "stock": 95,
        "image_url": "https://images.unsplash.com/photo-1617127365659-c47fa864d8bc?w=500",
    },
    {
        "name": "Dress Formal Black",
        "price": 129.99,
        "category": "clothing",
        "description": "Elegant black dress perfect for special occasions",
        "stock": 55,
        "image_url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=500",
    },
    {
        "name": "Blouse Silk Sleeveless",
        "price": 74.99,
        "category": "clothing",
        "description": "Stylish silk blouse with elegant drape",
        "stock": 70,
        "image_url": "https://images.unsplash.com/photo-1618932260643-eee4a2f652a6?w=500",
    },
    {
        "name": "Skirt Midi Pleated",
        "price": 59.99,
        "category": "clothing",
        "description": "Flowing pleated midi skirt in solid color",
        "stock": 80,
        "image_url": "https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?w=500",
    },
    {
        "name": "Leggings High-Waist Black",
        "price": 39.99,
        "category": "clothing",
        "description": "Versatile black leggings with high waistband",
        "stock": 170,
        "image_url": "https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=500",
    },
    {
        "name": "Blazer Professional",
        "price": 149.99,
        "category": "clothing",
        "description": "Tailored blazer for business or formal events",
        "stock": 50,
        "image_url": "https://images.unsplash.com/photo-1591369822096-ffd140ec948f?w=500",
    },
    {
        "name": "Pajama Set Comfortable",
        "price": 49.99,
        "category": "clothing",
        "description": "Soft pajama set for comfortable sleep",
        "stock": 100,
        "image_url": "https://images.unsplash.com/photo-1596522354195-e84ae3c98731?w=500",
    },
]


async def seed_products():
    """Seed the database with sample products"""
    engine = create_async_engine(str(DATABASE_URL), echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Check if products already exist
        from sqlalchemy import select as sql_select

        result = await session.execute(sql_select(Product).limit(1))
        existing = result.scalars().first()

        if existing:
            print("Products already exist in the database. Skipping seed.")
            print("If you want to re-seed, delete all products first.")
            return

        # Add all products
        for product_data in PRODUCTS:
            product = Product(**product_data)
            session.add(product)

        await session.commit()
        print(f"\n[SUCCESS] Successfully seeded {len(PRODUCTS)} products!")
        print(
            f"   - Featured: {len([p for p in PRODUCTS if p['category'] == 'featured'])}"
        )
        print(
            f"   - Electronics: {len([p for p in PRODUCTS if p['category'] == 'electronics'])}"
        )
        print(
            f"   - Clothing: {len([p for p in PRODUCTS if p['category'] == 'clothing'])}"
        )


if __name__ == "__main__":
    print("[INFO] Starting product seeding...")
    asyncio.run(seed_products())
    print("[DONE] Seeding complete!")
