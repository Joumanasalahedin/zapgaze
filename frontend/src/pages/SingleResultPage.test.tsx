import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App from "../App";

jest.mock("../pages/SingleResultPage", () => ({
  __esModule: true,
  default: () => <div>Single Result Page Rendered</div>,
}));

jest.mock("../components/Header", () => ({
  __esModule: true,
  default: () => <div>Header</div>,
}));

jest.mock("../components/Footer", () => ({
  __esModule: true,
  default: () => <div>Footer</div>,
}));

describe("Unit Testing SingleResultPage", () => {
  const renderSingleResultRoute = () => {
    return render(
      <MemoryRouter initialEntries={["/results/session-123"]}>
        <App />
      </MemoryRouter>
    );
  };

  it("should render via the /results/:sessionUid route", async () => {
    renderSingleResultRoute();
    expect(await screen.findByText("Single Result Page Rendered")).toBeInTheDocument();
  });

  it("should show header and footer on /results/:sessionUid", async () => {
    renderSingleResultRoute();
    await waitFor(() => {
      expect(screen.getByText("Header")).toBeInTheDocument();
      expect(screen.getByText("Footer")).toBeInTheDocument();
    });
  });

  it("should render via the /results/:sessionUid route for different session ids", async () => {
    render(
      <MemoryRouter initialEntries={["/results/another-session"]}>
        <App />
      </MemoryRouter>
    );

    expect(await screen.findByText("Single Result Page Rendered")).toBeInTheDocument();
  });
});
