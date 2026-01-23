import { render, screen, waitFor, act } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import NotFoundPage from "./NotFoundPage";

jest.mock("lottie-react", () => ({
  __esModule: true,
  default: () => <div>Animation Rendered</div>,
}));

describe("Unit Testing NotFoundPage", () => {
  beforeEach(() => {
    global.fetch = jest.fn(() => new Promise(() => {})) as jest.Mock;
  });

  const flushPromises = () => new Promise((resolve) => setTimeout(resolve, 0));

  const renderNotFound = () => {
    return render(
      <MemoryRouter>
        <NotFoundPage />
      </MemoryRouter>
    );
  };

  const renderNotFoundAndFlush = async () => {
    await act(async () => {
      renderNotFound();
      await flushPromises();
    });
  };

  it("should render the 404 heading and message", () => {
    renderNotFound();
    expect(screen.getByRole("heading", { name: "404" })).toBeInTheDocument();
    expect(screen.getByText("Page Not Found")).toBeInTheDocument();
    expect(screen.getByText("The page you're looking for doesn't exist.")).toBeInTheDocument();
  });

  it("should render a link back to home", () => {
    renderNotFound();
    const homeLink = screen.getByRole("link", { name: "Back to Home" });
    expect(homeLink).toHaveAttribute("href", "/");
  });

  it("should load the lottie animation on mount", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    });
    await renderNotFoundAndFlush();
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith("/lottie/alert-lottie.json");
    });
  });
});
