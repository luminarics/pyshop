import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ShoppingBag, Shield, Truck, CreditCard } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="py-20 px-4 bg-gradient-to-b from-primary/10 to-background">
        <div className="container mx-auto max-w-6xl text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            Welcome to PyShop
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-3xl mx-auto">
            Your trusted e-commerce platform for quality products at competitive prices
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" className="text-lg">
              <Link href="/register">Get Started</Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="text-lg">
              <Link href="/login">Login</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 px-4">
        <div className="container mx-auto max-w-6xl">
          <h2 className="text-3xl font-bold text-center mb-12">Why Choose PyShop?</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader>
                <ShoppingBag className="h-10 w-10 mb-2 text-primary" />
                <CardTitle>Wide Selection</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Browse thousands of quality products across multiple categories
                </CardDescription>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Shield className="h-10 w-10 mb-2 text-primary" />
                <CardTitle>Secure Shopping</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Your data is protected with enterprise-grade security
                </CardDescription>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Truck className="h-10 w-10 mb-2 text-primary" />
                <CardTitle>Fast Delivery</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Quick and reliable shipping to your doorstep
                </CardDescription>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CreditCard className="h-10 w-10 mb-2 text-primary" />
                <CardTitle>Easy Payments</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Multiple payment options for your convenience
                </CardDescription>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 px-4 bg-primary/5">
        <div className="container mx-auto max-w-4xl text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Start Shopping?</h2>
          <p className="text-lg text-muted-foreground mb-8">
            Create an account today and enjoy exclusive deals and personalized recommendations
          </p>
          <Button asChild size="lg">
            <Link href="/register">Create Your Account</Link>
          </Button>
        </div>
      </section>
    </div>
  );
}
