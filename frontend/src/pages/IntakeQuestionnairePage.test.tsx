import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App from "../App";

jest.mock("../pages/IntakeQuestionnairePage", () => ({
  __esModule: true,
  default: () => <div>Intake Page Rendered</div>,
}));

jest.mock("../components/Header", () => ({
  __esModule: true,
  default: () => <div>Header</div>,
}));

jest.mock("../components/Footer", () => ({
  __esModule: true,
  default: () => <div>Footer</div>,
}));

describe("Unit Testing IntakeQuestionnairePage", () => {
  const renderIntakePage = () => {
    return render(
      <MemoryRouter initialEntries={["/intake"]}>
        <App />
      </MemoryRouter>
    );
  };

  it("should render via the /intake route", async () => {
    renderIntakePage();
    expect(await screen.findByText("Intake Page Rendered")).toBeInTheDocument();
  });

  it("should show header and footer on /intake", async () => {
    renderIntakePage();
    await waitFor(() => {
      expect(screen.getByText("Header")).toBeInTheDocument();
      expect(screen.getByText("Footer")).toBeInTheDocument();
    });
  });
});
