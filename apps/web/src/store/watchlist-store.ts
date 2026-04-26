"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

interface WatchlistState {
  symbols: string[];
  toggle: (symbol: string) => void;
  has: (symbol: string) => boolean;
}

export const useWatchlistStore = create<WatchlistState>()(
  persist(
    (set, get) => ({
      symbols: [],
      toggle: (symbol) =>
        set((state) => ({
          symbols: state.symbols.includes(symbol)
            ? state.symbols.filter((item) => item !== symbol)
            : [...state.symbols, symbol],
        })),
      has: (symbol) => get().symbols.includes(symbol),
    }),
    {
      name: "winlong-watchlist",
    },
  ),
);
