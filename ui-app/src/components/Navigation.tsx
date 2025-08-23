'use client';

import { Button } from "@/components/ui/button";
import { FileText, Clock, BarChart3, Upload, User, LogOut, LogIn, UserPlus } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import LogoutButton from './LogoutButton';
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export function Navigation() {
  const pathname = usePathname();
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const navItems = [
    { path: "/", label: "Home", icon: FileText },
    ...(isAuthenticated ? [
      { path: "/upload", label: "Upload", icon: Upload },
      { path: "/dashboard", label: "Dashboard", icon: BarChart3 },
    ] : []),
  ];

  // Don't render navigation until mounted and auth state is determined
  if (!mounted || isLoading) {
    return (
      <nav className="border-b bg-card/80 backdrop-blur-xl shadow-soft sticky top-0 z-50">
        <div className="container mx-auto px-6">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-8">
              <Link href="/" className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Zamindaar
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 rounded-full bg-gray-200 animate-pulse"></div>
            </div>
          </div>
        </div>
      </nav>
    );
  }

  return (
    <nav className="border-b bg-card/80 backdrop-blur-xl shadow-soft sticky top-0 z-50">
      <div className="container mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link href="/" className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Zamindaar
            </Link>
            <div className="hidden md:flex space-x-2">
              {navItems.map(({ path, label, icon: Icon }) => (
                <Button
                  key={path}
                  variant={pathname === path ? "default" : "ghost"}
                  size="lg"
                  onClick={() => router.push(path)}
                  className={`
                    transition-all duration-300 rounded-xl
                    ${pathname === path 
                      ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg" 
                      : "hover:bg-accent/50"
                    }
                  `}
                >
                  <Icon className="w-4 h-4" />
                  <span className="font-medium">{label}</span>
                </Button>
              ))}
            </div>
          </div>
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <div className="flex items-center space-x-4">
                <div className="hidden sm:block text-right">
                  <p className="text-sm font-medium text-foreground">
                    {user?.fullName}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {user?.email}
                  </p>
                </div>
                <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg flex items-center justify-center">
                  <span className="text-white text-sm font-semibold">
                    {user?.fullName?.split(' ').map(n => n[0]).join('')}
                  </span>
                </div>
                <LogoutButton />
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Button
                  variant={pathname === '/signin' ? "default" : "ghost"}
                  size="sm"
                  onClick={() => router.push('/signin')}
                  className={`
                    ${pathname === '/signin' 
                      ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg" 
                      : ""
                    }
                  `}
                >
                  <LogIn className="w-4 h-4" />
                  <span className="hidden sm:inline">Sign In</span>
                </Button>
                <Button
                  variant={pathname === '/signup' ? "default" : "ghost"}
                  size="sm"
                  onClick={() => router.push('/signup')}
                  className={`
                    ${pathname === '/signup' 
                      ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg" 
                      : ""
                    }
                  `}
                >
                  <UserPlus className="w-4 h-4" />
                  <span className="hidden sm:inline">Sign Up</span>
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
} 
