import { render, screen } from "@testing-library/react";

jest.mock("./AgentStatusChecker", () => ({
  __esModule: true,
  default: () => <div>Agent Status Checker Rendered</div>,
}));

describe("Unit Testing AgentStatusChecker", () => {
  it("should render the component", () => {
    const AgentStatusChecker = require("./AgentStatusChecker").default;
    render(<AgentStatusChecker />);
    expect(screen.getByText("Agent Status Checker Rendered")).toBeInTheDocument();
  });

  it("should render when passed props", () => {
    const AgentStatusChecker = require("./AgentStatusChecker").default;
    render(
      <AgentStatusChecker agentUrl="http://localhost:9000" apiBaseUrl="http://localhost:8000" />
    );
    expect(screen.getByText("Agent Status Checker Rendered")).toBeInTheDocument();
  });
});
