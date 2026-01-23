import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Header from "./Header";

jest.mock("./GenericIcon", () => ({
  __esModule: true,
  default: ({ onClick }: { onClick?: () => void }) => (
    <button type="button" onClick={onClick}>
      GitHub
    </button>
  ),
}));

describe("Unit Testing Header", () => {
  const renderHeader = (initialPath: string = "/") => {
    return render(
      <MemoryRouter initialEntries={[initialPath]}>
        <Header />
      </MemoryRouter>
    );
  };

  it("should render the logo and navigation links", () => {
    renderHeader();
    expect(screen.getByRole("link", { name: "zapgaze™" })).toHaveAttribute("href", "/");
    expect(screen.getByRole("link", { name: "Home" })).toHaveAttribute("href", "/");
    expect(screen.getByRole("link", { name: "Test" })).toHaveAttribute("href", "/test");
    expect(screen.getByRole("link", { name: "Results" })).toHaveAttribute("href", "/results");
    expect(screen.getByRole("link", { name: "About" })).toHaveAttribute("href", "/about");
  });

  it("should open the GitHub repo when clicking the icon", () => {
    const openSpy = jest.spyOn(window, "open").mockImplementation(() => null);
    renderHeader();

    fireEvent.click(screen.getByRole("button", { name: "GitHub" }));
    expect(openSpy).toHaveBeenCalledWith(
      "https://github.com/Joumanasalahedin/zapgaze",
      "_blank"
    );
  });

  it("should keep the active link on /test", () => {
    renderHeader("/test");
    const testLink = screen.getByRole("link", { name: "Test" });
    expect(testLink.className).toContain("linkActive");
  });
});
