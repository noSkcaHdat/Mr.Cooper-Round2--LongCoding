#Insurance Policy Management
import datetime

db = {"customers": {}, "policies": {}, "premiums": {}, "claims": {}}
_ids = {"pol": 1, "cust": 1, "prem": 1, "claim": 1}

def next_id(key, prefix):
    val = f"{prefix}{_ids[key]:04d}"
    _ids[key] += 1
    return val


class RiskEngine: 
    def __init__(self):
        self.ageFactor = 0.0
        self.coverageFactor = 0.0
        self.historyFactor = 0

    def scoreRisk(self, customer, coverageAmount): # calculated from given score 
        age = customer.age
        self.ageFactor = 0.0 if age <= 35 else 0.5 if age <= 50 else 1.0 if age <= 60 else 2.0
        self.coverageFactor = coverageAmount * 0.005
        self.historyFactor = sum(1 for c in customer.claims_history if c.status == "APPROVED")

    def calculatePremium(self, customer, coverageAmount, preExistingConditions=0, claimFreeYears=0):
        base = coverageAmount * 0.005
        total = base * (1 + self.ageFactor) + preExistingConditions * 500 - base * min(claimFreeYears * 0.05, 0.5)
        return round(total / 10) * 10


class Policy:
    def __init__(self, policyNumber, holderId, policyType, coverageAmount, premium, startDate, endDate):
        self.policyNumber = policyNumber
        self.holderId = holderId
        self.type = policyType
        self.coverageAmount = coverageAmount
        self.premium = premium
        self.startDate = startDate
        self.endDate = endDate
        self.status = "PENDING"

    def activate(self):
        self.status = "ACTIVE"
        print(f"Policy {self.policyNumber} activated.")

    def lapse(self):
        self.status = "LAPSED"
        print(f"Policy {self.policyNumber} lapsed.") # lapsed state for exceptions

    def renew(self, newEndDate):
        self.endDate = newEndDate
        self.status = "ACTIVE"
        print(f"Policy {self.policyNumber} renewed till {newEndDate}.")

    def surrender(self):
        today = datetime.date.today()
        ratio = max(0.0, (self.endDate - today).days / (self.endDate - self.startDate).days)
        value = round(self.premium * ratio * 0.8 / 10) * 10
        self.status = "SURRENDERED"
        print(f"Policy {self.policyNumber} surrendered. Value: Rs{value}")

    def __str__(self):
        return f"{self.policyNumber} | {self.type} | Rs{self.coverageAmount} | Premium Rs{self.premium} | {self.status} | {self.startDate}~{self.endDate}"


class Claim:
    def __init__(self, policyNumber, incidentDate, amount):
        self.claimId = next_id("claim", "CLM")
        self.policyNumber = policyNumber
        self.incidentDate = incidentDate
        self.amount = amount
        self.status = "SUBMITTED"
        self.adjusterNotes = ""

    def submit(self):
        self.status = "SUBMITTED"
        print(f"Claim {self.claimId} submitted.")

    def approve(self, settlementAmount, notes=""):
        self.status = "APPROVED"
        self.adjusterNotes = notes
        print(f"Claim {self.claimId} approved. Settlement: Rs{settlementAmount}")

    def reject(self, notes=""):
        self.status = "REJECTED"
        self.adjusterNotes = notes
        print(f"Claim {self.claimId} rejected.")

    def calculateSettlement(self, coverageAmount):
        if self.amount > coverageAmount:
            print(f"Claim Rs{self.amount} exceeds limit. Shortfall: Rs{self.amount - coverageAmount}")
            return coverageAmount
        return self.amount

    def __str__(self):
        return f"{self.claimId} | Policy {self.policyNumber} | Rs{self.amount} | {self.status} | {self.incidentDate}"


class Premium:
    def __init__(self, policyNumber, dueDate, amount):
        self.premiumId = next_id("prem", "PRE")
        self.policyNumber = policyNumber
        self.dueDate = dueDate
        self.amount = amount
        self.paidDate = None
        self.status = "DUE"

    def pay(self, policy):
        self.paidDate = datetime.date.today()
        self.status = "PAID"
        policy.activate()
        print(f"Premium {self.premiumId} paid. Rs{self.amount}")

    def markOverdue(self):
        self.status = "OVERDUE"
        print(f"Premium {self.premiumId} overdue. Grace period: 30 days.")

    def applyGracePeriod(self, policy):
        if datetime.date.today() > self.dueDate + datetime.timedelta(days=30):
            self.status = "LAPSED"
            policy.lapse()
        else:
            print(f"Grace period ends {self.dueDate + datetime.timedelta(days=30)}.")

    def __str__(self):
        return f"{self.premiumId} | Policy {self.policyNumber} | Rs{self.amount} | Due {self.dueDate} | {self.status}"


class Underwriter:
    def __init__(self, underwriterId, name):
        self.underwriterId = underwriterId
        self.name = name

    def assessRisk(self, application):
        score = application["age"] * 0.5 + application.get("preExisting", 0) * 10
        print(f"Risk score: {score:.1f}")
        return score

    def approve(self, application):
        print(f"Approved: {application['customerId']}")

    def reject(self, application, reason="High risk"):
        print(f"Rejected: {application['customerId']} — {reason}")


class Customer:
    def __init__(self, name, age, kycStatus=True):
        self.customerId = next_id("cust", "CUST")
        self.name = name
        self.age = age
        self.kycStatus = kycStatus
        self.policies = []
        self.claims_history = []

    def applyPolicy(self, policyType, coverageAmount, preExisting=0):
        if not self.kycStatus:
            print("KYC incomplete."); return
        uw = Underwriter("UW01", "Rajesh")
        app = {"customerId": self.customerId, "age": self.age, "preExisting": preExisting}
        if uw.assessRisk(app) > 100:
            uw.reject(app); return
        uw.approve(app)
        engine = RiskEngine()
        engine.scoreRisk(self, coverageAmount)
        free_years = max(0, len(self.policies) - sum(1 for c in self.claims_history if c.status == "APPROVED"))
        premium = engine.calculatePremium(self, coverageAmount, preExisting, free_years)
        today = datetime.date.today()
        pol = Policy(next_id("pol", "POL"), self.customerId, policyType, coverageAmount, premium, today, today.replace(year=today.year + 1))
        db["policies"][pol.policyNumber] = pol
        self.policies.append(pol)
        prem = Premium(pol.policyNumber, today, premium)
        db["premiums"][prem.premiumId] = prem
        print(f"Policy {pol.policyNumber} created | Premium Rs{premium} | Pay {prem.premiumId} to activate.")

    def raiseClaim(self, policyNumber, incidentDate, amount):
        pol = db["policies"].get(policyNumber)
        if not pol or pol.status != "ACTIVE":
            print("Policy not active."); return
        c = Claim(policyNumber, incidentDate, amount)
        c.submit()
        c.approve(c.calculateSettlement(pol.coverageAmount))
        self.claims_history.append(c)
        db["claims"][c.claimId] = c

    def renewPolicy(self, policyNumber):
        pol = db["policies"].get(policyNumber)
        if not pol:
            print("Policy not found."); return
        pol.renew(pol.endDate.replace(year=pol.endDate.year + 1))
        prem = Premium(policyNumber, datetime.date.today(), pol.premium)
        db["premiums"][prem.premiumId] = prem
        print(f"Pay {prem.premiumId} (Rs{prem.amount}) to complete renewal.")

    def __str__(self):
        return f"{self.customerId} | {self.name} | Age {self.age} | KYC {'Y' if self.kycStatus else 'N'} | Policies: {len(self.policies)}"



def main():
    while True:
        print("\n1=Add Customer  2=Apply Policy  3=Pay Premium  4=Raise Claim")
        print("5=Renew Policy  6=Endorsement  7=Miss Payment  8=Surrender  9=View All  0=Exit")
        ch = input("> ").strip()

        if ch == "1":
            c = Customer(input("Name: "), int(input("Age: ")), input("KYC done? y/n: ") == "y")
            db["customers"][c.customerId] = c
            print(c)

        elif ch == "2":
            c = db["customers"].get(input("Customer ID: "))
            if c: c.applyPolicy(input("Type: "), float(input("Coverage Rs: ")), int(input("Pre-existing: ")))
            else: print("Not found.")

        elif ch == "3":
            p = db["premiums"].get(input("Premium ID: "))
            if p: p.pay(db["policies"][p.policyNumber])
            else: print("Not found.")

        elif ch == "4":
            c = db["customers"].get(input("Customer ID: "))
            if c: c.raiseClaim(input("Policy No: "), datetime.date.fromisoformat(input("Date YYYY-MM-DD: ")), float(input("Amount Rs: ")))
            else: print("Not found.")

        elif ch == "5":
            c = db["customers"].get(input("Customer ID: "))
            if c: c.renewPolicy(input("Policy No: "))
            else: print("Not found.")

        elif ch == "6":
            pol = db["policies"].get(input("Policy No: "))
            if pol:
                new_cov = float(input("New coverage Rs: "))
                rem = (pol.endDate - datetime.date.today()).days
                new_prem = round(new_cov * 0.005 / 10) * 10
                extra = round((new_prem - pol.premium) * rem / 365 / 10) * 10 #calculated from given formula 
                pol.coverageAmount, pol.premium = new_cov, new_prem
                print(f"Updated. Extra pro-rata: Rs{extra}")
                if extra > 0:
                    pr = Premium(pol.policyNumber, datetime.date.today(), extra)
                    db["premiums"][pr.premiumId] = pr
                    print(f"Pay {pr.premiumId}")
            else: print("Not found.")

        elif ch == "7":
            p = db["premiums"].get(input("Premium ID: "))
            if p: p.markOverdue(); p.applyGracePeriod(db["policies"][p.policyNumber])
            else: print("Not found.")

        elif ch == "8":
            pol = db["policies"].get(input("Policy No: "))
            if pol: pol.surrender()
            else: print("Not found.")

        elif ch == "9":
            for label, store in [("Customers", "customers"), ("Policies", "policies"), ("Premiums", "premiums"), ("Claims", "claims")]:
                print(f"\n-- {label} --")
                for item in db[store].values(): print(item)

        elif ch == "0":
            print("Bye!"); break


if __name__ == "__main__":
    main()
#base premium and age factor formulas are dervived from the question