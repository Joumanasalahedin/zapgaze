import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App from "../App";

jest.mock("../pages/TestPage", () => ({
  __esModule: true,
  default: () => <div>Test Page Rendered</div>,
}));

jest.mock("../components/Header", () => ({
  __esModule: true,
  default: () => <div>Header</div>,
}));

jest.mock("../components/Footer", () => ({
  __esModule: true,
  default: () => <div>Footer</div>,
}));

describe("Unit Testing TestPage", () => {
  const renderTestRoute = () => {
    return render(
      <MemoryRouter initialEntries={["/test"]}>
        <App />
      </MemoryRouter>
    );
  };

  it("should render via the /test route", async () => {
    renderTestRoute();
    expect(await screen.findByText("Test Page Rendered")).toBeInTheDocument();
  });

  it("should hide header and footer on /test", async () => {
    renderTestRoute();
    await waitFor(() => {
      expect(screen.queryByText("Header")).not.toBeInTheDocument();
      expect(screen.queryByText("Footer")).not.toBeInTheDocument();
    });
  });
});
