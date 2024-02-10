# PythonPayCalculator

This is a cimple calculator using Streamlit and Python to determine the pay cut faced by UK NHS Doctors since 2008. 
It pulls RPI and CPIH indexes from the Office for National Statistics and uses these to compare the change in doctor's pay to inflation. 
Pay Data is read from a JSON file for each country. This is hosted on this GitHub Repositry. These have been created based on the base pay levels recorded in the relevant NHS Medicine Pay Circulars.
Weekend Allowances are also read of the JSON File due to alterations made in 2018 to their value. This is only applicable for those on the 2016 Junior Doctor Contract.
