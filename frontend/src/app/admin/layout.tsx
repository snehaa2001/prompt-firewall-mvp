"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { auth, logout } from "@/lib/firebase-auth";
import { onAuthStateChanged } from "firebase/auth";
import Link from "next/link";
import { Shield, LayoutDashboard, FileText, Settings, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";

interface User {
  email: string | null;
  uid: string;
}

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const isLoginPage = pathname === '/admin/login';
    const isSignupPage = pathname === '/admin/signup';

    if (isLoginPage || isSignupPage) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setLoading(false);
      setUser(null);
      return;
    }

    const unsubscribe = onAuthStateChanged(auth!, (currentUser) => {
      if (currentUser) {
        setUser({
          email: currentUser.email,
          uid: currentUser.uid
        });
        setLoading(false);
      } else {
        router.push("/admin/login");
        setLoading(false);
      }
    });

    return () => unsubscribe();
  }, [router, pathname]);

  const handleSignOut = () => {
    logout();
    router.push("/admin/login");
  };

  // Show loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Shield className="w-12 h-12 text-blue-600 mx-auto mb-4 animate-pulse" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  const isPublicPage = pathname === '/admin/login' || pathname === '/admin/signup';

  if (isPublicPage) {
    return <>{children}</>;
  }

  if (!user) {
    return null;
  }

  // Render admin layout with sidebar (for authenticated users)
  return (
    <div className="flex min-h-screen bg-gray-50">
      <aside className="w-64 bg-white border-r border-gray-200">
        <div className="p-6">
          <div className="flex items-center gap-2 mb-8">
            <Shield className="w-8 h-8 text-blue-600" />
            <h1 className="text-xl font-bold text-gray-900">Prompt Firewall</h1>
          </div>

          <nav className="space-y-2">
            <Link href="/admin/dashboard">
              <Button variant="ghost" className="w-full justify-start">
                <LayoutDashboard className="w-4 h-4 mr-2" />
                Dashboard
              </Button>
            </Link>
            <Link href="/admin/logs">
              <Button variant="ghost" className="w-full justify-start">
                <FileText className="w-4 h-4 mr-2" />
                Logs
              </Button>
            </Link>
            <Link href="/admin/policies">
              <Button variant="ghost" className="w-full justify-start">
                <Settings className="w-4 h-4 mr-2" />
                Policies
              </Button>
            </Link>
          </nav>
        </div>

        <div className="absolute bottom-0 w-64 p-6 border-t border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <div className="text-sm">
              <p className="font-medium text-gray-900">{user.email || 'Admin'}</p>
              <p className="text-gray-500 text-xs">Admin</p>
            </div>
          </div>
          <Button
            variant="outline"
            className="w-full justify-start"
            onClick={handleSignOut}
          >
            <LogOut className="w-4 h-4 mr-2" />
            Sign Out
          </Button>
        </div>
      </aside>

      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  );
}
