/**
 * Verifies the basic user flow through intake and agent download.
 * This does not test the agent camera functionality.
 */

describe("Basic app flow", () => {
  it("completes intake and reaches agent download", () => {
    cy.intercept("POST", "**/intake/", {
      statusCode: 200,
      body: { session_uid: "e2e-session-123" },
    }).as("submitIntake");

    cy.intercept("GET", "**/agent/status", {
      statusCode: 200,
      body: { status: "disconnected" },
    }).as("agentStatus");

    cy.visit("/");
    cy.contains("Take the Test").click();

    cy.contains("Take Questionnaire").click();
    cy.get('input[type="text"]').type("Test User");
    cy.get('input[type="date"]').type("1990-01-01");
    cy.get('input[type="radio"][value="2"]').check({ force: true });

    cy.contains("Submit").click();
    cy.wait("@submitIntake");

    cy.contains("Go/No-Go Test Instructions").should("be.visible");
    cy.wait("@agentStatus");
    cy.contains("Download Agent").should("be.visible");

    cy.request("https://api.github.com/repos/Joumanasalahedin/zapgaze/releases/latest").then(
      (response) => {
        const asset = response.body.assets?.find((item: { name?: string }) =>
          item.name?.endsWith("ZapGazeAgent.zip")
        );
        cy.wrap(asset, { log: false }).should("exist");

        cy.window().then((win) => {
          cy.stub(win, "open").as("windowOpen");
        });

        cy.contains("Download Agent").click();
        cy.contains("macOS").click();

        cy.get("@windowOpen").should("have.been.calledWith", asset.browser_download_url, "_blank");
      }
    );

    cy.contains("Waiting for agent to connect...").should("be.visible");
    cy.visit("/");
  });
});
