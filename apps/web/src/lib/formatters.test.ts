import {
  formatCompactCurrency,
  formatCurrency,
  formatPercent,
  getScoreTone,
} from "@/lib/formatters";

describe("formatters", () => {
  it("formats currency with separators", () => {
    expect(formatCurrency(97500)).toBe("$97,500.00");
  });

  it("formats compact currency in uppercase", () => {
    expect(formatCompactCurrency(28500000000)).toBe("$28.50B");
  });

  it("formats positive percentages with plus sign", () => {
    expect(formatPercent(2.35)).toBe("+2.35%");
    expect(formatPercent(-1.26)).toBe("-1.26%");
  });

  it("maps score ranges to tones", () => {
    expect(getScoreTone(87)).toBe("excellent");
    expect(getScoreTone(70)).toBe("good");
    expect(getScoreTone(48)).toBe("average");
    expect(getScoreTone(20)).toBe("poor");
  });
});
