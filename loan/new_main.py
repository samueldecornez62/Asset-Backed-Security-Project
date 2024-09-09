'''
This file demonstrates calling our functions from built classes.
It demonstrates different loan types, different asset types, etc..
All called functions can be read in the files contained in this loan folder.
'''

# Import required modules and classes
import logging
from asset_base import Asset
from loan_base import Loan
from loans import FixedRateLoan, VariableRateLoan
from car_class import Car
from house_base import HouseBase
from house_derived_classes import PrimaryHome, VacationHome

# Configure logging to show messages in the console
# Raise this to higher level i.e. ERROR to reduce output clutter
logging.basicConfig(level=logging.ERROR)

def main():
    # Initialize an Asset object
    my_asset = Asset(initial_value=100000)

    # FixedRateLoan example
    loan_face_value = 50000
    fixed_rate = 0.05
    loan_start = '2024-01-01'
    loan_end = '2027-01-01'

    # Create a FixedRateLoan instance
    my_fixed_loan = FixedRateLoan(my_asset, loan_face_value, fixed_rate, loan_start, loan_end)

    period = 12

    logging.info('Fixed Rate Loan')
    print(f'Monthly Payment: {my_fixed_loan.monthlyPmt(period)}')
    print(f'Total Payments: {my_fixed_loan.totalPayments()}')
    print(f'Total Interest: {my_fixed_loan.totalInterest()}')

    # Set a specific period for FixedRateLoan
    fixed_rate_period = 12  # Example period for FixedRateLoan

    try:
        interest_due = my_fixed_loan.interestDue_formula(fixed_rate_period)
        principal_due = my_fixed_loan.principalDue_formula(fixed_rate_period)
        balance = my_fixed_loan.balance_formula(fixed_rate_period)

        if isinstance(interest_due, (int, float)) and isinstance(principal_due, (int, float)) and isinstance(balance, (int, float)):
            print(f'Interest Due at Period {fixed_rate_period}: {interest_due}')
            print(f'Principal Due at Period {fixed_rate_period}: {principal_due}')
            print(f'Balance at Period {fixed_rate_period}: {balance}')
        else:
            print(f'Error: Unexpected result type received for period {fixed_rate_period}.')
    except Exception as ex:
        logging.error(f'An error occurred: {ex}')

    # VariableRateLoan example
    rate_dict = {0: 0.04, 12: 0.045, 24: 0.05}  # Rates change every year
    my_variable_loan = VariableRateLoan(my_asset, loan_face_value, rate_dict, loan_start, loan_end)

    logging.info('Variable Rate Loan')
    print(f'Monthly Payment: {my_variable_loan.monthlyPmt(period)}')
    print(f'Total Payments: {my_variable_loan.totalPayments()}')
    print(f'Total Interest: {my_variable_loan.totalInterest()}')

    # Set a specific period for VariableRateLoan
    variable_rate_period = 24  # Example period for VariableRateLoan

    try:
        interest_due = my_variable_loan.interestDue_formula(variable_rate_period)
        principal_due = my_variable_loan.principalDue_formula(variable_rate_period)
        balance = my_variable_loan.balance_formula(variable_rate_period)

        if isinstance(interest_due, (int, float)) and isinstance(principal_due, (int, float)) and isinstance(balance, (int, float)):
            print(f'Interest Due at Period {variable_rate_period}: {interest_due}')
            print(f'Principal Due at Period {variable_rate_period}: {principal_due}')
            print(f'Balance at Period {variable_rate_period}: {balance}')
        else:
            print(f'Error: Unexpected result type received for period {variable_rate_period}.')
    except Exception as ex:
        logging.error(f'An error occurred: {ex}')


    #==========================================

    # Testing Car class
    car_models = ['Civic', 'Lexus', 'Lambo', 'Toyota', 'Ferrari']
    for model in car_models:
        car = Car(initial_value=30000, model=model)
        logging.info(f'{model} Car')
        print(f'{model} Car Initial Value: {car.initial_value}')
        print(f'{model} Car Depreciation Rate: {car.yearlyDepreciationRate()}')
        print(f'{model} Car Value after 12 months: {car.current_asset_value(12)}')

    # Testing HouseBase class and derived classes
    home_values = {'Primary': 150000, 'Vacation': 100000}
    for purpose, value in home_values.items():
        if purpose == 'Primary':
            home = PrimaryHome(initial_value=value)
        else:
            home = VacationHome(initial_value=value)

        logging.info(f'{purpose} Home')
        print(f'{purpose} Home Initial Value: {home.initial_value}')
        print(f'{purpose} Home Depreciation Rate: {home.yearlyDepreciationRate()}')
        print(f'{purpose} Home Value after 12 months: {home.current_asset_value(12)}')






if __name__ == '__main__':
    main()