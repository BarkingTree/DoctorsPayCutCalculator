from ctypes import alignment
from nis import match
from pickle import TRUE
from tkinter import CENTER
from turtle import color
from unicodedata import decimal
from unittest import case
from urllib import response
from nbformat import write
from numpy import inf
from pandas import json_normalize
import streamlit as st
from PIL import Image
import json 
import requests
from dateutil.relativedelta import relativedelta
import numpy as np

# See Excel CalculationFile for Calculation Details 
antiocialEnhancementPerHour = 0.00925
additionalHourEnhancement = 0.025
nrocMultiplier = 0.08
ltft = False

def weekendAllowance(yearSelected): 
    response = requests.get('https://raw.githubusercontent.com/BarkingTree/PythonPayCalculator/master/englandPay.json') 
    jsonData = response.json()
    induvidualYear = jsonData[str(yearSelected)]
    allowance = induvidualYear['WeekendAllowance']
    return allowance

# Get RPI Data and Cache It
@st.cache
def getRPIJSON(inflationMeasure): 
    if inflationMeasure == 'RPI': 
        response = requests.get('https://api.ons.gov.uk/timeseries/chaw/dataset/mm23/data') 
    if inflationMeasure == 'CPIH': 
        response = requests.get('https://api.ons.gov.uk/timeseries/L522/dataset/mm23/data')
    jsonData = response.json()
    rpiYears = jsonData["years"]
    return rpiYears

def getRPI(yearSelected, inflationMeasure): 
    indexAdjustment = 0 
    # Adjust for Year Indexes Started
    if inflationMeasure == 'RPI': 
        indexAdjustment = 1987
    if inflationMeasure == 'CPIH': 
        indexAdjustment = 1988
    rpiYears = getRPIJSON(inflationMeasure)
    induvidualYear = rpiYears[yearSelected - indexAdjustment]
    rpi = induvidualYear["value"]
    return rpi

# Get Pay Data from GitHub Repo
def getPayData(yearSelected, gradeSelected): 
    response = requests.get('https://raw.githubusercontent.com/BarkingTree/PythonPayCalculator/master/englandPay.json') 
    jsonData = response.json()
    induvidualYear = jsonData[str(yearSelected)]
    pay = induvidualYear[gradeSelected]
    return pay

def currentPay(yearSelected, gradeSelected, nroc, ltft, weekendsWorked = '<1:8'): 

    weekAllowance = weekendAllowance(yearSelected)
    basePay = getPayData(yearSelected, gradeSelected)
    resultsArray = []
    # Caluclate Pay if < 40 Hours Per Week
    if ltft == True:
        percentageWorked = hoursWorked / 40
        oneHourPay = basePay / 40
        ltftPay = round(oneHourPay * hoursWorked)
        ltftAllowance = 1000
        if weekendsWorked == '<1:8': 
            weekendMultiplier = weekAllowance[0]
        if weekendsWorked == '<1:7 - 1:8':
            weekendMultiplier = weekAllowance[1]
        if weekendsWorked == '<1:6 - 1:7': 
            weekendMultiplier = weekAllowance[2]
        if weekendsWorked == '<1:5 - 1:6': 
            weekendMultiplier = weekAllowance[3]
        if weekendsWorked == '<1:4 - 1:5': 
            weekendMultiplier = weekAllowance[4]
        if weekendsWorked == '<1:3 - 1:4': 
            weekendMultiplier = weekAllowance[5]
        if weekendsWorked == '<1:2 - 1:3': 
            weekendMultiplier = weekAllowance[6]
        if weekendsWorked == '1:2':
            weekendMultiplier = weekAllowance[7]
        if nroc: 
            nrocPay = (nrocMultiplier * basePay) * percentageWorked
        else:
            nrocPay = 0
        
        additionalHoursPay = 0
        antisocialPay = basePay * (antisocialHours * antiocialEnhancementPerHour) 
        weekendPay = (basePay * (weekendMultiplier / 100 )) * percentageWorked    
        totalPayRaw = ltftPay + antisocialPay + weekendPay + nrocPay + ltftAllowance
        totalPayRounded = round(totalPayRaw)
        resultsArray = [totalPayRounded, ltftPay, antisocialPay, additionalHoursPay, weekendPay, nrocPay, ltftAllowance]
        return resultsArray
    elif ltft == False: 
         # Caluclate Pay if > 40 Hours Per Week
        # Unable to Use Match due to Streamlit Requiring Python 3.9 or Older. Review if Streamlit adds support for Python 3.10
        if weekendsWorked == '<1:8': 
            weekendMultiplier = weekAllowance[0]
        if weekendsWorked == '<1:7 - 1:8':
            weekendMultiplier = weekAllowance[1]
        if weekendsWorked == '<1:6 - 1:7': 
            weekendMultiplier = weekAllowance[2]
        if weekendsWorked == '<1:5 - 1:6': 
            weekendMultiplier = weekAllowance[3]
        if weekendsWorked == '<1:4 - 1:5': 
            weekendMultiplier = weekAllowance[4]
        if weekendsWorked == '<1:3 - 1:4': 
            weekendMultiplier = weekAllowance[5]
        if weekendsWorked == '<1:2 - 1:3': 
            weekendMultiplier = weekAllowance[6]
        if weekendsWorked == '1:2':
            weekendMultiplier = weekAllowance[7]
        if nroc: 
            nrocPay = nrocMultiplier * basePay
        else:
            nrocPay = 0
        antisocialPay = basePay * (antisocialHours * antiocialEnhancementPerHour) 
        additionalHoursPay = basePay * ((hoursWorked - 40) * additionalHourEnhancement)
        weekendPay = basePay * (weekendMultiplier / 100)
        totalPayRaw = basePay + additionalHoursPay + antisocialPay + weekendPay + nrocPay
        totalPayRounded = round(totalPayRaw)
        resultsArray = [totalPayRounded, basePay, antisocialPay, additionalHoursPay, weekendPay, nrocPay, 0]
        return resultsArray

def oldPay(yearSelected, gradeSelected, hours, antiSocialHours, ltft, weekendsWorked): 
    percentAntiSocialHours = antiSocialHours / hours
    basePay = getPayData(yearSelected, gradeSelected)
    resultsArray = []
    banding = 0 
    # Caluclate Pay if < 40 Hours Per Week
    if ltft == True:
        worksOneinSixWeekends = False
        baseSalaryBanding = 0 
        percentageWorked = int((hours / 40) * 100)
        if percentageWorked in range(50, 59): 
            baseSalaryBanding = 0.5
        if percentageWorked in range(60, 69): 
            baseSalaryBanding = 0.6  
        if percentageWorked in range(70, 79): 
            baseSalaryBanding = 0.7
        if percentageWorked in range(80, 89): 
            baseSalaryBanding = 0.8
        if percentageWorked in range(90, 99): 
            baseSalaryBanding = 0.9             
        if weekendsWorked == '<1:8': 
            worksOneinSixWeekends = False
        if weekendsWorked == '<1:7 - 1:8':
            worksOneinSixWeekends = False
        if weekendsWorked == '<1:6 - 1:7': 
            worksOneinSixWeekends = False
        if weekendsWorked == '<1:5 - 1:6': 
           worksOneinSixWeekends = True
        if weekendsWorked == '<1:4 - 1:5': 
            worksOneinSixWeekends = True
        if weekendsWorked == '<1:3 - 1:4': 
            worksOneinSixWeekends = True
        if weekendsWorked == '<1:2 - 1:3': 
            worksOneinSixWeekends = True
        if weekendsWorked == '1:2':
           worksOneinSixWeekends = True
        if worksOneinSixWeekends or percentAntiSocialHours > 0.33: 
            #Band FA
            banding = 1.5
        elif percentAntiSocialHours > 0:
            #Band FB 
            banding = 1.4
        elif percentAntiSocialHours == 0: 
            banding = 1.2
        bandedBasePay = basePay * baseSalaryBanding
        totalPayRaw = bandedBasePay * banding
        totalPayRounded = round(totalPayRaw)
        resultsArray = [totalPayRounded, round(bandedBasePay), banding]
    
    if ltft == False:
        worksOneInFourWeekends = False
        if weekendsWorked == '<1:8': 
            worksOneInFourWeekends = False
        if weekendsWorked == '<1:7 - 1:8':
            worksOneInFourWeekends = False
        if weekendsWorked == '<1:6 - 1:7': 
            worksOneInFourWeekends = False
        if weekendsWorked == '<1:5 - 1:6': 
           worksOneInFourWeekends = False
        if weekendsWorked == '<1:4 - 1:5': 
            worksOneInFourWeekends = False
        if weekendsWorked == '<1:3 - 1:4': 
            worksOneInFourWeekends = True
        if weekendsWorked == '<1:2 - 1:3': 
            worksOneInFourWeekends = True
        if weekendsWorked == '1:2':
           worksOneInFourWeekends = True
        if worksOneInFourWeekends or percentAntiSocialHours > 0.33: 
            #Band 1A
            banding = 1.5
        elif percentAntiSocialHours > 0:
            #Band 1B 
            banding = 1.4
        elif percentAntiSocialHours == 0: 
            # Band 1C. Likely to require rework
            banding = 1.2
        totalPayRaw = basePay * banding
        totalPayRounded = round(totalPayRaw)
        resultsArray = [totalPayRounded, round(basePay) ,banding]
    return resultsArray

with st.container():
    st.title('Medics For Pay Restoration')
    st.subheader('Calculate Your Pay Cut - England')
    
from datetime import date
currentDate = date.today()
adjustedDate = currentDate - relativedelta(years= 1, days=19)
st.subheader('Select Inflation Year')
slider_year_selected = st.slider(
     "Select Year to Compare to",
     min_value= date(2008, 1, 1),
     max_value= adjustedDate ,
     # Change to month = 1 on release
     format="YYYY")

inflationMeasure = st.selectbox(
    'Inflation Measure',
    ('RPI', 'CPIH')
)
st.subheader('Your Grade')
grade = st.selectbox(
     'Select Your Grade',
     ('FY1', 'FY2', 'ST1', 'ST2', 'ST3', 'ST4', 'ST5', 'ST6', 'ST7', 'ST8'))

st.subheader('Hours')
hoursWorked = st.slider('Total Hours Worked Per Week', 20, 48, 40)
if hoursWorked < 40:
    ltft = True 
antisocialHours = st.slider('Hours Worked Outside of 07:00 - 21:00 (2016 Contract Antisocial)?', 0, 20, 0)
antisocialHoursOld = st.slider('Hours Worked Outside of 07:00 - 19:00 (2002 Contract Antisocial)?', 0, 20, 0)
st.write('Do you recieve the Non-Resident On Call Supplement?')
nroc = st.checkbox('Non-Resident On Call')

st.subheader('Weekends Worked')
if ltft == True: 
    st.write('Please Select the number of Weekends you would work if working Full-Time')
weekendsWorked = st.select_slider(
    '<1:8 = Work One in Eight Weekends', 
    options=[ '<1:8', '<1:7 - 1:8', '<1:6 - 1:7', '<1:5 - 1:6', '<1:4 - 1:5', '<1:3 - 1:4', '<1:2 - 1:3', '1:2'])

#Change on Release
currentInflation = getRPI(adjustedDate.year, inflationMeasure)
selectedInflation = getRPI(slider_year_selected.year, inflationMeasure)
inflationChange = float(currentInflation) - float(selectedInflation)
payArray = currentPay(adjustedDate.year, grade, nroc, ltft ,weekendsWorked)
if slider_year_selected < date(2017, 1, 1): 
    payArrayOld = oldPay(slider_year_selected.year, grade, hoursWorked, antisocialHoursOld, ltft, weekendsWorked)
elif slider_year_selected > date(2017, 1, 1):
    payArrayOld = currentPay(slider_year_selected.year, grade, nroc, ltft ,weekendsWorked)
inflationPercentage = float(currentInflation) / float(selectedInflation)
inflationPercentageDisplay = round(inflationPercentage * 100)
oldPayWithInflation = payArrayOld[0] * inflationPercentage

relativePayLoss = round(payArray[0] - oldPayWithInflation)
percentageLoss = round(relativePayLoss / payArray[0] * 100)
change = ""
if oldPayWithInflation < payArray[0]: 
    change = "+Gain"
elif oldPayWithInflation > payArray[0]:
    change = "-Loss"

col1, col2, col3 = st.columns(3)
with col1:
    st.metric('Pay Loss', f'£{relativePayLoss}', change)
with col2:
     st.metric(f'{slider_year_selected.year} Pay Adjusted For Inflation', f'£{round(oldPayWithInflation)}')
with col3: 
     st.metric(f'{adjustedDate.year}', f'£{payArray[0]}', f'{percentageLoss}%')
col1, col2 = st.columns(2)

with col1:
    if slider_year_selected < date(2017, 1, 1): 
        st.subheader(f'{slider_year_selected.year}')
        st.subheader(f'Your Pay: £{payArrayOld[0]}')
        st.write(f'Base Pay: £{payArrayOld[1]}')
        st.write(f'Your Banding: {payArrayOld[2]}')
        st.write('Based of the 2002 Contract')
    if slider_year_selected > date(2017, 1, 1):
        st.subheader(f'{slider_year_selected.year}')
        st.subheader(f'Your Pay: £{round(payArrayOld[0])}')
        st.write(f'Base Pay: £{round(payArrayOld[1])}')
        st.write(f'Antisocial Hours Supplement: £{round(payArrayOld[2])}')
        if ltft == False: 
            st.write(f'Supplement for > 40 Hours Per Week £{round(payArrayOld[3])}')
            st.write(f'Weekend Supplement: £{round(payArrayOld[4])}')
            st.write(f'Non Resident On Call Supplement: £{round(payArrayOld[5])}')
            if ltft == True: 
                st.write(f'Less Than Full Time Allowance: £{round(payArrayOld[6])}')
            

with col2: 
    st.subheader(f'{adjustedDate.year}')
    st.subheader(f'Your Pay: £{payArray[0]}')
    st.write(f'Base Pay: £{payArray[1]}')
    st.write(f'Antisocial Hours Supplement: £{round(payArray[2])}')
    if ltft == False: 
        st.write(f'Supplement for > 40 Hours Per Week £{round(payArray[3])}')
    st.write(f'Weekend Supplement: £{round(payArray[4])}')
    st.write(f'Non Resident On Call Supplement: £{round(payArray[5])}')
    if ltft == True: 
        st.write(f'Less Than Full Time Allowance: £{round(payArray[6])}')

