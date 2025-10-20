"use client";

import React, { useState, useMemo } from "react";
import { Search, SlidersHorizontal, X } from "lucide-react";
import { ProductGrid as Grid } from "@/components/ui/responsive-grid";
import { ProductCard, ProductCardSkeleton } from "./ProductCard";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import type { Product } from "@/types";

interface ProductGridLayoutProps {
  products: Product[];
  isLoading?: boolean;
  onAddToCart?: (product: Product) => void;
  cartItems?: Map<number, number>; // productId -> quantity
  onUpdateQuantity?: (product: Product, quantity: number) => void;
  showSearch?: boolean;
  showSort?: boolean;
  showFilters?: boolean;
  emptyMessage?: string;
  className?: string;
}

type SortOption = "name-asc" | "name-desc" | "price-asc" | "price-desc" | "date-new" | "date-old";

export function ProductGridLayout({
  products,
  isLoading = false,
  onAddToCart,
  cartItems = new Map(),
  onUpdateQuantity,
  showSearch = true,
  showSort = true,
  showFilters = true,
  emptyMessage = "No products found",
  className,
}: ProductGridLayoutProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState<SortOption>("date-new");
  const [priceFilter, setPriceFilter] = useState<string>("all");

  // Filter and sort products
  const filteredProducts = useMemo(() => {
    let filtered = [...products];

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (product) =>
          product.name.toLowerCase().includes(query) ||
          product.id.toString().includes(query)
      );
    }

    // Price filter
    if (priceFilter !== "all") {
      const [min, max] = priceFilter.split("-").map(Number);
      filtered = filtered.filter((product) => {
        if (max) {
          return product.price >= min && product.price <= max;
        }
        return product.price >= min;
      });
    }

    // Sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case "name-asc":
          return a.name.localeCompare(b.name);
        case "name-desc":
          return b.name.localeCompare(a.name);
        case "price-asc":
          return a.price - b.price;
        case "price-desc":
          return b.price - a.price;
        case "date-new":
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        case "date-old":
          return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
        default:
          return 0;
      }
    });

    return filtered;
  }, [products, searchQuery, sortBy, priceFilter]);

  const clearFilters = () => {
    setSearchQuery("");
    setSortBy("date-new");
    setPriceFilter("all");
  };

  const hasActiveFilters = searchQuery || sortBy !== "date-new" || priceFilter !== "all";

  return (
    <div className={className}>
      {/* Filters and Controls */}
      {(showSearch || showSort || showFilters) && (
        <div className="mb-6 space-y-4">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            {/* Search */}
            {showSearch && (
              <div className="relative flex-1 sm:max-w-md">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  type="search"
                  placeholder="Search products..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9"
                />
              </div>
            )}

            {/* Sort */}
            {showSort && (
              <div className="flex items-center gap-2">
                <Select value={sortBy} onValueChange={(value) => setSortBy(value as SortOption)}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Sort by" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="date-new">Newest First</SelectItem>
                    <SelectItem value="date-old">Oldest First</SelectItem>
                    <SelectItem value="name-asc">Name (A-Z)</SelectItem>
                    <SelectItem value="name-desc">Name (Z-A)</SelectItem>
                    <SelectItem value="price-asc">Price (Low to High)</SelectItem>
                    <SelectItem value="price-desc">Price (High to Low)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            )}
          </div>

          {/* Price Filter */}
          {showFilters && (
            <div className="flex flex-wrap items-center gap-2">
              <SlidersHorizontal className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">Price:</span>
              <div className="flex flex-wrap gap-2">
                <Badge
                  variant={priceFilter === "all" ? "default" : "outline"}
                  className="cursor-pointer"
                  onClick={() => setPriceFilter("all")}
                >
                  All
                </Badge>
                <Badge
                  variant={priceFilter === "0-25" ? "default" : "outline"}
                  className="cursor-pointer"
                  onClick={() => setPriceFilter("0-25")}
                >
                  Under $25
                </Badge>
                <Badge
                  variant={priceFilter === "25-50" ? "default" : "outline"}
                  className="cursor-pointer"
                  onClick={() => setPriceFilter("25-50")}
                >
                  $25 - $50
                </Badge>
                <Badge
                  variant={priceFilter === "50-100" ? "default" : "outline"}
                  className="cursor-pointer"
                  onClick={() => setPriceFilter("50-100")}
                >
                  $50 - $100
                </Badge>
                <Badge
                  variant={priceFilter === "100" ? "default" : "outline"}
                  className="cursor-pointer"
                  onClick={() => setPriceFilter("100")}
                >
                  Over $100
                </Badge>
              </div>
              {hasActiveFilters && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearFilters}
                  className="ml-auto"
                >
                  <X className="mr-1 h-3 w-3" />
                  Clear Filters
                </Button>
              )}
            </div>
          )}

          {/* Results Count */}
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>
              Showing {filteredProducts.length} of {products.length} products
            </span>
          </div>
        </div>
      )}

      {/* Product Grid */}
      {isLoading ? (
        <Grid>
          {Array.from({ length: 8 }).map((_, i) => (
            <ProductCardSkeleton key={i} />
          ))}
        </Grid>
      ) : filteredProducts.length > 0 ? (
        <Grid>
          {filteredProducts.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              onAddToCart={onAddToCart}
              cartQuantity={cartItems.get(product.id) || 0}
              onUpdateQuantity={onUpdateQuantity}
            />
          ))}
        </Grid>
      ) : (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="rounded-full bg-muted p-6">
            <Search className="h-8 w-8 text-muted-foreground" />
          </div>
          <h3 className="mt-4 text-lg font-semibold">No products found</h3>
          <p className="mt-2 text-sm text-muted-foreground">{emptyMessage}</p>
          {hasActiveFilters && (
            <Button variant="outline" className="mt-4" onClick={clearFilters}>
              Clear all filters
            </Button>
          )}
        </div>
      )}
    </div>
  );
}

// Simple grid without filters (for smaller lists)
export function SimpleProductGrid({
  products,
  isLoading = false,
  onAddToCart,
  className,
}: Pick<ProductGridLayoutProps, "products" | "isLoading" | "onAddToCart" | "className">) {
  if (isLoading) {
    return (
      <Grid className={className}>
        {Array.from({ length: 4 }).map((_, i) => (
          <ProductCardSkeleton key={i} />
        ))}
      </Grid>
    );
  }

  return (
    <Grid className={className}>
      {products.map((product) => (
        <ProductCard
          key={product.id}
          product={product}
          onAddToCart={onAddToCart}
        />
      ))}
    </Grid>
  );
}
