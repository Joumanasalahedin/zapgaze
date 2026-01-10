import { render, screen, waitFor, act } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import TestPage from "./TestPage";

const mockNavigate = jest.fn();
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockNavigate,
  Link: ({ to, children, ...props }: any) => (
    <a href={to} {...props}>
      {children}
    </a>
  ),
}));

jest.mock("../components/modals/EscapeConfirmationModal", () => {
  return function MockEscapeConfirmationModal({ show, onCancel, onContinue }: any) {
    if (!show) return null;
    return (
      <div data-testid="escape-confirmation-modal">
        <button onClick={onCancel}>Cancel</button>
        <button onClick={onContinue}>Continue</button>
      </div>
    );
  };
});

jest.mock("./IntakeQuestionnairePage", () => ({
  ASRS_QUESTIONS: [
    { id: 1, text: "Test Question 1" },
    { id: 2, text: "Test Question 2" },
    { id: 3, text: "Test Question 3" },
    { id: 4, text: "Test Question 4" },
    { id: 5, text: "Test Question 5" },
  ],
  ASRS_OPTIONS: ["Never", "Rarely", "Sometimes", "Often", "Very Often"],
}));

global.fetch = jest.fn();

const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, "localStorage", {
  value: localStorageMock,
});

describe("Unit Testing TestPage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({}),
    });
    localStorageMock.getItem.mockReturnValue(null);
  });

  const renderTestPage = () => {
    return render(
      <BrowserRouter>
        <TestPage />
      </BrowserRouter>
    );
  };

  describe("Initial render without intake data", () => {
    it("should show instructions with questionnaire button when no intake data", () => {
      renderTestPage();

      expect(screen.getByText("Go/No-Go Test Instructions")).toBeInTheDocument();
      expect(screen.getByText(/You will see letters one at a time/i)).toBeInTheDocument();
      expect(screen.getByText("Take Questionnaire")).toBeInTheDocument();
    });
  });

  describe("Instructions phase with intake data", () => {
    beforeEach(() => {
      localStorageMock.getItem.mockReturnValue(
        JSON.stringify({
          session_uid: "test-session-123",
          name: "Test User",
          birthdate: "1990-01-01",
          timestamp: Date.now(),
          answers: [0, 1, 2, 3, 4],
        })
      );
    });

    it("should render instructions with action buttons when intake data exists", () => {
      renderTestPage();

      expect(screen.getByText("Go/No-Go Test Instructions")).toBeInTheDocument();
      expect(screen.getByText("Proceed to Calibration")).toBeInTheDocument();
      expect(screen.getByText("View Previous Results")).toBeInTheDocument();
      expect(screen.getByText("Answer Again")).toBeInTheDocument();
    });
  });

  describe("Calibration phase", () => {
    beforeEach(() => {
      localStorageMock.getItem.mockReturnValue(
        JSON.stringify({
          session_uid: "test-session-123",
          name: "Test User",
          birthdate: "1990-01-01",
          timestamp: Date.now(),
          answers: [0, 1, 2, 3, 4],
        })
      );
    });

    it("should show calibration instructions initially", async () => {
      renderTestPage();

      const proceedButton = screen.getByText("Proceed to Calibration");
      await act(async () => {
        proceedButton.click();
      });

      await waitFor(() => {
        expect(screen.getByText(/Calibration/i)).toBeInTheDocument();
      });
    });
  });

  describe("Component rendering", () => {
    it("should render without crashing", () => {
      renderTestPage();
      expect(screen.getByText("Go/No-Go Test Instructions")).toBeInTheDocument();
    });

    it("should handle missing intake data gracefully", () => {
      localStorageMock.getItem.mockReturnValue(null);
      renderTestPage();

      expect(screen.getByText("Go/No-Go Test Instructions")).toBeInTheDocument();
    });
  });
});
