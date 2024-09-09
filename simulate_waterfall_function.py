'''
This file creates a global function: simulateWaterfall
'''
import logging

#Import function
from Tranches.waterfall_function import doWaterfall




#Create the function, with input parameters: LoanPool object, StructuredSecurities object, NSIM (# simulations)
#This function runs doWaterfall NSIM times, and returns average DIRR and AL from NSIM iterations
# noinspection PyTypeChecker
def simulateWaterfall(loan_pool, ss, NSIM):
    #For every tranche in SS object, we add values here to take an average
    aggregate_al = [0]*len(ss._tranches)
    aggregate_dirr = [0]*len(ss._tranches)
    #Since the number of positions corresponds to number of tranches, also have a counter variable to divide by
    al_counter = [0]*len(ss._tranches)
    dirr_counter = [0]*len(ss._tranches)

    #Run the simulation NSIM times
    for i in range(NSIM):
        #Metric dict can only be computed once per simulation, or default randomness will keep changing (bad)
        _, metric_dict, _ = doWaterfall(loan_pool, ss)
        #For each tranche, accumulate vcalues that contribute to the average computation
        #Try except block ensure the counter only goes up if the value could be added
        # This excludes None value aautomatically as well
        for index, tranche in enumerate(ss._tranches):
            #Read metrics
            tranche_metrics = metric_dict.get(tranche, (None, None, None))
            irr, al, dirr = tranche_metrics
            #Add to average counters for al
            if al is not None:
                aggregate_al[index] += al
                al_counter[index] += 1
            else:
                logging.error(f'Error processing tranche metric al for tranche {tranche}. ')
            #Add to average counters for dirr
            if dirr is not None:
                aggregate_dirr[index] += dirr
                dirr_counter[index] += 1
            else:
                logging.error(f'Error processing tranche metric dirr for tranche {tranche}. ')




    #With lists processed, finally compute and return averages from NSIM simulation
    #We will return a list, with number of values equal to number of tranches
    #This final list will be the average (average_dirr, WAL) tuple at each index
    #First initialize the list
    average_metrics = [None]*len(ss._tranches)
    for index in range(len(average_metrics)):
        try:
            #Calculate the two values; directly avoid 0 if every loan defaulted
            WAL = aggregate_al[index]/al_counter[index] if al_counter[index] > 0 else None
            average_dirr = aggregate_dirr[index]/dirr_counter[index] if dirr_counter[index] > 0 else None
            #Make a tuple of it to slam into list
            the_tuple = (average_dirr, WAL)
            #Replace the initialized None value in average_metrics
            # Note that any Nones in return are failed calculations
            average_metrics[index] = the_tuple
        except Exception as ex:
            logging.error(f'Error computing computations. WAL and average DIRR not proccessed correctly: {ex}')






    return average_metrics