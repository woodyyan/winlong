import { beforeEach, describe, expect, it, vi } from "vitest";

import { clientFetcher, getCoinDetail, getStatus, getWinlongList } from "@/lib/api";

function setWindowValue(value: Window | object | undefined) {
  Object.defineProperty(globalThis, "window", {
    value,
    configurable: true,
    writable: true,
  });
}

describe("api client", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    setWindowValue(window);
  });

  it("uses API_BASE_URL on server-side list fetch", async () => {
    process.env.API_BASE_URL = "http://api.internal:8001";
    setWindowValue(undefined);
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ code: 0, message: "ok", data: { coins: [] } }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await getWinlongList();

    expect(fetchMock).toHaveBeenCalledWith(
      "http://api.internal:8001/api/winlong/list?sort_by=score&order=desc",
      expect.objectContaining({ next: { revalidate: 60 } }),
    );
  });

  it("throws when detail request fails", async () => {
    process.env.API_BASE_URL = "http://api.internal:8001";
    setWindowValue(undefined);
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
      }),
    );

    await expect(getCoinDetail("BTCUSDT")).rejects.toThrow("Request failed: /api/winlong/coins/BTCUSDT");
  });

  it("uses relative path for clientFetcher in browser context", async () => {
    setWindowValue({});

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ code: 0, message: "ok", data: { overview: {} } }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await clientFetcher("/api/winlong/status");

    expect(fetchMock).toHaveBeenCalledWith("/api/winlong/status");
  });

  it("requests status with shorter revalidate window", async () => {
    process.env.API_BASE_URL = "http://api.internal:8001";
    setWindowValue(undefined);
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ code: 0, message: "ok", data: { overview: {}, sources: [], logs: [] } }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await getStatus();

    expect(fetchMock).toHaveBeenCalledWith(
      "http://api.internal:8001/api/winlong/status",
      expect.objectContaining({ next: { revalidate: 30 } }),
    );
  });
});
