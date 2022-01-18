from ctypes import alignment
from nis import match
from tkinter import CENTER
from unittest import case
from urllib import response
from pandas import json_normalize
import streamlit as st
from PIL import Image
import json 
import requests
from dateutil.relativedelta import relativedelta
import sys;print(sys.version)

# See Excel CalculationFile for Calculation Details
antiocialEnhancementPerHour = 0.00925
additionalHourEnhancement = 0.025

# Get RPI Data 
def getRPI(yearSelected): 
    response = requests.get('https://api.ons.gov.uk/timeseries/chaw/dataset/mm23/data') 
    jsonData = response.json()
    rpiYears = jsonData["years"]
    induvidualYear = rpiYears[yearSelected - 1987]
    rpi = induvidualYear["value"]
    return rpi

# Get Pay Data from GitHub Repo
def getPayData(yearSelected, gradeSelected): 
    response = requests.get('https://raw.githubusercontent.com/BarkingTree/PythonPayCalculator/master/englandPay.json') 
    jsonData = response.json()
    induvidualYear = jsonData[str(yearSelected)]
    pay = induvidualYear[gradeSelected]
    return pay

def currentPay(yearSelected, gradeSelected, weekendsWorked = '<1:8'): 
    weekendMultiplier = 0
    match weekendsWorked: 
        case '<1:8': 
            weekendMultiplier = 0
        case '<1:7 - 1:8':
             weekendMultiplier = 0.03
        case '<1:6 - 1:7': 
            weekendMultiplier = 0.04
        case '<1:5 - 1:6': 
            weekendMultiplier = 0.05
        case '<1:4 - 1:5': 
            weekendMultiplier = 0.06
        case '<1:3 - 1:4': 
            weekendMultiplier = 0.075
        case '<1:2 - 1:3': 
            weekendMultiplier = 0.10
        case '1:2':
            weekendMultiplier = 0.15
    basePay = getPayData(yearSelected, gradeSelected)
    antisocialPay = basePay * (antisocialHours * antiocialEnhancementPerHour) 
    additionalHoursPay = basePay * ((hoursWorked - 40) * additionalHourEnhancement)
    weekedPay = basePay * weekendMultiplier
    totalPayRaw = basePay + additionalHoursPay + antisocialPay + weekedPay
    totalPayRounded = round(totalPayRaw)
    return totalPayRounded

with st.container():
    st.title('Medics For Pay Restoration')
    st.subheader('Calculate Your Pay Cut - England')
    
from datetime import date
currentDate = date.today()
st.subheader('Year')
slider_year_selected = st.slider(
     "Select Year to Compare to",
     min_value= date(2008, 1, 1),
     max_value= currentDate - relativedelta(years= 1, days=19),
     # Change to month = 1 on release
     format="YYYY")

st.subheader('Your Grade')
grade = st.selectbox(
     'Select Your Grade',
     ('FY1', 'FY2', 'ST1', 'ST2', 'ST3', 'ST4', 'ST5', 'ST6', 'ST7', 'ST8'))

st.write('Grade:', grade)
st.subheader('Hours')
hoursWorked = st.slider('Total Hours Worked', 40, 48, 40)
antisocialHours = st.slider('Hours Worked Outside of Monday - Friday 07:00 - 21:00 ?', 0, 20, 0)

st.subheader('Weekends Worked')
weekendsWorked = st.select_slider(
    '<1:8 = Work One in Eight Weekends', 
    options=[ '<1:8', '<1:7 - 1:8', '<1:6 - 1:7', '<1:5 - 1:6', '<1:4 - 1:5', '<1:3 - 1:4', '<1:2 - 1:3', '1:2'])

st.write(getRPI(slider_year_selected.year))
st.write(getPayData(2021, grade))
st.write(currentPay(2021, grade))