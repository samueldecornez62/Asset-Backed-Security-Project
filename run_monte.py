'''
This file creates a global function: runMonte
'''

#Import packages
import math

#Import function
from Tranches.standard_tranche_class import StandardTranche
from simulate_waterfall_function import simulateWaterfall



#Define the calculateYield function
#Input parameters: average DIRR and WAL
def calculateYield(dirr, wal):
    #Break up formula for clarity and to reduce code clutter
    fraction_term = 7 / (1 + 0.08*math.exp(-0.19 * wal/12))
    root_term = 0.019 * (wal*dirr*100/12)**0.5
    answer = (fraction_term + root_term) / 100
    return answer

#Create another method to efficiently calculate updated tranche rates
def newTrancheRate(old_tranche_rate, coeff, yield_value):
    new_tranche_rate = old_tranche_rate + coeff * (yield_value - old_tranche_rate)
    return new_tranche_rate




#Create the function, with input parameters: LoanPool object, StructuredSecurities object, tolerance and NSIM
def runMonte(loan_pool, ss, tolerance, NSIM):
    #The StructuredSecurities object ss must only be given an initial notional
    #In this function we manually assign two tranches of specific rate as base rates (initial guesses)
    ss.addTranche(percent_notional=0.5, rate=0.05, subordination='A', tranche_class=StandardTranche)
    ss.addTranche(percent_notional=0.5, rate=0.08, subordination='B', tranche_class=StandardTranche)

    #This function will then use a yield curve to determine newly adjusted rates until reaching tolerance
    #Begin with infinite loop
    while True:
        #This returns a list of tuples
        #Each index is for a tranche
        #Each value is (average_dirr, WAL) of that tranche over NSIM simulations
        average_metrics = simulateWaterfall(loan_pool=loan_pool, ss=ss, NSIM=NSIM)


        ### We want to update tranches rates based on a formula (see below code for its implementation)
        #It requires a variable to test against our input tolerance, initialized to 0
        aggregate_diff = 0

        #Next step is to calculate yield
        #Define a function above this runMonte, called calculateYield, with inputs average DIRR and WAL
        for i, tranche in enumerate(ss._tranches):
            tranche_tuple = average_metrics[i]
            dirr = tranche_tuple[0] #Read average dirr of tranche
            wal = tranche_tuple[1] #Read WAL of tranche
            #Use calculate yield function
            yield_value = calculateYield(dirr, wal)

            #Assign a coefficient based on subordination
            # These must be set manually, implement future vlues as needed
            if tranche._subordination == 'A':
                coeff = 1.2
            elif tranche._subordination == 'B':
                coeff = 0.8
            else:
                coeff = 1.0

            #Store current rate as "old rate" for calculation
            old_tranche_rate = tranche._rate
            #Use this coeff to compute new rate, using new rate function calculator defined above
            new_tranche_rate = newTrancheRate(old_tranche_rate=tranche._rate, coeff=coeff, yield_value=yield_value)

            #Update tranche rate using ths new rate; this can be done easily thanks to getter/setter class methods
            tranche._rate = new_tranche_rate


            #Lastly, check if the calculated difference is less than epsilon tolerance; if yes break loop
            #See implemented formula below which extends beyond this iteration to outside the loop as well
            diff_component = tranche._notional * abs(new_tranche_rate-old_tranche_rate)/old_tranche_rate

            #At each tranche, add this component in our tolerance analysis formula
            aggregate_diff += diff_component

        #First line of code after looping through tranches
        #Use the aggregate diff from all tranches to now test formula against tolerance
        #Also, StructuredSecurity class has a self parameter for total notional across tranches
        sum_notional = ss._totalNotionalAmount
        diff = aggregate_diff/sum_notional

        #Lastly, break loop if within tolerance; else go back up and repeat rate adjustment process
        if diff < tolerance:
            break



