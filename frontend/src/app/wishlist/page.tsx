"use client";

import { useState } from "react";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Heart, ShoppingCart, X, Share2, AlertCircle } from "lucide-react";
import { toast } from "sonner";

// Mock wishlist data
const mockWishlistItems = [
  {
    id: 1,
    name: "Wireless Headphones Pro",
    price: 299.99,
    originalPrice: 399.99,
    image: "https://via.placeholder.com/300x300?text=Headphones",
    inStock: true,
    discount: 25,
  },
  {
    id: 2,
    name: "Smart Watch Series X",
    price: 449.99,
    originalPrice: null,
    image: "https://via.placeholder.com/300x300?text=Smart+Watch",
    inStock: true,
    discount: 0,
  },
  {
    id: 3,
    name: "Premium Laptop Backpack",
    price: 79.99,
    originalPrice: 99.99,
    image: "https://via.placeholder.com/300x300?text=Backpack",
    inStock: false,
    discount: 20,
  },
];

export default function WishlistPage() {
  const [wishlistItems, setWishlistItems] = useState(mockWishlistItems);

  const handleRemoveItem = (id: number) => {
    setWishlistItems(wishlistItems.filter((item) => item.id !== id));
    toast.success("Item removed from wishlist");
  };

  const handleAddToCart = (item: typeof mockWishlistItems[0]) => {
    if (!item.inStock) {
      toast.error("This item is currently out of stock");
      return;
    }
    toast.success(`${item.name} added to cart`);
  };

  const handleShareWishlist = () => {
    toast.success("Wishlist link copied to clipboard!");
  };

  if (wishlistItems.length === 0) {
    return (
      <div className="py-16 text-center">
        <Heart className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
        <h1 className="text-2xl font-bold mb-2">Your Wishlist is Empty</h1>
        <p className="text-muted-foreground mb-6 max-w-md mx-auto">
          Save items you love to your wishlist and we&apos;ll notify you when they go
          on sale!
        </p>
        <Button asChild>
          <Link href="/products">Start Shopping</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">My Wishlist</h1>
          <p className="text-muted-foreground">
            {wishlistItems.length} {wishlistItems.length === 1 ? "item" : "items"} saved
          </p>
        </div>
        <Button variant="outline" onClick={handleShareWishlist}>
          <Share2 className="h-4 w-4 mr-2" />
          Share Wishlist
        </Button>
      </div>

      {/* Wishlist Items */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {wishlistItems.map((item) => (
          <Card key={item.id} className="group relative overflow-hidden">
            <button
              onClick={() => handleRemoveItem(item.id)}
              className="absolute top-2 right-2 z-10 h-8 w-8 rounded-full bg-background/80 backdrop-blur-sm hover:bg-background transition-colors flex items-center justify-center group/btn"
              aria-label="Remove from wishlist"
            >
              <X className="h-4 w-4 group-hover/btn:text-destructive transition-colors" />
            </button>

            {item.discount > 0 && (
              <Badge className="absolute top-2 left-2 z-10" variant="destructive">
                {item.discount}% OFF
              </Badge>
            )}

            {!item.inStock && (
              <div className="absolute inset-0 bg-background/80 backdrop-blur-sm z-10 flex items-center justify-center">
                <div className="text-center">
                  <AlertCircle className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                  <p className="font-medium">Out of Stock</p>
                  <p className="text-sm text-muted-foreground">
                    We&apos;ll notify you when available
                  </p>
                </div>
              </div>
            )}

            <Link href={`/products/${item.id}`}>
              <div className="aspect-square bg-muted overflow-hidden">
                <img
                  src={item.image}
                  alt={item.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
              </div>
            </Link>

            <CardContent className="p-4">
              <Link href={`/products/${item.id}`}>
                <h3 className="font-semibold mb-2 line-clamp-2 hover:text-primary transition-colors">
                  {item.name}
                </h3>
              </Link>

              <div className="flex items-baseline gap-2 mb-4">
                <span className="text-lg font-bold">${item.price}</span>
                {item.originalPrice && (
                  <span className="text-sm text-muted-foreground line-through">
                    ${item.originalPrice}
                  </span>
                )}
              </div>

              <Button
                className="w-full"
                onClick={() => handleAddToCart(item)}
                disabled={!item.inStock}
              >
                <ShoppingCart className="h-4 w-4 mr-2" />
                {item.inStock ? "Add to Cart" : "Out of Stock"}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Info Card */}
      <Card className="mt-8 bg-muted/50">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <Heart className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold mb-1">Never Miss a Deal</h3>
              <p className="text-sm text-muted-foreground">
                Items in your wishlist are tracked automatically. We&apos;ll send you
                notifications when they go on sale or come back in stock. You can
                also share your wishlist with friends and family!
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
