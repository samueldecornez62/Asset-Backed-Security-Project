# waterfall_testing_file_mixed.py
# End-to-end check with BOTH cars and mortgages in one pool

import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# Imports
from loan.car_class import Car
from loan.loans import FixedRateLoan
from loan.house_derived_classes import PrimaryHome
from loan.mortgage import FixedMortgage
from loan.loan_pool import LoanPool

from Tranches.structured_securities_class import StructuredSecurities
from Tranches.waterfall_function import doWaterfall


try:
    from Tranches.waterfall_function import printWaterfall
except Exception:
    def printWaterfall(liability_rows):
        if not liability_rows:
            print("No data.")
            return
        header = ["Period"] + [f"Tranche {i+1}" for i in range(len(liability_rows[0]))]
        print(" | ".join(header))
        print("-" * 100)
        for period, row in enumerate(liability_rows, start=1):
            print(" | ".join([str(period)] + [f"{tr}" for tr in row]))

def build_mixed_pool():
    """
    Mixed pool: 2 car loans + 2 mortgages.
    Keep all terms = 1 year for a quick run (~12 periods).
    """
    loans = []

    # --- Cars ---
    civic  = Car(initial_value=22_000, model="Civic")
    camry  = Car(initial_value=27_000, model="Camry")
    loans.append(FixedRateLoan(asset=civic, face=10_000, rate=0.06, term=1))   # 12 months
    loans.append(FixedRateLoan(asset=camry, face=12_000, rate=0.055, term=1))

    # --- Mortgages ---
    h1 = PrimaryHome(initial_value=450_000)
    h2 = PrimaryHome(initial_value=380_000)
    loans.append(FixedMortgage(asset=h1, face=160_000, rate=0.045, term=1))
    loans.append(FixedMortgage(asset=h2, face=120_000, rate=0.050, term=1))

    return LoanPool(loans)

def build_structure(total_notional):
    """
    Two tranches: A (80%) and B (20%), Sequential mode.
    """
    ss = StructuredSecurities(total_notional_amount=total_notional)
    ss.addTranche(percent_notional=0.80, rate=0.05, subordination='A')
    ss.addTranche(percent_notional=0.20, rate=0.08, subordination='B')
    ss.setMode('Sequential')  # switch to 'Pro Rata' if you want to test that branch
    return ss

def main():
    lp = build_mixed_pool()
    ss = build_structure(total_notional=lp.totalLoanPrincipal())

    # Run waterfall (returns only liabilities grid)
    liability_rows = doWaterfall(loan_pool=lp, ss=ss)

    # Pretty print: Period | Tranche 1 | Tranche 2
    printWaterfall(liability_rows)

if __name__ == "__main__":
    main()
