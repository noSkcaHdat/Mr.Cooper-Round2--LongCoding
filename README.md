# Insurance Management System

A console-based Insurance Management System built using Python. Developed as part of the Long Code Round assessment.

---

## Problem Statement

Build a console-based application to manage the complete lifecycle of insurance policies including customer onboarding, policy creation, premium payments, claim processing, policy renewal, endorsements and surrenders.

The system should handle:
- Customer registration with KYC verification
- Risk-based premium calculation using a Risk Engine
- Policy lifecycle management (activate, lapse, renew, surrender)
- Claim submission and settlement
- Premium tracking with grace period handling
- Policy endorsement (coverage updates)

---

## Approach & Logic

I designed the system around real-world insurance workflows. Each class represents an actual entity in an insurance company.

### Classes

| Class | What it does |
|---|---|
| Customer | Registers customers, applies for policies, raises claims |
| Policy | Manages policy lifecycle - activate, lapse, renew, surrender |
| Claim | Handles claim submission, approval, rejection and settlement |
| Premium | Tracks premium payments, overdue status and grace period |
| Underwriter | Assesses risk score and approves or rejects applications |
| RiskEngine | Calculates premium based on age, coverage and claim history |

### How Premium is Calculated (RiskEngine)

I used a RiskEngine class to calculate premiums dynamically based on:
- **Age Factor** - younger customers pay less
- **Coverage Factor** - higher coverage = higher premium
- **Claim History** - more past claims = higher premium
- **Claim Free Years** - discount for not raising claims (max 50% off)
- **Pre-existing Conditions** - Rs500 extra per condition

```
Base = coverageAmount × 0.005
Total = Base × (1 + ageFactor) + preExisting × 500 - discount
```

### Data Storage

Instead of separate lists I used a central `db` dictionary to store all records:

```python
db = {
    "customers": {},
    "policies": {},
    "premiums": {},
    "claims": {}
}
```

This makes it easy to look up any record directly using its ID.

### Auto ID Generation

I used a `next_id()` function to automatically generate unique IDs:
- Customers → CUST0001, CUST0002...
- Policies → POL0001, POL0002...
- Premiums → PRE0001, PRE0002...
- Claims → CLM0001, CLM0002...

### Policy Lifecycle Flow

```
Customer Registers
       ↓
Apply for Policy (Underwriter assesses risk)
       ↓
Policy Created (PENDING)
       ↓
Pay Premium → Policy ACTIVE
       ↓
Miss Payment → OVERDUE → Grace Period 30 days → LAPSED
       ↓
Raise Claim → Settlement Calculated → APPROVED/REJECTED
       ↓
Renew / Surrender
```

### OOPs Concepts Used

- **Encapsulation** - Each class manages its own data. For example, Policy handles its own status changes through activate(), lapse(), renew() and surrender()
- **Abstraction** - Customer just calls applyPolicy() or raiseClaim(). All the internal risk calculation and underwriting logic is hidden
- **Composition** - Customer holds a list of Policy objects and Claim history objects inside it

---

## Features

- Register customers with KYC verification
- Apply for policy with automatic risk-based premium calculation
- Pay premium to activate policy
- Raise and settle claims with coverage limit check
- Renew existing policies
- Update coverage mid-term with pro-rata premium adjustment (Endorsement)
- Miss payment → mark overdue → apply 30-day grace period → lapse policy
- Surrender policy and get back partial value
- View all customers, policies, premiums and claims

---

## Steps to Execute

### Requirements
- Python 3.x
- No external libraries needed

### Run the Program

```bash
# Clone the repository
git https://github.com/noSkcaHdat/Mr.Cooper-Round2--LongCoding

# Navigate to the folder
cd INSURANCE-POLICY-MGMT

# Run the program
python insurance_management.py
```

### How to Use

```
1 = Add Customer
2 = Apply Policy
3 = Pay Premium
4 = Raise Claim
5 = Renew Policy
6 = Endorsement (update coverage)
7 = Miss Payment (mark overdue + grace period)
8 = Surrender Policy
9 = View All Records
0 = Exit
```

**Typical flow:**
1. Add a customer (option 1)
2. Apply for a policy (option 2) using the Customer ID
3. Pay the premium (option 3) using the Premium ID shown
4. Raise a claim (option 4) once policy is active
5. View all records (option 9) to see current status

---

## Project Structure

```
insurance-management/
│
├── insurance_management.py   # Complete source code
└── README.md                 # Project documentation
```

---

