import { render, screen, act, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import HomePage from "./HomePage";

describe("Unit Testing HomePage", () => {
  afterEach(() => {
    jest.restoreAllMocks();
    jest.useRealTimers();
  });

  const renderHomePage = () => {
    return render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>
    );
  };

  it("should render a morning greeting", () => {
    jest.spyOn(Date.prototype, "getHours").mockReturnValue(9);
    renderHomePage();

    expect(screen.getByRole("heading", { name: "Good morning!" })).toBeInTheDocument();
  });

  it("should link to the test page", () => {
    renderHomePage();
    const takeTestLink = screen.getByRole("link", { name: "Take the Test" });
    expect(takeTestLink).toHaveAttribute("href", "/test");
  });

  it("should link to the about page", () => {
    renderHomePage();
    const learnMoreLink = screen.getByRole("link", { name: "Learn More" });
    expect(learnMoreLink).toHaveAttribute("href", "/about");
  });

  it("should advance the ADHD fact automatically", () => {
    jest.useFakeTimers();
    renderHomePage();

    expect(screen.getByText(/World Health Organization \(WHO\)/)).toBeInTheDocument();

    act(() => {
      jest.advanceTimersByTime(10000);
    });

    expect(screen.getByText(/National Institute of Mental Health \(NIMH\)/)).toBeInTheDocument();
  });

  it("should advance the ADHD fact when clicking Next", () => {
    renderHomePage();
    const nextButton = screen.getByRole("button", { name: "Next >" });
    fireEvent.click(nextButton);

    expect(screen.getByText(/National Institute of Mental Health \(NIMH\)/)).toBeInTheDocument();
  });
});
