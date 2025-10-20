"use client";

import React from "react";
import { ShoppingCart, Plus, Minus } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import type { Product } from "@/types";

interface ProductCardProps {
  product: Product;
  onAddToCart?: (product: Product) => void;
  cartQuantity?: number;
  onUpdateQuantity?: (product: Product, quantity: number) => void;
  className?: string;
}

export function ProductCard({
  product,
  onAddToCart,
  cartQuantity = 0,
  onUpdateQuantity,
  className,
}: ProductCardProps) {
  const handleAddToCart = () => {
    onAddToCart?.(product);
  };

  const handleIncrement = () => {
    onUpdateQuantity?.(product, cartQuantity + 1);
  };

  const handleDecrement = () => {
    if (cartQuantity > 0) {
      onUpdateQuantity?.(product, cartQuantity - 1);
    }
  };

  const formattedPrice = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(product.price);

  const formattedDate = new Date(product.created_at).toLocaleDateString(
    "en-US",
    {
      year: "numeric",
      month: "short",
      day: "numeric",
    }
  );

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <CardTitle className="line-clamp-2">{product.name}</CardTitle>
            <CardDescription className="mt-1">
              Added {formattedDate}
            </CardDescription>
          </div>
          <Badge variant="secondary" className="shrink-0">
            {formattedPrice}
          </Badge>
        </div>
      </CardHeader>

      <CardContent>
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Product ID:</span>
            <span className="font-mono">#{product.id}</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Price:</span>
            <span className="font-semibold">{formattedPrice}</span>
          </div>
        </div>
      </CardContent>

      <CardFooter>
        {cartQuantity > 0 ? (
          <div className="flex w-full items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={handleDecrement}
                aria-label="Decrease quantity"
              >
                <Minus className="h-4 w-4" />
              </Button>
              <span className="min-w-[2rem] text-center font-semibold">
                {cartQuantity}
              </span>
              <Button
                size="sm"
                variant="outline"
                onClick={handleIncrement}
                aria-label="Increase quantity"
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            <span className="text-sm text-muted-foreground">In Cart</span>
          </div>
        ) : (
          <Button
            className="w-full"
            onClick={handleAddToCart}
            disabled={!onAddToCart}
          >
            <ShoppingCart className="mr-2 h-4 w-4" />
            Add to Cart
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}

// Compact variant for smaller cards
export function ProductCardCompact({
  product,
  onAddToCart,
  className,
}: Omit<ProductCardProps, "cartQuantity" | "onUpdateQuantity">) {
  const formattedPrice = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(product.price);

  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <CardTitle className="line-clamp-1 text-base">{product.name}</CardTitle>
        <CardDescription>{formattedPrice}</CardDescription>
      </CardHeader>
      <CardFooter className="pt-0">
        <Button
          size="sm"
          className="w-full"
          onClick={() => onAddToCart?.(product)}
          disabled={!onAddToCart}
        >
          <ShoppingCart className="mr-2 h-3 w-3" />
          Add
        </Button>
      </CardFooter>
    </Card>
  );
}

// Skeleton loading state
export function ProductCardSkeleton() {
  return (
    <Card>
      <CardHeader>
        <div className="space-y-2">
          <div className="h-5 w-3/4 animate-pulse rounded bg-muted" />
          <div className="h-4 w-1/2 animate-pulse rounded bg-muted" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="h-4 w-full animate-pulse rounded bg-muted" />
          <div className="h-4 w-2/3 animate-pulse rounded bg-muted" />
        </div>
      </CardContent>
      <CardFooter>
        <div className="h-10 w-full animate-pulse rounded bg-muted" />
      </CardFooter>
    </Card>
  );
}
