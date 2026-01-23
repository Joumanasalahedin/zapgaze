import { render, screen, fireEvent } from "@testing-library/react";
import EscapeConfirmationModal from "./EscapeConfirmationModal";

describe("Unit Testing EscapeConfirmationModal", () => {
  it("should not render when show is false", () => {
    const { container } = render(
      <EscapeConfirmationModal show={false} onCancel={jest.fn()} onContinue={jest.fn()} />
    );
    expect(container.firstChild).toBeNull();
  });

  it("should render title and buttons when show is true", () => {
    render(<EscapeConfirmationModal show={true} onCancel={jest.fn()} onContinue={jest.fn()} />);
    expect(screen.getByText("Stop Test?")).toBeInTheDocument();
    expect(screen.getByText("Yes, Cancel [Esc]")).toBeInTheDocument();
    expect(screen.getByText("No, Continue [Enter]")).toBeInTheDocument();
  });

  it("should call handlers when buttons are clicked", () => {
    const onCancel = jest.fn();
    const onContinue = jest.fn();
    render(<EscapeConfirmationModal show={true} onCancel={onCancel} onContinue={onContinue} />);

    fireEvent.click(screen.getByText("Yes, Cancel [Esc]"));
    fireEvent.click(screen.getByText("No, Continue [Enter]"));

    expect(onCancel).toHaveBeenCalledTimes(1);
    expect(onContinue).toHaveBeenCalledTimes(1);
  });
});
