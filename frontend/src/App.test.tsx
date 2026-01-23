import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App from "./App";

jest.mock("./components/Layout", () => ({
  __esModule: true,
  default: () => {
    const { Outlet } = require("react-router-dom");
    return (
      <div>
        <Outlet />
      </div>
    );
  },
}));

jest.mock("./pages/HomePage", () => ({
  __esModule: true,
  default: () => <div>Home Page Rendered</div>,
}));

jest.mock("./pages/AboutPage", () => ({
  __esModule: true,
  default: () => <div>About Page Rendered</div>,
}));

jest.mock("./pages/TestPage", () => ({
  __esModule: true,
  default: () => <div>Test Page Rendered</div>,
}));

jest.mock("./pages/ResultsPage", () => ({
  __esModule: true,
  default: () => <div>Results Page Rendered</div>,
}));

jest.mock("./pages/NotFoundPage", () => ({
  __esModule: true,
  default: () => <div>Not Found Page Rendered</div>,
}));

jest.mock("./pages/IntakeQuestionnairePage", () => ({
  __esModule: true,
  default: () => <div>Intake Page Rendered</div>,
}));

jest.mock("./pages/SingleResultPage", () => ({
  __esModule: true,
  default: () => <div>Single Result Page Rendered</div>,
}));

describe("Unit Testing App", () => {
  it("should render the home route", async () => {
    render(
      <MemoryRouter initialEntries={["/"]}>
        <App />
      </MemoryRouter>
    );

    expect(await screen.findByText("Home Page Rendered")).toBeInTheDocument();
  });

  it("should render the about route", async () => {
    render(
      <MemoryRouter initialEntries={["/about"]}>
        <App />
      </MemoryRouter>
    );

    expect(await screen.findByText("About Page Rendered")).toBeInTheDocument();
  });

  it("should render the test route", async () => {
    render(
      <MemoryRouter initialEntries={["/test"]}>
        <App />
      </MemoryRouter>
    );

    expect(await screen.findByText("Test Page Rendered")).toBeInTheDocument();
  });

  it("should render the intake route", async () => {
    render(
      <MemoryRouter initialEntries={["/intake"]}>
        <App />
      </MemoryRouter>
    );

    expect(await screen.findByText("Intake Page Rendered")).toBeInTheDocument();
  });

  it("should render the single result route", async () => {
    render(
      <MemoryRouter initialEntries={["/results/session-123"]}>
        <App />
      </MemoryRouter>
    );

    expect(await screen.findByText("Single Result Page Rendered")).toBeInTheDocument();
  });

  it("should render the not found route", async () => {
    render(
      <MemoryRouter initialEntries={["/does-not-exist"]}>
        <App />
      </MemoryRouter>
    );

    expect(await screen.findByText("Not Found Page Rendered")).toBeInTheDocument();
  });
});
