'''
Samuel Decornez
This module contains the edited Asset base class.
'''




'''======================================
Main Program:
This program will create the Asset class.
======================================'''



#Create the Asset class to save initial asset value upon object initialization
class Asset(object):
    #Define initialization function
    def __init__(self, initial_value):
        self.initial_value = initial_value

    #Method to return yearly depreciation rate
    def yearlyDepreciationRate(self):
        #Edited version of asset class copied from previous section
        #Raise the not-implemented error; can be overridden by derived classes
        raise NotImplementedError()






    #Method to calculate monthly depreciation rate from yearly depreciation rate
    def monthlyDepreciationRate(self):
        #Read yearly depreciation rate
        yearly_rate = self.yearlyDepreciationRate()
        #Convert to monthly
        monthly_rate = yearly_rate/12
        #Return monthly depreciation rate
        return monthly_rate


    #Create method to calculate current value of asset
    def current_asset_value(self, period):
        total_depreciation = (1 - self.monthlyDepreciationRate())**period
        return self.initial_value * total_depreciation