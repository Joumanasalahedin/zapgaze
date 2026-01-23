import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Layout from "./Layout";

const mockUseLayoutFlags = jest.fn();
jest.mock("../App", () => ({
  useLayoutFlags: () => mockUseLayoutFlags(),
}));

jest.mock("./Header", () => ({
  __esModule: true,
  default: () => <div>Header</div>,
}));

jest.mock("./Footer", () => ({
  __esModule: true,
  default: () => <div>Footer</div>,
}));

describe("Unit Testing Layout", () => {
  const renderLayout = (flags: { showHeader: boolean; showFooter: boolean }) => {
    mockUseLayoutFlags.mockReturnValue({ flags });
    return render(
      <MemoryRouter>
        <Layout />
      </MemoryRouter>
    );
  };

  it("should render header and footer when enabled", () => {
    renderLayout({ showHeader: true, showFooter: true });
    expect(screen.getByText("Header")).toBeInTheDocument();
    expect(screen.getByText("Footer")).toBeInTheDocument();
  });

  it("should hide header and footer when disabled", () => {
    renderLayout({ showHeader: false, showFooter: false });
    expect(screen.queryByText("Header")).not.toBeInTheDocument();
    expect(screen.queryByText("Footer")).not.toBeInTheDocument();
  });
});
