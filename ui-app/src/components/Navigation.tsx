'use client';

import { Button } from "@/components/ui/button";
import { FileText, Clock, BarChart3, Upload } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

export function Navigation() {
  const pathname = usePathname();

  const navItems = [
    { path: "/", label: "Home", icon: FileText },
    { path: "/upload", label: "Upload", icon: Upload },
    { path: "/dashboard", label: "Dashboard", icon: BarChart3 },
  ];

  return (
    <nav className="border-b bg-card/80 backdrop-blur-xl shadow-soft sticky top-0 z-50">
      <div className="container mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link href="/" className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              PropertyLegal 
            </Link>
            <div className="hidden md:flex space-x-2">
              {navItems.map(({ path, label, icon: Icon }) => (
                <Button
                  key={path}
                  variant={pathname === path ? "default" : "ghost"}
                  size="sm"
                  asChild
                  className={`
                    transition-all duration-300 rounded-xl
                    ${pathname === path 
                      ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg" 
                      : "hover:bg-accent/50"
                    }
                  `}
                >
                  <Link href={path} className="flex items-center space-x-2">
                    <Icon className="w-4 h-4" />
                    <span className="font-medium">{label}</span>
                  </Link>
                </Button>
              ))}
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-medium text-foreground">Sarah Thompson</p>
                <p className="text-xs text-muted-foreground">Senior Legal Analyst</p>
              </div>
              <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg flex items-center justify-center">
                <span className="text-white text-sm font-semibold">ST</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
} 
