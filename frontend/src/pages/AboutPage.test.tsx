import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import AboutPage from "./AboutPage";

describe("Unit Testing AboutPage", () => {
  const renderAboutPage = () => {
    return render(
      <MemoryRouter>
        <AboutPage />
      </MemoryRouter>
    );
  };

  it("should render the main heading", () => {
    renderAboutPage();
    expect(screen.getByRole("heading", { name: "About zapgaze™" })).toBeInTheDocument();
  });

  it("should link to the test demo", () => {
    renderAboutPage();
    const demoLink = screen.getByRole("link", { name: "Try Demo" });
    expect(demoLink).toHaveAttribute("href", "/test");
  });
});
