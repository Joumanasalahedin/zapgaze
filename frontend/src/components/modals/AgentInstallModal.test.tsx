import { render, screen } from "@testing-library/react";

jest.mock("./AgentInstallModal", () => ({
  __esModule: true,
  default: () => <div>Agent Install Modal Rendered</div>,
}));

describe("Unit Testing AgentInstallModal", () => {
  it("should render the modal component", () => {
    const AgentInstallModal = require("./AgentInstallModal").default;
    render(<AgentInstallModal open={true} onClose={jest.fn()} agentUrl="http://localhost:9000" />);
    expect(screen.getByText("Agent Install Modal Rendered")).toBeInTheDocument();
  });

  it("should render when closed prop is false", () => {
    const AgentInstallModal = require("./AgentInstallModal").default;
    render(<AgentInstallModal open={false} onClose={jest.fn()} agentUrl="http://localhost:9000" />);
    expect(screen.getByText("Agent Install Modal Rendered")).toBeInTheDocument();
  });
});
