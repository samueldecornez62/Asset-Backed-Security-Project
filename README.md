## Asset Backed Security Model Project Background

This project is my attempt at creating an Asset Backed Security model. The base for this project was given by a course at ScriptUni. 

I intend to continue building my own functionality to further improve this model. 


This project consists of two major parts: 

- The first is building a loan class which allows us to initialize Loan objects. Through various derived classes, more functionality is added to these loan objects. 
- For example, loans can be either fixed or variable rate. 
- The loan folder also includes an Asset base class, which creates Asset objects to initialize any Loan object with. 
- The Asset derived classes can initialize Car objects, House objects (Vacation or Primary home for example), and I hope to add more Asset types to be initialized into Loan objects in the future.


- The next major section of the project is the Tranche folder. It creates a base Tranche class, initialized with a notional, a rate, and a subordination tag. 
- Tranches are ordered by subordination lexicographically for processing payments. 
- It also includes a StandardTranche class (more tranche types to come in future!), and a StructurdSecurities class, which is a composition of Tranche objects. 
- This culminates in the waterfall function, which is intended to display Interest Due, Interest Paid, Interest Shortfall, Principal Paid, and Balance, at each period, and for each tranche in the StructuredSecurities object. 
- Additionaly, waterfall metrics (Internal Rate of Return, Average life, Reduction in Yield) are displayed at the end of the waterfall, as well some loan default information. 
