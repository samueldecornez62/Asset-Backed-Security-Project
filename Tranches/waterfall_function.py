'''
This is a standalone function called doWaterfall. This populates data across periods.
'''



# from typing import List, Dict, Tuple



# Standalone function: not a class itself; calls other class methods
def doWaterfall(loan_pool, ss, max_periods: int = 10000):
    """
    Return format:
    Reads available amount of money supplied by the loan pool, to pay it out to the tranches
    Calls getWaterfall to get the waterfall per tranche at given period
    Loops through all periods until no more active loans
    getWaterfall, at period tp, prints a list of the 5 waterfall parameters for each tranche, side by side on the row
    """
    liability_rows = []

    # Start at first period, since no payments at period 0
    period = 1
    # Computational limit
    while period <= max_periods:
        # Stop if loan pool is inactive before period begins (hence breaking the loop since all loans paid out)
        if loan_pool.activeLoans(period - 1) == 0:
            break

        # Advance tranche time (default +1)
        ss.increaseTime()

        # Asset cash for given period
        interest_cash = loan_pool.aggregateInterest(period)
        principal_cash = loan_pool.aggregatePrincipal(period)
        total_cash = interest_cash + principal_cash

        # Pay out tranches with makePayments using cash received from loan
        ss.makePayments(total_cash, principal_cash)

        # Create liabilities row for given period (this loop is by period)
        # Default time period taken from tranche._timePeriod; see getWaterfall method
        row = ss.getWaterfall()
        liability_rows.append(row)

        # Additional check if all balances are 0:
        # Index [-1] is balance; check all sublists (i.e. all tranche waterfall lists in period/row)
        if all(sublist[-1] <= 1e-6 for sublist in row):
            break

        # Increment period before re-looping
        period += 1

    return liability_rows




# Extra function to nicely print liability_rows
def printWaterfall(liability_rows):
    # Create header
    header = ["Period"] + [f"Tranche {i+1}" for i in range(len(liability_rows[0]))]
    print(f" | ".join(header))
    # n = 10 + 50 * num_tranches
    print("-" * 100)


    for period, row in enumerate(liability_rows, start=1):
        # Each 'row' is the list of tranche sublists
        formatted_tranches = ["{}".format(tr) for tr in row]
        print(" | ".join([str(period)] + formatted_tranches))








































# def doWaterfall(loan_pool, ss, max_periods: int = 10000):
#     asset_side = []
#     liability_side = []
#     reserve_series = []
#
#     period = 1
#     while period <= max_periods:
#         if loan_pool.activeLoans(period - 1) == 0:
#             break
#
#         ss.increaseTime()
#
#         interest_pay = loan_pool.aggregateInterest(period)
#         principal_pay = loan_pool.aggregatePrincipal(period)
#         total_payment = interest_pay + principal_pay
#
#         ss.makePayments(total_payment, principal_pay)
#
#         asset_side.append({
#             "Period": period,
#             "Interest": float(interest_pay),
#             "Principal": float(principal_pay),
#             "Total": float(total_payment),
#             "ActiveLoans": int(loan_pool.activeLoans(period)),
#             "PoolBalance": float(loan_pool.totalLoanBalance(period)),
#         })
#
#         liability_side.append(ss.getWaterfall())
#         reserve_series.append(float(ss._reserveAccount))  # reserve after payments this period
#
#         period += 1
#
#     return asset_side, liability_side, reserve_series, float(ss._reserveAccount)











# def doWaterfall(loan_pool, ss, max_periods: int = 10000
#                ) -> Tuple[List[Dict[str, float]], List[list], float]:
#     """
#     Run the waterfall to completion.
#
#     Returns:
#       asset_side:    list of dicts per period with asset cash breakdown
#       liability_side: list of lists per period; each inner list is
#                       [Interest Due, Interest Paid, Interest Shortfall, Principal Paid, Balance]
#                       for each tranche (ordered by subordination) at that period.
#       reserve_balance: final reserve account balance (float)
#     """
#     asset_side: List[Dict[str, float]] = []
#     liability_side: List[list] = []
#
#     period = 1
#     while period <= max_periods:
#         # If there are no active loans as of end of previous period, we’re done.
#         if loan_pool.activeLoans(period - 1) == 0:
#             break
#
#         # 1) Advance liabilities’ time
#         ss.increaseTime()
#
#         # 2) Pull asset cash for this period
#         interest_pay = loan_pool.aggregateInterest(period)
#         principal_pay = loan_pool.aggregatePrincipal(period)
#         total_payment = interest_pay + principal_pay
#
#         # 3) Pay liabilities (interest first, then principal mode-dependent)
#         ss.makePayments(total_payment, principal_pay)
#
#         # 4) Capture waterfalls
#         asset_side.append({
#             "Period": period,
#             "Interest": float(interest_pay),
#             "Principal": float(principal_pay),
#             "Total": float(total_payment),
#             "ActiveLoans": int(loan_pool.activeLoans(period)),
#             "PoolBalance": float(loan_pool.totalLoanBalance(period)),
#         })
#
#         # Each item is the per-tranche row for this period (ordered by subordination)
#         liability_side.append(ss.getWaterfall())
#
#         period += 1
#
#     return asset_side, liability_side, float(ss._reserveAccount)
