# Testing files for metric calculations



import logging
logging.getLogger().setLevel(logging.INFO)

from Tranches.base_tranche_class import Tranche

def pretty(v, nd=6):
    return "None" if v is None else (f"{v:.{nd}f}")

def run_case(name, rate, notional, principal_series, extra_interest_each_period=0.0):
    print(f"\n=== {name} ===")
    t = Tranche(notional=notional, rate=rate, subordination='A')

    # Build cash inflows per period = (interest + principal).
    # For testing, we just add a flat 'extra interest' to each period.
    cashflows = [p + extra_interest_each_period for p in principal_series]

    irr_ann = t.IRR(cashflows)                  # annual decimal
    dirr_bps = t.DIRR(cashflows)                # basis points
    rating  = t.DIRR_rating(dirr_bps)           # rating from bps thresholds
    al_yrs  = t.AL(principal_series, return_years=True)

    print(f"Tranche rate (annual): {rate:.4f}")
    print(f"IRR (annual):          {pretty(irr_ann, 6)}")
    print(f"DIRR (bps):            {pretty(dirr_bps, 3)}")
    print(f"Rating:                {rating}")
    print(f"Average Life (years):  {pretty(al_yrs, 4)}")

if __name__ == "__main__":
    # Case A: Fully paid over 12 months, NO extra interest -> IRR < rate => positive DIRR (bps), mid-tier rating
    notional = 1000.0
    principal_12 = [80.0]*11 + [120.0]  # sums to 1000
    run_case(
        name="Case A - principal only",
        rate=0.0500,             # 5% annual tranche coupon
        notional=notional,
        principal_series=principal_12,
        extra_interest_each_period=0.0
    )

    # Case B: Same principal, add small interest each period -> IRR increases, DIRR (bps) drops, rating improves
    run_case(
        name="Case B - principal + $5 interest each period",
        rate=0.0500,
        notional=notional,
        principal_series=principal_12,
        extra_interest_each_period=5.0
    )
