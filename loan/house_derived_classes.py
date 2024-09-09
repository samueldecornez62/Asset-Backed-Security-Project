'''
Samuel Decornez
This module contains classes derived from HouseBase.
'''




'''================================================
Main Program:
This program will create the derived House classes.
================================================'''


#Import class we are deriving this from
from house_base import HouseBase
from asset_base import Asset


#Create PrimaryHome class, derived from HouseBase
class PrimaryHome(HouseBase):
    #Initialization function
    def __init__(self, initial_value):
        #Call superclass; must inherit initial value from asset, home_purpose from house base
        super(PrimaryHome, self).__init__(initial_value, home_purpose='Primary')


#Repeat exact same as above, for VacationHome
class VacationHome(HouseBase):
    #Initialization function
    def __init__(self, initial_value):
        #Call superclass; must inherit initial value from asset, home_purpose from house base
        super(VacationHome, self).__init__(initial_value, home_purpose='Vacation')

