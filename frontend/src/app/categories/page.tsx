import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Laptop,
  Shirt,
  Home as HomeIcon,
  Book,
  Dumbbell,
  Watch,
  GamepadIcon,
  HeadphonesIcon
} from "lucide-react";

const categories = [
  {
    id: "electronics",
    name: "Electronics",
    icon: Laptop,
    description: "Computers, phones, and gadgets",
    itemCount: 1234,
    href: "/products?category=electronics",
  },
  {
    id: "clothing",
    name: "Clothing & Fashion",
    icon: Shirt,
    description: "Apparel and accessories",
    itemCount: 2345,
    href: "/products?category=clothing",
  },
  {
    id: "home",
    name: "Home & Garden",
    icon: HomeIcon,
    description: "Furniture, decor, and garden supplies",
    itemCount: 890,
    href: "/products?category=home",
  },
  {
    id: "books",
    name: "Books & Media",
    icon: Book,
    description: "Books, movies, and music",
    itemCount: 3456,
    href: "/products?category=books",
  },
  {
    id: "sports",
    name: "Sports & Fitness",
    icon: Dumbbell,
    description: "Exercise equipment and sportswear",
    itemCount: 567,
    href: "/products?category=sports",
  },
  {
    id: "accessories",
    name: "Accessories",
    icon: Watch,
    description: "Watches, jewelry, and more",
    itemCount: 1890,
    href: "/products?category=accessories",
  },
  {
    id: "gaming",
    name: "Gaming",
    icon: GamepadIcon,
    description: "Video games and consoles",
    itemCount: 789,
    href: "/products?category=gaming",
  },
  {
    id: "audio",
    name: "Audio & Music",
    icon: HeadphonesIcon,
    description: "Headphones, speakers, and instruments",
    itemCount: 456,
    href: "/products?category=audio",
  },
];

export default function CategoriesPage() {
  return (
    <div className="py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Shop by Category</h1>
        <p className="text-lg text-muted-foreground">
          Browse our wide selection of products organized by category
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {categories.map((category) => {
          const Icon = category.icon;
          return (
            <Link key={category.id} href={category.href}>
              <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer group">
                <CardHeader>
                  <div className="flex items-center justify-between mb-2">
                    <Icon className="h-10 w-10 text-primary group-hover:scale-110 transition-transform" />
                    <span className="text-sm text-muted-foreground">
                      {category.itemCount.toLocaleString()} items
                    </span>
                  </div>
                  <CardTitle className="group-hover:text-primary transition-colors">
                    {category.name}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription>{category.description}</CardDescription>
                </CardContent>
              </Card>
            </Link>
          );
        })}
      </div>

      <div className="mt-12 text-center">
        <p className="text-muted-foreground mb-4">
          Can&apos;t find what you&apos;re looking for?
        </p>
        <Link
          href="/products"
          className="text-primary hover:underline font-medium"
        >
          Browse all products →
        </Link>
      </div>
    </div>
  );
}
