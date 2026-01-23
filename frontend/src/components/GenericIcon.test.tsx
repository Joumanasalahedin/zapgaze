import { render, fireEvent } from "@testing-library/react";
import GenericIcon from "./GenericIcon";

describe("Unit Testing GenericIcon", () => {
  it("should render the github icon svg", () => {
    const { container } = render(<GenericIcon icon="github" />);
    expect(container.querySelector("svg")).toBeInTheDocument();
  });

  it("should render the flag icon svg", () => {
    const { container } = render(<GenericIcon icon="flag" />);
    expect(container.querySelector("svg")).toBeInTheDocument();
  });

  it("should return null for unknown icon", () => {
    const { container } = render(<GenericIcon icon="unknown" />);
    expect(container.firstChild).toBeNull();
  });

  it("should call onClick when provided", () => {
    const onClick = jest.fn();
    const { container } = render(<GenericIcon icon="github" onClick={onClick} />);
    const svg = container.querySelector("svg");
    expect(svg).toBeInTheDocument();
    if (!svg) {
      throw new Error("Expected svg to be rendered");
    }
    fireEvent.click(svg);
    expect(onClick).toHaveBeenCalledTimes(1);
  });
});
