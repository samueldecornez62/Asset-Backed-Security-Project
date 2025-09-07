# waterfall_testing_file_mortgages.py
# Minimal end-to-end check using only mortgage-backed loans

import os, sys

# Ensure local packages are importable when running this file directly
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# Imports
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
            formatted_tranches = [f"{tr}" for tr in row]
            print(" | ".join([str(period)] + formatted_tranches))

def build_mortgage_pool():
    """
    Tiny deterministic pool: 3 fixed-rate mortgages with 1-year terms
    (keeps the run short and comparable to the car test).
    """
    loans = []

    h1 = PrimaryHome(initial_value=400_000)
    h2 = PrimaryHome(initial_value=550_000)
    h3 = PrimaryHome(initial_value=300_000)

    # Mortgages (face, annual rate, term in years)
    loans.append(FixedMortgage(asset=h1, face=200_000, rate=0.045, term=1))
    loans.append(FixedMortgage(asset=h2, face=150_000, rate=0.040, term=1))
    loans.append(FixedMortgage(asset=h3, face=100_000, rate=0.050, term=1))

    return LoanPool(loans)

def build_structure(total_notional):
    """
    Two tranches: A (80%) and B (20%), Sequential mode.
    """
    ss = StructuredSecurities(total_notional_amount=total_notional)
    ss.addTranche(percent_notional=0.80, rate=0.05, subordination='A')
    ss.addTranche(percent_notional=0.20, rate=0.08, subordination='B')
    ss.setMode('Sequential')  # swap to 'Pro Rata' to test that branch
    return ss

def main():
    lp = build_mortgage_pool()
    ss = build_structure(total_notional=lp.totalLoanPrincipal())

    # Run the liability waterfall grid only
    liability_rows = doWaterfall(loan_pool=lp, ss=ss)

    # Pretty print
    printWaterfall(liability_rows)

if __name__ == "__main__":
    main()
