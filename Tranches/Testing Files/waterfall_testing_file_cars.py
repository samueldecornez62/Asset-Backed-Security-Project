# test_waterfall_run.py
# Minimal end-to-end check of Part 1 waterfall

import os, sys


HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# Imports
from loan.car_class import Car
from loan.loans import FixedRateLoan
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
            formatted_tranches = [f"{tr}" for tr in row]
            print(" | ".join([str(period)] + formatted_tranches))

def build_small_pool():
    """
    Tiny deterministic pool: 3 fixed-rate car loans, 1-year term,
    so we should see ~12 periods until fully paid (ignoring rounding).
    """
    loans = []
    # Assets
    civic  = Car(initial_value=20000, model="Civic")
    lexus  = Car(initial_value=35000, model="Lexus")
    toyota = Car(initial_value=25000, model="Toyota")

    # Loans (face, annual rate, term in years)
    loans.append(FixedRateLoan(asset=civic,  face=10000, rate=0.06, term=1))  # 12 months
    loans.append(FixedRateLoan(asset=lexus,  face=15000, rate=0.05, term=1))
    loans.append(FixedRateLoan(asset=toyota, face= 5000, rate=0.07, term=1))

    return LoanPool(loans)

def build_structure(total_notional):
    """
    Two tranches: A (80%) and B (20%), Sequential mode.
    Rates are arbitrary for Part 1; you can tweak to taste.
    """
    ss = StructuredSecurities(total_notional_amount=total_notional)
    ss.addTranche(percent_notional=0.80, rate=0.05, subordination='A')
    ss.addTranche(percent_notional=0.20, rate=0.08, subordination='B')
    ss.setMode('Sequential')  # or 'Pro Rata'
    return ss

def main():
    lp = build_small_pool()
    ss = build_structure(total_notional=lp.totalLoanPrincipal())

    # Run the liability waterfall grid only (doWaterfall returns just rows)
    liability_rows = doWaterfall(loan_pool=lp, ss=ss)

    # Pretty print: Period | Tranche 1 | Tranche 2 | ...
    printWaterfall(liability_rows)

if __name__ == "__main__":
    main()
