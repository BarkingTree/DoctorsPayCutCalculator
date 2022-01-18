from ctypes import alignment
from nis import match
from tkinter import CENTER
from turtle import color
from unittest import case
from urllib import response
from numpy import inf
from pandas import json_normalize
import streamlit as st
from PIL import Image
import json 
import requests
from dateutil.relativedelta import relativedelta

# See Excel CalculationFile for Calculation Details
antiocialEnhancementPerHour = 0.00925
additionalHourEnhancement = 0.025
nrocMultiplier = 0.08

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

def currentPay(yearSelected, gradeSelected, nroc, weekendsWorked = '<1:8'): 
    weekendMultiplier = 0
    basePay = getPayData(yearSelected, gradeSelected)
    # Unable to Use Match due to Streamlit Requiring Python 3.9 or Older. Review if Streamlit adds support for Python 3.10
    if weekendsWorked == '<1:8': 
        weekendMultiplier = 0
    if weekendsWorked == '<1:7 - 1:8':
        weekendMultiplier = 0.03
    if weekendsWorked == '<1:6 - 1:7': 
        weekendMultiplier = 0.04
    if weekendsWorked == '<1:5 - 1:6': 
        weekendMultiplier = 0.05
    if weekendsWorked == '<1:4 - 1:5': 
        weekendMultiplier = 0.06
    if weekendsWorked == '<1:3 - 1:4': 
        weekendMultiplier = 0.075
    if weekendsWorked == '<1:2 - 1:3': 
        weekendMultiplier = 0.10
    if weekendsWorked == '1:2':
        weekendMultiplier = 0.15
    if nroc: 
        nrocPay = nrocMultiplier * basePay
    else:
        nrocPay = 0
    antisocialPay = basePay * (antisocialHours * antiocialEnhancementPerHour) 
    additionalHoursPay = basePay * ((hoursWorked - 40) * additionalHourEnhancement)
    weekendPay = basePay * weekendMultiplier
    totalPayRaw = basePay + additionalHoursPay + antisocialPay + weekendPay + nrocPay
    totalPayRounded = round(totalPayRaw)
    return totalPayRounded, antisocialPay, additionalHoursPay, weekendPay, nrocPay

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
hoursWorked = st.slider('Total Hours Worked Per Week', 40, 48, 40)
antisocialHours = st.slider('Hours Worked Outside of Monday - Friday 07:00 - 21:00 ?', 0, 20, 0)
st.write('Are you on the Non-resident on-call rota')
nroc = st.checkbox('Non-Resident On Call')

st.subheader('Weekends Worked')
weekendsWorked = st.select_slider(
    '<1:8 = Work One in Eight Weekends', 
    options=[ '<1:8', '<1:7 - 1:8', '<1:6 - 1:7', '<1:5 - 1:6', '<1:4 - 1:5', '<1:3 - 1:4', '<1:2 - 1:3', '1:2'])

#Change on Release
currentInflation = getRPI(adjustedDate.year, inflationMeasure)
selectedInflation = getRPI(slider_year_selected.year, inflationMeasure)
inflationChange = float(currentInflation) - float(selectedInflation)
basePay = getPayData(2021, grade)
totalPay = str(currentPay(2021, grade, nroc, weekendsWorked)[0])
st.header(f'Your Pay: £{totalPay}')
st.write(f'Base Pay: £{basePay}')
st.write(f'Antisocial Hours Supplement: £{currentPay(2021, grade, nroc, weekendsWorked)[1]}')
st.write(f'Additional Hours (> 40Hour Week) Supplement £{currentPay(2021, grade, nroc, weekendsWorked)[2]}')
st.write(f'Weekend Supplement: £{currentPay(2021, grade, nroc, weekendsWorked)[3]}')
st.write(f'Non Resident On Call Supplement: £{currentPay(2021, grade, nroc, weekendsWorked)[4]}')

st.write(getPayData(2021, grade))
st.write(currentPay(2021, grade, nroc, weekendsWorked)[0])
st.metric(label = f"Inflation {inflationMeasure}", value = f'{currentInflation}', delta = f'{round(inflationChange)}')