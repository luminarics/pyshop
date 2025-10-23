# PyShop Frontend - Remaining Work

## ✅ Already Done
- Next.js 15 + TypeScript setup
- Login/Register pages
- Products listing with pagination
- Profile page
- Protected routes
- shadcn/ui components
- TanStack Query setup

## 🔨 To Do

### 1. Shopping Cart Page
**File**: `frontend/src/app/cart/page.tsx`
- Display cart items list
- Update quantities (+/- buttons)
- Remove items
- Show cart total
- "Proceed to Checkout" button

**Backend**: Cart API already exists (`GET /cart`, `POST /cart/items`, etc.)

---

### 2. Checkout Flow
**File**: `frontend/src/app/checkout/page.tsx`
- Order review (cart items + total)
- Shipping info form (name, address, phone)
- Submit order button
- Redirect to success page

**Backend**: Need to implement `POST /orders` endpoint

---

### 3. Order Success Page
**File**: `frontend/src/app/checkout/success/page.tsx`
- Order confirmation message
- Order details display
- "Back to Products" button

---

### 4. Product Detail Page
**File**: `frontend/src/app/products/[id]/page.tsx`
- Product image
- Product name, price, description
- Add to cart button
- Back to products link

**Backend**: Already exists (`GET /products/{id}`)

---

## Backend Work Needed
- `POST /orders` endpoint to create orders
- `GET /orders` to view order history (optional)

## That's It!
Just 4 pages to complete the MVP:
1. Cart page
2. Checkout page
3. Success page
4. Product detail page

Total estimate: ~8-12 hours
