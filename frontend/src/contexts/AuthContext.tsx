"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { onAuthStateChanged, User as FirebaseUser } from "firebase/auth";
import { auth } from "@/lib/firebase-auth";

interface UserWithClaims {
  uid: string;
  email: string | null;
  role: string;
  tenantId: string;
}

interface AuthContextType {
  user: UserWithClaims | null;
  loading: boolean;
  firebaseUser: FirebaseUser | null;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  firebaseUser: null,
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserWithClaims | null>(null);
  const [firebaseUser, setFirebaseUser] = useState<FirebaseUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        try {
          // Get the ID token result which contains custom claims
          const idTokenResult = await firebaseUser.getIdTokenResult();

          // Extract custom claims
          const role = (idTokenResult.claims.role as string) || "user";
          const tenantId = (idTokenResult.claims.tenantId as string) || "default";

          setUser({
            uid: firebaseUser.uid,
            email: firebaseUser.email,
            role,
            tenantId,
          });
          setFirebaseUser(firebaseUser);
        } catch (error) {
          console.error("Error fetching custom claims:", error);
          setUser(null);
          setFirebaseUser(null);
        }
      } else {
        setUser(null);
        setFirebaseUser(null);
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, firebaseUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
