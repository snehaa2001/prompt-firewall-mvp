import { signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut, onAuthStateChanged } from 'firebase/auth';
import { auth as firebaseAuth } from './firebase';

export const auth = firebaseAuth;

export async function loginWithEmail(email: string, password: string) {
  if (!auth) throw new Error('Firebase auth is not initialized');
  const userCredential = await signInWithEmailAndPassword(auth, email, password);
  const idToken = await userCredential.user.getIdToken();
  localStorage.setItem('firebase_token', idToken);
  return idToken;
}

export async function signupWithEmail(email: string, password: string) {
  if (!auth) throw new Error('Firebase auth is not initialized');
  const userCredential = await createUserWithEmailAndPassword(auth, email, password);
  const idToken = await userCredential.user.getIdToken();
  localStorage.setItem('firebase_token', idToken);
  return idToken;
}

export async function logout() {
  if (!auth) throw new Error('Firebase auth is not initialized');
  await signOut(auth);
  localStorage.removeItem('firebase_token');
}

export function getCurrentToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('firebase_token');
}

if (typeof window !== 'undefined' && auth) {
  onAuthStateChanged(auth, async (user) => {
    if (user) {
      const token = await user.getIdToken(true);
      localStorage.setItem('firebase_token', token);
    }
  });
}
