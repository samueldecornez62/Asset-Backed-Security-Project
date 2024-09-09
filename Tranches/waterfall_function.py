'''
This is a standalone function called doWaterfall. This populates data across periods.
'''

### Standalone function, not necessary to do all imports, just kept from random testing for easier access
### if this needs to come back


# #Import modules
# import logging
# from loan.loan_base import Loan
# from loan.loan_pool import LoanPool
# from loan.asset_base import Asset
#
#
# logging.getLogger().setLevel(logging.DEBUG)
#
# #Import oother classes in case we need them
# from base_tranche_class import Tranche
# from standard_tranche_class import StandardTranche
# from structured_securities_class import StructuredSecurities
#
# #Loan imports
# from loan.loan_base import Loan
# from loan.loan_pool import LoanPool






#Create the function
#Can set payment flag before function call and it iwll work
#It loops through all possible time periods and calculates some parameters
def doWaterfall(loan_pool, ss):
    #Initialize a rreturn list
    result_list = []


    # Initialize a sum to aggregate recovery value of defaulted loans
    defaulted_loan_recovery_amount = 0


    #First, find the max loan term so we can loop through it all
    max_term = max(loan.term() for loan in loan_pool)
    #Increase time period on all tranches together at end of this loop
    for period in range(1, max_term+1):
        #Incease time period to move to next one and continue looping through periods
        #This begins at period 1, which makes sense since period 0 has no payment anyways
        ss.increaseTime(num_increases=1)
        # Check for any defaulted loans and get the recovery amount
        period_recovery = loan_pool.checkDefaults(period=period)
        defaulted_loan_recovery_amount += period_recovery

        #Ask loan pool for its total payment at current time period
        #This amount will be the input into getWaterfall method call for tranche payout
        total_loan_balance = loan_pool.total_loan_balance(period=period)
        #Make payments on this period; this will return the list of lists from waterfall
        ss.makePayments(cash_amount=total_loan_balance)
        current_waterfall = ss.getWaterfall(period=period)
        print(f'Period {period}: {current_waterfall}')
        result_list.append(current_waterfall)

    #For each tranche in structured securities object, find the (IRR, DIRR, AL) metrics tuple
    #Initialize a dict to store the metric tuple for each tranche
    metric_dict = {}
    for tranche in ss:
        #Read relevant payments
        principal_payments = tranche._principalPayments
        interest_payments = tranche._interestPayments
        # Store results in a list, 0 when no value can be read from dictionaries (i.e. no payment registered)
        principal_payment_list = [principal_payments.get(period, 0) for period in range(1, max_term + 1)]
        interest_payment_list = [interest_payments.get(period, 0) for period in range(1, max_term + 1)]
        total_payment_list = [p+i for p,i in zip(principal_payment_list, interest_payment_list)]

        ## Calculate metrics
        #For IRR we want interest and principal payments to count
        irr = tranche.IRR(total_payment_list)
        al = tranche.AL(principal_payment_list)
        dirr = tranche.DIRR(total_payment_list)

        #Store in tuple for return dict, but print nice message for metrics separately
        metric_tuple = (irr, al, dirr)

        #Store values
        metric_dict[tranche] = metric_tuple

        #Print result to output
        print(f'Tranche {tranche}: IRR = {irr}, AL = {al}, DIRR = {dirr}')


    # Print recovered value from defaulted loans at end
    print(f'Total recovery value from defaulted loans: {defaulted_loan_recovery_amount}')


    return result_list, metric_dict, defaulted_loan_recovery_amount
    #List of list of lists; waterfall parameters for each tranche, at each period