from ctypes import alignment
from tkinter import CENTER
from urllib import response
from pandas import json_normalize
import streamlit as st
from PIL import Image
import json 
import requests
from dateutil.relativedelta import relativedelta

# Get RPI Data 
def getRPI(yearSelected): 
    response = requests.get('https://api.ons.gov.uk/timeseries/chaw/dataset/mm23/data') 
    jsonData = response.json()
    rpiYears = jsonData["years"]
    induvidualYear = rpiYears[yearSelected - 1987]
    rpi = induvidualYear["value"]
    return rpi

def getPayData(yearSelected, gradeSelected): 
    response = requests.get('https://raw.githubusercontent.com/BarkingTree/PythonPayCalculator/master/englandPay.json') 
    jsonData = response.json()
    payYears = jsonData["Years"]
    induvidualYear = payYears[yearSelected]
    pay = induvidualYear[gradeSelected]
    return pay

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
st.subheader('Antisocial Hours')
antisocialHoursOld = st.slider('Hours worked outside of Monday - Friday 07:00 - 19:00 ?', 0, 20, 0)
antisocialHoursNew = st.slider('Of these how many are outside of Monday - Friday 07:00 - 21:00 ?', 0, 20, 0)

st.subheader('Weekends Worked')
weekendsWorked = st.select_slider(
    '<1:8 = Work One in Eight Weekends', 
    options=[ '<1:8', '<1:7 - 1:8', '<1:6 - 1:7', '<1:5 - 1:6', '<1:4 - 1:5', '<1:3 - 1:4', '<1:2 - 1:3', '1:2',])

st.write(getRPI(slider_year_selected.year))
st.write(getPayData(2008, 'FY1'))