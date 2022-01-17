from ctypes import alignment
from tkinter import CENTER
from urllib import response
from pandas import json_normalize
import streamlit as st
from PIL import Image
import json 
import requests


#ONS Query Functions
def process(obj, ds):
	data = {}
	values  =  obj[ds]['value']
	index = obj[ds]['dimension'][obj[ds]['dimension']['id'][1]]['category']['index']
	labels = obj[ds]['dimension'][obj[ds]['dimension']['id'][1]]['category']['label']
	for l in labels:
		num = index[l]
		count = values[str(num)]
		data[labels[l]] = count
	return data

def getData(): 
    response = requests.get('https://api.beta.ons.gov.uk/v1/datasets/cpih01') 
    if response.getcode() == 200:
        source = response.read()
        data = json.loads(source)
        return data
    else:
        print('An error occurred while attempting to retrieve data from the API.')

response = requests.get('https://api.ons.gov.uk/timeseries/chaw/dataset/mm23/data') 

print(response.json())
print('response above')

st.title('Medics For Pay Restoration')
st.subheader('Calculate Your Pay Cut - England')
st.json(response.json())

from datetime import date
currentDate = date.today()
st.subheader('Year')
slider_time = st.slider(
     "Select Year to Compare to",
     min_value= date(2008, 1, 1),
     max_value= currentDate,
     format="YYYY")
formattedTime = slider_time.strftime("%d/%m/%Y")

st.subheader('Your Grade')
grade = st.selectbox(
     'Select Your Grade',
     ('FY1', 'FY2', 'ST1', 'ST2', 'ST3', 'ST4', 'ST5', 'ST6', 'ST7', 'ST8'))
st.write('Grade:', grade)
st.subheader('Antisocial Commitment')
antisocialHours = st.slider('Number of Antisocial Hours Worked?', 0, 20, 0)
st.subheader('Weekends Worked')
weekendsWorked = st.select_slider(
    '<1:8 = Work One in Eight', 
    options=[ '<1:8', '<1:7 - 1:8', '<1:6 - 1:7', '<1:5 - 1:6', '<1:4 - 1:5', '<1:3 - 1:4', '<1:2 - 1:3', '1:2',])
