import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Clock, Percent, Star, TrendingUp, Zap } from "lucide-react";

const featuredDeals = [
  {
    id: 1,
    title: "Flash Sale: Electronics",
    description: "Up to 50% off on selected electronics. Limited time offer!",
    discount: "50% OFF",
    endsIn: "2 hours",
    icon: Zap,
    color: "text-yellow-500",
  },
  {
    id: 2,
    title: "Seasonal Clearance",
    description: "End of season sale on clothing and accessories",
    discount: "30-70% OFF",
    endsIn: "3 days",
    icon: Percent,
    color: "text-blue-500",
  },
  {
    id: 3,
    title: "Best Sellers",
    description: "Special prices on our most popular items",
    discount: "25% OFF",
    endsIn: "1 week",
    icon: Star,
    color: "text-purple-500",
  },
  {
    id: 4,
    title: "Daily Deals",
    description: "New deals every day! Check back for more",
    discount: "Up to 40% OFF",
    endsIn: "24 hours",
    icon: TrendingUp,
    color: "text-green-500",
  },
];

const dealCategories = [
  { name: "Electronics", discount: "Up to 50%", count: 156 },
  { name: "Fashion", discount: "Up to 40%", count: 234 },
  { name: "Home & Garden", discount: "Up to 35%", count: 89 },
  { name: "Sports", discount: "Up to 30%", count: 67 },
  { name: "Books", discount: "Up to 25%", count: 145 },
  { name: "Gaming", discount: "Up to 45%", count: 78 },
];

export default function DealsPage() {
  return (
    <div className="py-8">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-primary/10 via-primary/5 to-background rounded-lg p-8 mb-8">
        <div className="max-w-3xl">
          <h1 className="text-4xl font-bold mb-2">Hot Deals & Special Offers</h1>
          <p className="text-lg text-muted-foreground mb-4">
            Save big on your favorite products. New deals added daily!
          </p>
          <Button size="lg">
            Browse All Deals
          </Button>
        </div>
      </div>

      {/* Featured Deals */}
      <div className="mb-12">
        <h2 className="text-2xl font-bold mb-6">Featured Deals</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {featuredDeals.map((deal) => {
            const Icon = deal.icon;
            return (
              <Card key={deal.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <Icon className={`h-8 w-8 ${deal.color}`} />
                    <Badge variant="destructive" className="font-bold">
                      {deal.discount}
                    </Badge>
                  </div>
                  <CardTitle className="text-lg mt-4">{deal.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="mb-4">
                    {deal.description}
                  </CardDescription>
                  <div className="flex items-center text-sm text-muted-foreground">
                    <Clock className="h-4 w-4 mr-1" />
                    Ends in {deal.endsIn}
                  </div>
                  <Button className="w-full mt-4" variant="outline">
                    Shop Now
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Deal Categories */}
      <div className="mb-12">
        <h2 className="text-2xl font-bold mb-6">Deals by Category</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {dealCategories.map((category) => (
            <Link key={category.name} href={`/products?category=${category.name.toLowerCase()}&deals=true`}>
              <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{category.name}</CardTitle>
                    <Badge variant="secondary">{category.discount}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    {category.count} products on sale
                  </p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>

      {/* Tips Section */}
      <Card className="bg-muted/50">
        <CardHeader>
          <CardTitle>Deal Hunting Tips</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="flex items-start gap-2">
            <div className="h-6 w-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
              <span className="text-sm font-bold text-primary">1</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Check back daily for new flash deals and limited-time offers
            </p>
          </div>
          <div className="flex items-start gap-2">
            <div className="h-6 w-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
              <span className="text-sm font-bold text-primary">2</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Sign up for our newsletter to get exclusive early access to deals
            </p>
          </div>
          <div className="flex items-start gap-2">
            <div className="h-6 w-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
              <span className="text-sm font-bold text-primary">3</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Add items to your wishlist to get notified when they go on sale
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
