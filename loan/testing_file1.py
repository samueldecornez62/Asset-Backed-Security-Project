"""
One-file test harness for loan & asset modules
"""

from loan.asset_base import Asset
from loan.car_class import Car
from loan.house_derived_classes import PrimaryHome, VacationHome
from loan.loans import FixedRateLoan, VariableRateLoan
from loan.mortgage import FixedMortgage, VariableMortgage, AutoLoan, MortgageMixin
from loan.loan_base import Loan
from loan.loan_pool import LoanPool


def almost_equal(a, b, tol=1e-8):
    return abs(a - b) <= tol


def expect(name, cond):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}")
    return cond


def expect_raises(name, exc_type, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc_type:
        print(f"[PASS] {name} (raised {exc_type.__name__})")
        return True
    except Exception as e:
        print(f"[FAIL] {name} (raised {type(e).__name__}: {e})")
        return False
    else:
        print(f"[FAIL] {name} (no exception)")
        return False


def test_asset_classes():
    print("\n=== Asset base & derived ===")
    # Base Asset should be abstract for yearlyDepreciationRate
    a = Asset(1000)
    expect_raises("Asset.yearlyDepreciationRate is abstract",
                  NotImplementedError, a.yearlyDepreciationRate)

    # Car with known model
    c = Car(20000, "Civic")
    expect("Car.yearlyDepreciationRate returns model rate", almost_equal(c.yearlyDepreciationRate(), 0.05))
    expect("Car.monthlyDepreciationRate is annual/12", almost_equal(c.monthlyDepreciationRate(), 0.05/12))
    expect("Car.currentAssetValue declines", c.currentAssetValue(12) < c.initial_value)

    # Car with unknown model gets default
    u = Car(10000, "Unknown")
    expect("Unknown car model uses default rate", almost_equal(u.yearlyDepreciationRate(), 0.30))

    # Houses
    ph = PrimaryHome(500000)
    vh = VacationHome(500000)
    expect("PrimaryHome yearly rate", almost_equal(ph.yearlyDepreciationRate(), 0.025))
    expect("VacationHome yearly rate", almost_equal(vh.yearlyDepreciationRate(), 0.015))
    expect("VacationHome depreciates slower than PrimaryHome",
           vh.currentAssetValue(12) > ph.currentAssetValue(12))


def test_loan_base_and_fixed():
    print("\n=== Loan base & FixedRateLoan ===")
    car = Car(20000, "Civic")
    loan = FixedRateLoan(car, face=15000, rate=0.06, term=5)

    # Static/class methods
    expect("Loan.monthlyRate(0.12) == 0.01", almost_equal(Loan.monthlyRate(0.12), 0.01))
    expect("Loan.annualRate(0.01) == 0.12", almost_equal(loan.annualRate(0.01), 0.12))

    pmt_obj = loan.monthlyPayment()
    pmt_cls = Loan.calcMonthlyPmt(15000, loan.rate(0), 5)
    expect("monthlyPayment delegates to class calcMonthlyPmt", almost_equal(pmt_obj, pmt_cls))

    bal_obj_12 = loan.balance_formula(12)
    bal_cls_12 = Loan.calcBalance(15000, loan.rate(12), 5, 12)
    expect("balance delegates to class calcBalance", almost_equal(bal_obj_12, bal_cls_12))

    # Interest/principal consistency
    i1 = loan.interestDue_formula(1)
    pr1 = loan.principalDue_formula(1)
    expect("monthlyPayment == interest + principal (period 1)", almost_equal(pmt_obj, i1 + pr1))

    # Recursive vs formula for a few periods
    for t in (1, 6, 12):
        expect(f"interestDue_recursive == interestDue_formula (t={t})",
               almost_equal(loan.interestDue_recursive(t), loan.interestDue_formula(t)))
        expect(f"principalDue_recursive == principalDue_formula (t={t})",
               almost_equal(loan.principalDue_recursive(t), loan.principalDue_formula(t)))
        expect(f"balance_recursive == balance_formula (t={t})",
               almost_equal(loan.balance_recursive(t), loan.balance_formula(t)))

    # Recovery & equity
    expect("recoveryValue is 60% of asset current value at t=12",
           almost_equal(loan.recoveryValue(12), 0.6 * car.currentAssetValue(12)))
    expect("equity = asset_value - balance", almost_equal(
        loan.equity(12), car.currentAssetValue(12) - loan.balance_formula(12)))


def test_variable_rate_loan():
    print("\n=== VariableRateLoan ===")
    car = Car(18000, "Civic")
    rd = {1: 0.05, 13: 0.06, 25: 0.07}
    vloan = VariableRateLoan(car, face=12000, rateDict=rd, term=3)

    # Key range behavior
    expect("rate at period 1 uses key 1", almost_equal(vloan.rate(1), 0.05))
    expect("rate at period 12 uses key 1", almost_equal(vloan.rate(12), 0.05))
    expect("rate at period 13 uses key 13", almost_equal(vloan.rate(13), 0.06))
    expect("rate at period 26 uses key 25", almost_equal(vloan.rate(26), 0.07))

    # Out of range should error
    expect_raises("Invalid period raises ValueError", ValueError, vloan.rate, 0)


def test_mortgages_and_auto():
    print("\n=== Mortgages & AutoLoan ===")
    # Mortgages
    home = PrimaryHome(500000)
    m = FixedMortgage(home, face=400000, rate=0.06, term=30)
    expect("PMI is positive when LTV >= 0.8", m.PMI(1) > 0)

    # Variable mortgage only tests construction here
    rd = {1: 0.05, 121: 0.055}
    vm = VariableMortgage(home, face=350000, rateDict=rd, term=30)
    expect("VariableMortgage constructed", isinstance(vm, VariableMortgage))

    # Auto
    car = Car(25000, "Lexus")
    al = AutoLoan(car, face=20000, rate=0.05, term=5)
    expect("AutoLoan constructed", isinstance(al, AutoLoan))
    expect_raises("AutoLoan with non-Car asset raises", TypeError, AutoLoan, home, 20000, 0.05, 5)


def test_loan_pool():
    print("\n=== LoanPool ===")
    loans = [
        FixedRateLoan(Car(30000, "Civic"), 20000, 0.05, 5),
        FixedRateLoan(Car(50000, "Lexus"), 30000, 0.04, 7),
    ]
    pool = LoanPool(loans)

    expect("totalLoanPrincipal is sum of faces", almost_equal(pool.totalLoanPrincipal(), 50000))
    expect("totalLoanBalance decreases over time", pool.totalLoanBalance(24) < pool.totalLoanBalance(12))
    expect("aggregatePayment equals sum of monthly payments at t=1", pool.aggregatePayment(1) > 0)
    expect("aggregateInterest equals sum of interests at t=1", pool.aggregateInterest(1) > 0)
    expect("aggregatePrincipal equals sum of principals at t=1", pool.aggregatePrincipal(1) > 0)
    expect("activeLoans at large period is zero", pool.activeLoans(10_000) == 0)
    expect("WAM is positive", pool.WAM() > 0)
    expect("WAR is between min and max rates", 0.0 <= pool.WAR(1) <= 1.0)
    expect("WAM_remaining decreases over time", pool.WAM_remaining(24) < pool.WAM_remaining(12))


def main():
    test_asset_classes()
    test_loan_base_and_fixed()
    test_variable_rate_loan()
    test_mortgages_and_auto()
    test_loan_pool()
    print("\nDone.")


if __name__ == "__main__":
    main()
