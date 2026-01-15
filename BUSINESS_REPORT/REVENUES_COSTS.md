## Revenues & Costs (36 months / 3 years) — ZapGaze

This document provides a simple, defensible **Revenues and Costs analysis** for a **3-year (36-month) plan**, aligned to the previously defined SOM end-state of **~60 B2B accounts by month 36**.

All figures are **excl. VAT**.

---

### 1) What this model is (and is not)

- **This is**: a conservative, template-friendly P&L forecast for an early-stage, health-adjacent **ADHD evaluation (not diagnosis)** tool.
- **This is not**: a guarantee of adoption or regulatory clearance; it’s an internally consistent planning model.

---

### 2) Two views (recommended)

We provide two P&L views:

- **Cash view**: reflects **actual cash spending** (founders may take €0 salary early on).
- **Economic view**: cash view **plus fair-market founder labor** as an expense (to avoid unrealistic margins).

Use **cash view** for runway and budgeting; use **economic view** for credibility and “true cost”.

---

### 3) Revenue model (fits the “Revenue Calculation Year 1” template)

Keep revenue streams minimal (3 lines):

- **B2C single evaluation**
  - Price: **€9.99**
  - Units/year: number of single evaluations sold

- **B2C 3-evaluation pack**
  - Price: **€18.98**
  - Units/year: number of packs sold

- **B2B subscriptions**
  - Model unit as **subscription-months** (recommended for ramping)
  - Price/unit: monthly plan price (Basic/Business/Pro)
  - Units/year: customer-months per plan

**B2B plan prices (monthly):**
- Basic: **€149.99**
- Business: **€349.99**
- Business Pro: **€499.99**

---

### 4) B2B ramp assumptions (to align with SOM at month 36)

End-of-year targets (accounts):
- **End of Y1**: 10 accounts
- **End of Y2**: 30 accounts
- **End of Y3**: 60 accounts

End-of-Y3 plan mix (accounts):
- **40 Basic / 15 Business / 5 Pro**

For annual revenue, a simple and conservative approximation is to use **average customers during the year** (roughly linear ramp):
- Avg accounts in **Y1 ≈ 5**
- Avg accounts in **Y2 ≈ 20**
- Avg accounts in **Y3 ≈ 45**

---

### 5) Costs: what is COGS vs SG&A (and why)

For SaaS, **COGS** should include costs that scale with delivering the service.

#### COGS (direct delivery)
- Cloud infrastructure (hosting, DB, storage, backups, monitoring)
- Payment processing fees

#### SG&A (operating expenses)
- Marketing (website, content, flyers/ads, design tools)
- Sales (CRM, outreach tools, travel)
- R&D (development, testing, validation)
- Administrative (accounting, legal/GDPR, insurance)
- **Customer support**: **SG&A** (per your decision)

---

### 6) Year-by-year P&L summary (excl. VAT)

These values are provided as CSVs in this repo:
- `pnl_y1_cash.csv`, `pnl_y2_cash.csv`, `pnl_y3_cash.csv`
- `pnl_y1_economic.csv`, `pnl_y2_economic.csv`, `pnl_y3_economic.csv`

#### Cash view (founder labour not cash-paid)

| Year | Revenue | COGS | Gross Profit | SG&A (cash) | Operating Profit (cash) |
|---:|---:|---:|---:|---:|---:|
| Y1 | €28,495 | €4,430 | €24,065 | €6,500 | €17,565 |
| Y2 | €85,849 | €9,005 | €76,844 | €15,000 | €61,844 |
| Y3 | €168,731 | €14,907 | €153,824 | €28,000 | €125,824 |

#### Economic view (adds founder labour at fair-market cost)

| Year | Operating Profit (cash) | Founder labour (non-cash) | Operating Profit (economic) |
|---:|---:|---:|---:|
| Y1 | €17,565 | €80,000 | **-€62,435** |
| Y2 | €61,844 | €120,000 | **-€58,156** |
| Y3 | €125,824 | €160,000 | **-€34,176** |

---

### 7) How to use this with your Excel template

- **Revenue Y1–Y3**: enter your chosen revenue streams (B2C single, B2C pack, B2B subscription-months).
- **COGS Y1–Y3**: enter cloud infrastructure and payment fees as direct costs.
- **SG&A Y1–Y3**: enter Marketing/Sales/R&D/Admin; include **customer support** in SG&A.
- **Profit & Loss Statement**: link totals from Revenue/COGS/SG&A to the P&L summary for each year.

If your template only supports one SG&A number, use:
- **Cash view** for the main sheet, and
- include **economic view** in a separate appendix slide or a note.

---

## Slide-ready content

### Slide — Revenues & Costs (how we model it)

**On-slide:**
- **Horizon**: 36 months (Y1–Y3), excl. VAT
- **Revenue streams**: B2C evaluations + B2B subscriptions
- **Two views**: Cash P&L and Economic P&L (adds founder labor)
- **COGS**: cloud + payment fees
- **SG&A**: marketing, sales, R&D, admin, customer support

**Presenter notes (optional):**
- Cash view is for runway; economic view is for credibility (true cost of building and running).


### Slide — Profit & Loss (cash view)

| Year | Revenue | COGS | Gross Profit | SG&A (cash) | Operating Profit (cash) |
|---:|---:|---:|---:|---:|---:|
| Y1 | €28,495 | €4,430 | €24,065 | €6,500 | €17,565 |
| Y2 | €85,849 | €9,005 | €76,844 | €15,000 | €61,844 |
| Y3 | €168,731 | €14,907 | €153,824 | €28,000 | €125,824 |

**Presenter notes (optional):**
- This is “cash reality”: founders can choose to defer salaries early, which keeps the business cash-positive.


### Slide — Profit & Loss (economic view)

| Year | Operating Profit (cash) | Founder labour (non-cash) | Operating Profit (economic) |
|---:|---:|---:|---:|
| Y1 | €17,565 | €80,000 | **-€62,435** |
| Y2 | €61,844 | €120,000 | **-€58,156** |
| Y3 | €125,824 | €160,000 | **-€34,176** |

**Presenter notes (optional):**
- This answers the investor question: “what does it cost if you paid yourselves market rates?”
- Still improving by Y3; profitability requires either more scale (more accounts), higher ARPA, or slower hiring.


### Slide — Key operating assumptions (what drives the numbers)

| Driver | Y1 | Y2 | Y3 |
|---|---:|---:|---:|
| **B2B accounts (end of year)** | 10 | 30 | 60 |
| **B2B mix at end of Y3** |  |  | 40 Basic / 15 Business / 5 Pro |
| **B2C paid evaluations (year)** | 2,000 | 4,000 | 6,000 |
| **COGS (main components)** | cloud + payment fees | cloud + payment fees | cloud + payment fees |
| **Support** | SG&A | SG&A | SG&A |

**Presenter notes (optional):**
- B2B ramp is aligned to the SOM target: ~60 accounts by month 36.
- B2C is secondary; pricing is low, so distribution/trust is the constraint.


### Slide — Key takeaways (1 slide, very simple)

**On-slide:**
- **Gross margins are high** (software delivery; COGS mainly cloud + fees)
- **Cash-positive early** if founders defer salaries
- **Economic view still negative in Y3** → scale/ARPA needed for profitability


