-- Seed products for PyShop
-- Run with: docker compose exec db psql -U app -d fastapi -f /tmp/seed_products.sql

-- Featured Products
INSERT INTO product (name, price, category, description, stock, created_at) VALUES
('Premium Wireless Headphones', 299.99, 'featured', 'High-quality wireless headphones with active noise cancellation and 30-hour battery life', 50, NOW()),
('Smart Watch Pro', 399.99, 'featured', 'Advanced fitness tracking, heart rate monitoring, and smartphone notifications', 75, NOW()),
('4K Ultra HD Camera', 1299.99, 'featured', 'Professional mirrorless camera with 45MP sensor and 8K video recording', 25, NOW()),
('Designer Leather Jacket', 449.99, 'featured', 'Genuine leather jacket with premium craftsmanship and timeless design', 40, NOW()),
('Portable SSD 2TB', 179.99, 'featured', 'Ultra-fast portable storage with USB-C connectivity and 2000MB/s speeds', 100, NOW());

-- Electronics
INSERT INTO product (name, price, category, description, stock, created_at) VALUES
('Laptop 15.6-inch i7', 1099.99, 'electronics', 'Powerful laptop with Intel i7, 16GB RAM, and 512GB SSD', 45, NOW()),
('Tablet 10-inch', 329.99, 'electronics', 'Slim tablet with crisp display and all-day battery life', 60, NOW()),
('Smartphone 5G 128GB', 799.99, 'electronics', 'Latest 5G smartphone with triple camera system', 55, NOW()),
('27-inch 4K Monitor', 449.99, 'electronics', 'Professional 4K monitor with IPS panel and HDR support', 40, NOW()),
('Wireless Earbuds Pro', 199.99, 'electronics', 'True wireless earbuds with active noise cancellation', 100, NOW());

-- Clothing
INSERT INTO product (name, price, category, description, stock, created_at) VALUES
('Classic White T-Shirt', 24.99, 'clothing', '100% cotton premium white t-shirt with comfortable fit', 200, NOW()),
('Slim Fit Jeans', 79.99, 'clothing', 'Classic blue denim jeans with modern slim fit', 150, NOW()),
('Hoodie Premium Cotton', 59.99, 'clothing', 'Comfortable hoodie with kangaroo pocket and drawstring hood', 120, NOW()),
('Running Shoes Athletic', 119.99, 'clothing', 'Lightweight running shoes with cushioned sole', 90, NOW()),
('Dress Shirt Formal', 69.99, 'clothing', 'Elegant dress shirt perfect for business occasions', 80, NOW());
