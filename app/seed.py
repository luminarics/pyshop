"""
Database seeding script for PyShop.
Adds sample products to the database for development/testing.
"""

import asyncio
from sqlalchemy import select
from app.database import engine, Base
from app.models.product import Product
from sqlalchemy.ext.asyncio import AsyncSession


SAMPLE_PRODUCTS = [
    {"name": "Laptop Pro 15", "price": 1299.99},
    {"name": "Wireless Mouse", "price": 29.99},
    {"name": "Mechanical Keyboard", "price": 89.99},
    {"name": "USB-C Hub", "price": 49.99},
    {"name": "External SSD 1TB", "price": 129.99},
    {"name": '4K Monitor 27"', "price": 399.99},
    {"name": "Webcam HD", "price": 79.99},
    {"name": "Noise-Cancelling Headphones", "price": 249.99},
    {"name": "Laptop Stand", "price": 39.99},
    {"name": "USB Cable 3-Pack", "price": 14.99},
    {"name": "Phone Case", "price": 19.99},
    {"name": "Screen Protector", "price": 9.99},
    {"name": "Bluetooth Speaker", "price": 59.99},
    {"name": "Smart Watch", "price": 299.99},
    {"name": "Fitness Tracker", "price": 99.99},
    {"name": "Portable Charger", "price": 34.99},
    {"name": "Phone Stand", "price": 15.99},
    {"name": "Cable Organizer", "price": 12.99},
    {"name": "Desk Lamp LED", "price": 44.99},
    {"name": "Ergonomic Chair", "price": 349.99},
]


async def seed_products():
    """Seed the database with sample products."""
    async with AsyncSession(engine) as session:
        # Check if products already exist
        result = await session.execute(select(Product))
        existing_products = result.scalars().all()

        if existing_products:
            print(
                f"✓ Database already has {len(existing_products)} products. Skipping seed."
            )
            return

        # Add sample products
        products = [Product(**product_data) for product_data in SAMPLE_PRODUCTS]
        session.add_all(products)
        await session.commit()

        print(f"✓ Successfully seeded {len(SAMPLE_PRODUCTS)} products!")

        # Display seeded products
        for product in products:
            print(f"  - {product.name}: ${product.price}")


async def main():
    """Main function to run seeding."""
    print("Starting database seeding...")

    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed products
    await seed_products()

    print("\n✓ Seeding complete!")


if __name__ == "__main__":
    asyncio.run(main())
