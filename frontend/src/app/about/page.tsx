import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Users, Target, Award, Heart, Shield, TrendingUp } from "lucide-react";

const stats = [
  { label: "Active Users", value: "50K+", icon: Users },
  { label: "Products Listed", value: "100K+", icon: TrendingUp },
  { label: "Orders Delivered", value: "200K+", icon: Award },
  { label: "Customer Satisfaction", value: "98%", icon: Heart },
];

const values = [
  {
    title: "Customer First",
    description: "We prioritize customer satisfaction in everything we do, ensuring a seamless shopping experience.",
    icon: Heart,
  },
  {
    title: "Quality Assurance",
    description: "Every product is carefully vetted to meet our high standards for quality and authenticity.",
    icon: Shield,
  },
  {
    title: "Innovation",
    description: "We continuously improve our platform with the latest technology to serve you better.",
    icon: TrendingUp,
  },
  {
    title: "Trust & Security",
    description: "Your data and transactions are protected with enterprise-grade security measures.",
    icon: Shield,
  },
];

const milestones = [
  { year: "2020", event: "PyShop founded with a vision to revolutionize online shopping" },
  { year: "2021", event: "Reached 10,000 active users and expanded product categories" },
  { year: "2022", event: "Launched mobile app and same-day delivery in major cities" },
  { year: "2023", event: "Opened international shipping and reached 50,000 users" },
  { year: "2024", event: "Introduced AI-powered recommendations and virtual try-on" },
];

export default function AboutPage() {
  return (
    <div className="py-8">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <Badge className="mb-4">Our Story</Badge>
        <h1 className="text-4xl md:text-5xl font-bold mb-4">
          About PyShop
        </h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          Building the future of e-commerce, one satisfied customer at a time.
          We&apos;re committed to providing quality products at competitive prices
          with exceptional service.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label}>
              <CardContent className="pt-6">
                <div className="flex flex-col items-center text-center">
                  <Icon className="h-10 w-10 text-primary mb-2" />
                  <div className="text-3xl font-bold mb-1">{stat.value}</div>
                  <div className="text-sm text-muted-foreground">{stat.label}</div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Mission */}
      <Card className="mb-12 bg-gradient-to-br from-primary/5 to-background">
        <CardHeader>
          <div className="flex items-center gap-2 mb-2">
            <Target className="h-6 w-6 text-primary" />
            <CardTitle className="text-2xl">Our Mission</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-lg leading-relaxed">
            Our mission is to make online shopping accessible, enjoyable, and trustworthy
            for everyone. We believe that shopping should be more than just a transaction
            – it should be an experience that brings joy and convenience to your life.
            Through continuous innovation and unwavering commitment to quality, we strive
            to be your trusted partner for all your shopping needs.
          </p>
        </CardContent>
      </Card>

      {/* Values */}
      <div className="mb-12">
        <h2 className="text-3xl font-bold text-center mb-8">Our Core Values</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {values.map((value) => {
            const Icon = value.icon;
            return (
              <Card key={value.title}>
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center">
                      <Icon className="h-6 w-6 text-primary" />
                    </div>
                    <CardTitle>{value.title}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">
                    {value.description}
                  </CardDescription>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Timeline */}
      <div className="mb-12">
        <h2 className="text-3xl font-bold text-center mb-8">Our Journey</h2>
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-6">
              {milestones.map((milestone, index) => (
                <div key={milestone.year} className="flex gap-6">
                  <div className="flex flex-col items-center">
                    <div className="h-10 w-10 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold flex-shrink-0">
                      {index + 1}
                    </div>
                    {index < milestones.length - 1 && (
                      <div className="w-0.5 h-full bg-border flex-grow mt-2" />
                    )}
                  </div>
                  <div className="pb-6">
                    <div className="font-bold text-lg mb-1">{milestone.year}</div>
                    <p className="text-muted-foreground">{milestone.event}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Team Section */}
      <div className="text-center">
        <h2 className="text-3xl font-bold mb-4">Join Our Team</h2>
        <p className="text-lg text-muted-foreground mb-6 max-w-2xl mx-auto">
          We&apos;re always looking for talented individuals who share our passion
          for excellence and innovation. If you&apos;re interested in joining our team,
          we&apos;d love to hear from you.
        </p>
        <a
          href="/careers"
          className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background bg-primary text-primary-foreground hover:bg-primary/90 h-10 py-2 px-4"
        >
          View Open Positions
        </a>
      </div>
    </div>
  );
}
