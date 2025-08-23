import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowRight, Shield, Clock, BarChart3, FileText, Users, CheckCircle, Zap, Award, TrendingUp } from "lucide-react";
import Link from "next/link";
import Image from "next/image";
import deedDemoImage from "@/assets/deed-demo-image.jpg";
import { Navigation } from '@/components/Navigation';

const features = [
  {
    icon: Zap,
    title: "AI-Powered Analysis",
    description: "Advanced machine learning algorithms process Index II documents with 99.9% accuracy in seconds",
    color: "text-yellow-500",
    gradient: "from-yellow-400 to-orange-500",
  },
  {
    icon: Clock,
    title: "Real-Time Processing", 
    description: "Instant chronological visualization of property history with interactive timeline generation",
    color: "text-blue-500",
    gradient: "from-blue-400 to-cyan-500",
  },
  {
    icon: Shield,
    title: "Advanced Risk Detection",
    description: "Comprehensive legal risk analysis with predictive insights and compliance monitoring",
    color: "text-green-500",
    gradient: "from-green-400 to-emerald-500",
  },
  {
    icon: Award,
    title: "Professional Reports",
    description: "Generate court-ready documentation with automated compliance verification and audit trails",
    color: "text-purple-500",
    gradient: "from-purple-400 to-pink-500",
  },
];

const benefits = [
  "Reduce document review time by 85% with AI automation",
  "Identify potential legal issues before they become problems",
  "Generate professional reports with one-click compliance",
  "Track portfolio-wide risk metrics in real-time",
  "Ensure regulatory compliance with automatic updates",
  "Access 24/7 cloud-based analysis from anywhere",
];

export default function Home() {
  return (
    <main className="space-y-0">
      {/* Hero Section */}
      <section className="relative py-24 lg:py-32 overflow-hidden">
        {/* Background with modern gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900"></div>
        
        {/* Floating elements - using a placeholder for now */}
        <div className="absolute inset-0 opacity-10">
          <div className="w-full h-full bg-gradient-to-br from-cyan-400 to-blue-500"></div>
        </div>
        
        <div className="relative container mx-auto px-6">
          <div className="max-w-5xl mx-auto text-center text-white space-y-10">
            <div className="space-y-6">
              <Badge variant="outline" className="border-white/20 text-white hover:bg-white/10 rounded-full px-6 py-2 backdrop-blur-sm text-lg">
                <TrendingUp className="w-4 h-4 mr-2" />
                  Revolutionary Legal Tech Platform
              </Badge>
              
              <h1 className="text-5xl lg:text-7xl font-bold leading-tight">
                Transform Property Legal
                <span className="block bg-gradient-to-r from-cyan-300 to-blue-300 bg-clip-text text-transparent">
                  Analysis Forever
                </span>
              </h1>
              
              <p className="text-xl lg:text-2xl text-white/90 max-w-4xl mx-auto leading-relaxed">
                Revolutionary AI-powered platform that automates property legal documentation analysis, 
                generates comprehensive timelines, and delivers actionable risk insights in minutes, not days.
              </p>
            </div>
            
            <div className="flex items-center justify-center pt-6">
              <Button
                asChild
                size="lg"
                className="bg-white text-blue-900 hover:bg-white/90 shadow-lg rounded-xl px-12 py-6 text-xl font-semibold"
              >
                <Link href="/upload" className="flex items-center">
                  Upload your document
                  <ArrowRight className="w-6 h-6 ml-3" />
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 gradient-card">
        <div className="container mx-auto px-6">
          <div className="max-w-7xl mx-auto">
            <div className="text-center space-y-6 mb-20">
              <Badge variant="outline" className="text-lg rounded-full px-4 py-2 text-primary border-primary/20">
                Advanced Technology
              </Badge>
              <h2 className="text-4xl lg:text-5xl font-bold text-foreground">
                Next-Generation Legal Technology
              </h2>
              <p className="text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
                Experience the future of property legal analysis with our comprehensive AI-powered platform 
                that delivers unprecedented speed, accuracy, and insights.
              </p>
            </div>

            <div className="grid lg:grid-cols-2 xl:grid-cols-4 gap-8">
              {features.map((feature, index) => {
                const Icon = feature.icon;
                return (
                  <Card key={index} className="floating-card shadow-medium rounded-2xl overflow-hidden">
                    <CardContent className="p-8 text-center space-y-6">
                      <div className={`w-16 h-16 mx-auto rounded-2xl bg-gradient-to-r ${feature.gradient} shadow-large flex items-center justify-center`}>
                        <Icon className="w-8 h-8 text-white" />
                      </div>
                      <div className="space-y-3">
                        <h3 className="text-xl font-bold text-foreground">
                          {feature.title}
                        </h3>
                        <p className="text-muted-foreground leading-relaxed">
                          {feature.description}
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-24 bg-blue-50/50">
        <div className="container mx-auto px-6">
          <div className="max-w-7xl mx-auto">
            <div className="grid lg:grid-cols-2 gap-16 items-center">
              <div className="space-y-10">
                <div className="space-y-6">
                  <Badge variant="outline" className="rounded-full px-6 py-3 text-lg text-blue-600 border-blue-600/20">
                    Professional Results
                  </Badge>
                  <h2 className="text-4xl lg:text-5xl font-bold text-gray-900">
                    Revolutionize Your 
                    <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent block">
                      Legal Workflow
                    </span>
                  </h2>
                  <p className="text-xl text-gray-600 leading-relaxed">
                    Join the legal technology revolution. Our platform has transformed how hundreds 
                    of legal professionals handle property analysis, delivering results that exceed expectations.
                  </p>
                </div>
                
                <div className="grid gap-4">
                  {benefits.map((benefit, index) => (
                    <div key={index} className="flex items-start space-x-4 p-4 rounded-xl bg-white/70 shadow-sm">
                      <CheckCircle className="w-6 h-6 text-green-500 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-900 font-medium">{benefit}</span>
                    </div>
                  ))}
                </div>
                
                <div className="flex items-center space-x-6 pt-6">
                  <Button asChild size="lg" className="rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg hover:shadow-xl px-10 py-5 text-xl font-semibold">
                    <Link href="/upload">
                      Get Started Now
                      <ArrowRight className="w-6 h-6 ml-3" />
                    </Link>
                  </Button>
                  <Button variant="outline" size="lg" asChild className="rounded-xl px-10 py-6 text-xl font-semibold">
                    <Link href="/dashboard">Explore Dashboard</Link>
                  </Button>
                </div>
              </div>
              
              <div className="space-y-8">
                <div className="relative">
                  <div className="w-full h-96 rounded-2xl overflow-hidden shadow-xl">
                    <Image
                      src={deedDemoImage}
                      alt="AI-powered legal document analysis"
                      width={600}
                      height={400}
                      className="w-full h-full object-cover"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-r from-blue-600 to-purple-600 relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="w-full h-full bg-gradient-to-br from-blue-400 to-purple-500"></div>
        </div>
        <div className="relative container mx-auto px-6 text-center">
          <div className="max-w-4xl mx-auto space-y-10 text-white">
            <div className="space-y-6">
              <h2 className="text-4xl lg:text-6xl font-bold">
                Ready to Experience the Future?
              </h2>
              <p className="text-xl lg:text-2xl text-white/90 leading-relaxed">
                Join thousands of legal professionals who've already transformed their practice 
                with PropertyLegal Pro. Start your free analysis today.
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-6">
              <Button
                asChild
                size="lg"
                className="bg-white text-blue-600 hover:bg-white/90 shadow-lg rounded-xl px-10 py-6 text-lg font-semibold"
              >
                <Link href="/upload">
                  Upload Your First Document
                  <FileText className="w-5 h-5 ml-2" />
                </Link>
              </Button>
            </div>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-8 text-sm text-gray-200">
              <span>© 2024 PropertyLegal Pro. All rights reserved.</span>
              <span>•</span>
              <span>Privacy Policy</span>
              <span>•</span>
              <span>Terms of Service</span>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
