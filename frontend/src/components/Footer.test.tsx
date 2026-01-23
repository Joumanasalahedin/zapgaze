import { render, screen } from "@testing-library/react";
import Footer from "./Footer";

describe("Unit Testing Footer", () => {
  it("should render branding and year", () => {
    jest.spyOn(Date.prototype, "getFullYear").mockReturnValue(2026);
    render(<Footer />);

    expect(screen.getByText(/zapgaze™/i)).toBeInTheDocument();
    expect(screen.getByText(/2026/)).toBeInTheDocument();
    expect(screen.getByText(/All rights reserved/i)).toBeInTheDocument();
  });

  it("should credit the designers", () => {
    render(<Footer />);
    expect(screen.getByText(/Designed by/i)).toBeInTheDocument();
    expect(screen.getByText("Joumana")).toBeInTheDocument();
    expect(screen.getByText("Somto")).toBeInTheDocument();
  });
});
