import { render } from "@testing-library/react";
import LoadingSpinner from "./LoadingSpinner";

describe("Unit Testing LoadingSpinner", () => {
  it("should render without crashing", () => {
    const { container } = render(<LoadingSpinner />);
    expect(container.firstChild).toBeInTheDocument();
  });

  it("should render the spinner element", () => {
    const { container } = render(<LoadingSpinner />);
    const spinner = container.querySelector("div > div");
    expect(spinner).toBeInTheDocument();
  });
});
