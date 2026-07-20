import { create } from "zustand";

// TODO: implement. Holds client-side auth/session state only — the backend
// (auth module) owns actual authentication.
interface AuthState {
  user: { id: string; email: string } | null;
  setUser: (user: AuthState["user"]) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
  logout: () => set({ user: null }),
}));
