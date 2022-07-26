from email.mime import base
from nis import match
from urllib import response
import streamlit as st
from PIL import Image
import json 
import requests
from dateutil.relativedelta import relativedelta
import numpy as np

st.set_page_config('Pay Calculator', page_icon=' 🩺')

# See Excel CalculationFile for Calculation Details 
antiocialEnhancementPerHour = 0.00925
additionalHourEnhancement = 0.025
nrocMultiplier = 0.08
ltft = False

# Dates 
from datetime import date, timedelta
currentDate = date.today()
yearsPost2022 = date.today().year - 2022
# Alter to Allow data from later than 2022
maxYear = currentDate - relativedelta(years= yearsPost2022, months= 3, weeks=4)

# Prevents adjusted Date from going past 2022. This allows access to Quartely inflation figures 
# but prevents applciation attempting to parse Pay JSON when no data is avaliable. 
# ONS Appears to release data the Penultimate Wednesday of every Month. 

# Formally was adjustedDate = currentDate - relativedelta(years = 1, months = 0)

def weekendAllowance(yearSelected): 
    response = requests.get('https://raw.githubusercontent.com/BarkingTree/PythonPayCalculator/master/englandPay.json') 
    jsonData = response.json()
    induvidualYear = jsonData[str(yearSelected)]
    allowance = induvidualYear['WeekendAllowance']
    return allowance

# Get RPI / CPIH Data and Cache It
@st.cache
def getInflationJSON(inflationMeasure): 
    if inflationMeasure == 'RPI': 
        response = requests.get('https://api.ons.gov.uk/timeseries/chaw/dataset/mm23/data') 
    if inflationMeasure == 'CPIH': 
        response = requests.get('https://api.ons.gov.uk/timeseries/L522/dataset/mm23/data')
    jsonData = response.json()
    inflationYears = jsonData["years"]
    inflationQuarters = jsonData["quarters"]
    return inflationQuarters

def getInflationIndex(date, inflationMeasure): 
    adjustedArrayIndex = 0 
    # Adjust for Years Indexes Started
    if inflationMeasure == 'RPI': 
        adjustedArrayIndex = (((date.year - 1986) * 4) - 4) + ((date.month-1)//3)
    if inflationMeasure == 'CPIH': 
        adjustedArrayIndex = (((date.year - 1987) * 4) - 4) + ((date.month-1)//3)
    inflationArray = getInflationJSON(inflationMeasure)
    induvidualQuarter = inflationArray[adjustedArrayIndex]
    inflationIndex = induvidualQuarter["value"]
    return inflationIndex

# Get Pay Data from GitHub Repo
def getPayData(yearSelected, gradeSelected, country): 
    if country == 'England': 
        response = requests.get('https://raw.githubusercontent.com/BarkingTree/PythonPayCalculator/master/englandPay.json') 
    elif country == 'Scotland':
        response = requests.get('https://raw.githubusercontent.com/BarkingTree/PythonPayCalculator/master/scotlandPay.json')
    elif country == 'Wales':
        response = requests.get('https://raw.githubusercontent.com/BarkingTree/PythonPayCalculator/master/walesPay.json')
    elif country == 'Northern Ireland':
        response = requests.get('https://raw.githubusercontent.com/BarkingTree/PythonPayCalculator/master/niPay.json')   
    jsonData = response.json()
    induvidualYear = jsonData[str(yearSelected)]
    pay = induvidualYear[gradeSelected]
    return pay

def payNewContract(yearSelected, gradeSelected, hoursWorkedLocal, nroc, ltft, country, antisocialHoursLocal, weekendsWorked = '<1:8',): 
    weekAllowance = weekendAllowance(yearSelected)
    basePay = getPayData(yearSelected, gradeSelected, country)
    resultsArray = []
    # Caluclate Pay if < 40 Hours Per Week
    if ltft == True:
        percentageWorked = hoursWorkedLocal / 40
        oneHourPay = basePay / 40
        ltftPay = round(oneHourPay * hoursWorkedLocal)
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
        antisocialPay = basePay * (antisocialHoursLocal * antiocialEnhancementPerHour) 
        additionalHoursPay = basePay * ((hoursWorkedLocal - 40) * additionalHourEnhancement)
        weekendPay = basePay * (weekendMultiplier / 100)
        totalPayRaw = basePay + additionalHoursPay + antisocialPay + weekendPay + nrocPay
        totalPayRounded = round(totalPayRaw)
        resultsArray = [totalPayRounded, basePay, antisocialPay, additionalHoursPay, weekendPay, nrocPay, 0]
        return resultsArray

def payOldContract(yearSelected, gradeSelected, hours, antiSocialHours, ltft, country, weekendsWorked, manualBinding, manuallySelectedBinding): 
    percentAntiSocialHours = antiSocialHours / hours
    basePay = getPayData(yearSelected, gradeSelected, country)
    resultsArray = []
    banding = 0 
    bandingString = ""
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
            bandingString = 'FA'
        elif percentAntiSocialHours > 0.15:
            #Band FB 
            banding = 1.4
            bandingString = 'FB'
        elif percentAntiSocialHours > 0: 
            # Banding FC
            banding = 1.2
            bandingString = 'FC'
        elif percentAntiSocialHours == 0:
            # Unbanded
            banding = 1
            bandingString = 'Unbanded'
        # Ovverride if Manually Selecting Binding
        if manualBinding == True:
            if manuallySelectedBinding == 'FA': 
                banding = 1.5
                bandingString = 'FA'
            elif manuallySelectedBinding == 'FB':
                banding = 1.4
                bandingString = 'FB'
            elif manuallySelectedBinding == 'FC':
                banding = 1.2
                bandingString = 'FC'
            elif manuallySelectedBinding == 'Unbanded':
                banding = 1
                bandingString = 'Unbanded'
        bandedBasePay = basePay * baseSalaryBanding
        totalPayRaw = bandedBasePay * banding
        totalPayRounded = round(totalPayRaw)
        resultsArray = [totalPayRounded, round(bandedBasePay), banding, bandingString]
    
    if ltft == False:
        if manualBinding == False:
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
                bandingString = '1A'
            elif percentAntiSocialHours > 0.15:
                #Band 1B 
                banding = 1.4
                bandingString = '1B'
            elif hours > 40:
                # Band 1C. Likely to require rework
                banding = 1.2
                bandingString = '1C'
            elif hours == 40:
                # Unbanded only applies to those completing 40 Hour weeks.
                banding = 1
                bandingString = 'Unbanded'
       
        if manualBinding == True:
            if manuallySelectedBinding == '1A': 
                banding = 1.5
                bandingString = '1A'
            elif manuallySelectedBinding == '1B':
                banding = 1.4
                bandingString = '1B'
            elif manuallySelectedBinding == '1C':
                banding = 1.2
                bandingString = '1C'
            elif manuallySelectedBinding == 'Unbanded':
                banding = 1
                bandingString = 'Unbanded'
        totalPayRaw = basePay * banding
        totalPayRounded = round(totalPayRaw)
        resultsArray = [totalPayRounded, round(basePay) ,banding, bandingString]
    return resultsArray

def consultantContract(programmedActivities, year, grade, yearsAsCon): 
    results = []
    basePay = getPayData(year, grade, country)
    payPerPA = basePay / 10
    multiplier = 1
    nodalPoint = 'Base'
    if yearsAsCon > 0: 
         multiplier = 1.0313
         nodalPoint = 'One'
    if 1 <= yearsAsCon <= 2: 
        multiplier = 1.0626
        nodalPoint = 'Two'
    if 2 <= yearsAsCon <= 3: 
        multiplier = 1.0626
        nodalPoint = 'Three'
    if 3 <= yearsAsCon <= 4: 
        nodalPoint = 'Four'
        multiplier = 1.0939
    if 4 <= yearsAsCon <= 9: 
        nodalPoint = 'Five'
        multiplier = 1.1252
    if 9 <= yearsAsCon <= 13: 
        nodalPoint = 'Six'
        multiplier = 1.1995
    if 13 <= yearsAsCon <= 18: 
        nodalPoint = 'Seven'
        multiplier = 1.2739
    if yearsAsCon > 19: 
        nodalPoint = 'Eight'
        multiplier = 1.3482
    totalPay = payPerPA * programmedActivities
    adjustedTotalPay = round(totalPay * multiplier)
    results = [adjustedTotalPay, basePay, nodalPoint]
    return results

with st.container():
    st.title('Doctors Pay Cut Calculator')
    st.subheader('Calculate Your Pay Cut')

country = st.selectbox(
    'Select Country',
    ('England', 'Scotland' ,'Wales', 'Northern Ireland')
)

st.subheader('Your Grade')
grade = st.selectbox(
     'Select Your Grade',
     ('FY1', 'FY2', 'ST1', 'ST2', 'ST3', 'ST4', 'ST5', 'ST6', 'ST7', 'ST8', 'Consultant'))

# This prevents data being displayed for those Countries without Pay Data for 2022 Year.
if country == 'England' or country == 'Scotland' or country == 'Wales':
    maxYear = maxYear
if country == 'Northern Ireland' or grade == 'Consultant':
    maxYear = maxYear - relativedelta(years=yearsPost2022, months= currentDate.month) + relativedelta(months=4)
    
st.subheader('Inflation Metrics')
baselineInflationQuarter = st.slider(
     "Baseline Inflation Quarter.",
     min_value= date(2008, 1, 1),
     max_value= maxYear - relativedelta(day=1),
     value= date(2008, 1, 1),
     # Change to month = 1 on release
     format="Qo/YYYY",
     step= timedelta(days=365.5/4)
     )
comparisonInflationQuarter = st.slider(
     "Comparator Inflation Quarter.",
     min_value= baselineInflationQuarter,
     max_value= maxYear,
     value= maxYear,
     
     format="Qo/YYYY",
     step= timedelta(days=365.5/4)
     )

displayableComparatorDate = f'Q{((comparisonInflationQuarter.month-1)//3 + 1)} {comparisonInflationQuarter.year}'

inflationMeasure = st.selectbox(
    'Inflation Measure',
    ('RPI', 'CPIH')
)
displayableBaselineDate = f'Q{((baselineInflationQuarter.month-1)//3 + 1)} {baselineInflationQuarter.year}'
st.write(f'Comparing: {displayableBaselineDate} {inflationMeasure} to {displayableComparatorDate} {inflationMeasure}.')
     
# Determine Contracts to Display and Use
if country == 'England':
    if baselineInflationQuarter < date(2017, 1, 1) and comparisonInflationQuarter > date(2017, 1, 1): 
        contractSelected = [2002, 2016]
    elif baselineInflationQuarter < date(2017, 1, 1) and comparisonInflationQuarter < date(2017, 1, 1): 
        contractSelected = [2002, 2002]
    elif baselineInflationQuarter > date(2017, 1, 1): 
        contractSelected = [2016, 2016]
else:
    # All other Countries
    contractSelected = [2002, 2002]

# Check if Values Avaliable 
if payOldContract(comparisonInflationQuarter.year, grade, 40, 0, False, country, '<1:8', False, '1A')[0] > 0:   
    # Junior Doctor Pay 
    if grade != 'Consultant': 
        st.subheader('Average Hours Worked per Week')
        hoursWorked = st.slider('Total Hours Worked Per Week', 20, 48, 44)
        if hoursWorked < 40:
            ltft = True 

        st.subheader('Weekends Worked')
        if ltft == True: 
            st.write('Please Select the number of Weekends you would work if working Full-Time')
        weekendsWorked = st.select_slider(
            '<1:8 = Work One in Eight Weekends', 
            options=[ '<1:8', '<1:7 - 1:8', '<1:6 - 1:7', '<1:5 - 1:6', '<1:4 - 1:5', '<1:3 - 1:4', '<1:2 - 1:3', '1:2'], value= '<1:6 - 1:7')    

        # Only Display Parameters for Relevant Contract as Selected based on Country and Date (If comparing post 2016 contract introduction in
        # england)
        manuallySelectedBinding = 'Unbanded'
        antisocialHoursOld = 6
        if contractSelected[0] == 2002: 
            st.header('2002 Contract Details')
            manualBanding = st.checkbox('Manually Select Banding (Improves Accuracy)', False)
            if manualBanding == False:
                st.subheader(' Antisocial Hours')
                antisocialHoursOld = st.slider('Hours Worked Outside of Monday - Friday 07:00 - 19:00 (Allows Aproximate Banding Calculation).', 0, 20, 12)
            elif manualBanding == True:
                st.subheader('2002 Contract Banding')
                if ltft == True:
                    manuallySelectedBinding = st.selectbox('Select Your LTFT Banding', ['Unbanded', 'FC', 'FB', 'FA'])
                elif ltft == False:
                    manuallySelectedBinding = st.selectbox('Select Your Banding', ['Unbanded', '1C', '1B', '1A'])
                    st.write('[Summary of Banding](https://www.bma.org.uk/pay-and-contracts/pay/pay-banding/how-pay-banding-works)')
        elif contractSelected[0] == 2016:
            st.header('2016 Contract Details')
            st.subheader('Antisocial Hours')
            antisocialHours = st.slider('Hours Worked Outside of 07:00 - 21:00', 0, 20, 6)
            st.write('Do you recieve the Non-Resident On Call Supplement?')
            nroc = st.checkbox('Recieve Non-Resident On Call')
        if contractSelected[0] != contractSelected[1]:
            # Avoid Duplicating Display of Sliders
            if contractSelected[1] == 2002: 
                st.subheader('2002 Contract Antisocial Hours')
                antisocialHoursOld = st.slider('Hours Worked Outside of Monday - Friday 07:00 - 19:00', 0, 20, 12)
            elif contractSelected[1] == 2016: 
                st.header('2016 Contract Details')
                st.subheader('Antisocial Hours')
                antisocialHours = st.slider('Hours Worked Outside of 07:00 - 21:00', 0, 20, 6)
                st.write('Do you recieve the Non-Resident On Call Supplement?')
                nroc = st.checkbox('Recieve Non-Resident On Call')

        # Determine which contract to use to calculate Pay Data for Selected and Current Year
        if contractSelected[0] == 2002: 
            payArrayOld = payOldContract(baselineInflationQuarter.year, grade, hoursWorked, antisocialHoursOld, ltft, country, weekendsWorked, manualBanding, manuallySelectedBinding)
        elif contractSelected[0] == 2016: 
            payArrayOld = payNewContract(baselineInflationQuarter.year, grade, hoursWorked, nroc, ltft, country, antisocialHours, weekendsWorked)
        if contractSelected[1] == 2002: 
            payArray =  payOldContract(comparisonInflationQuarter.year, grade, hoursWorked, antisocialHoursOld, ltft, country, weekendsWorked, manualBanding, manuallySelectedBinding)
        elif contractSelected[1] == 2016: 
            payArray = payNewContract(comparisonInflationQuarter.year, grade, hoursWorked, nroc, ltft, country, antisocialHours, weekendsWorked)

        # Determine Inflation Change 
        currentInflation = getInflationIndex(comparisonInflationQuarter, inflationMeasure)
        inflationBaseline = getInflationIndex(baselineInflationQuarter, inflationMeasure)
        inflationChange = float(currentInflation) - float(inflationBaseline)
        inflationPercentage = float(currentInflation) / float(inflationBaseline)

        # Inflation for Display
        inflationPercentageChange = float(inflationChange) / float(inflationBaseline)
        inflationPercentageDisplay = round(inflationPercentageChange * 100)

        # Calculate Lossess Adjusting for Inflation
        oldPayWithInflation = payArrayOld[0] * inflationPercentage
        relativePayLoss = round(payArray[0] - oldPayWithInflation)
        percentageLoss = round(relativePayLoss / payArray[0] * 100)
        change = ""
        if oldPayWithInflation < payArray[0]: 
            change = "+Gain"
        elif oldPayWithInflation > payArray[0]:
            change = "-Loss"

        # Monthly Percent Loss
        monthlyPercentLoss = round((relativePayLoss / 12)/(payArray[0]/12)*100)

        # Show Pay + Inflation Details
        st.header(f'Summary')
        st.write(f'Pay changes from {baselineInflationQuarter.year} - {comparisonInflationQuarter.year} adjusted for inflation using {inflationMeasure} index ({displayableBaselineDate} - {displayableComparatorDate})')
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric('Yearly Change', f'£{relativePayLoss}', change)
            st.metric('Montly Change', f'£{round(relativePayLoss / 12)}', f'{monthlyPercentLoss}%')    
        with col2: 
            st.metric(f'{baselineInflationQuarter.year} Pay Adjusted For Inflation', f'£{round(oldPayWithInflation)}',) 
         
        with col3:
            st.metric(f'{comparisonInflationQuarter.year} Pay', f'£{payArray[0]}', f'{percentageLoss}%')
            st.metric(f'{inflationMeasure} {displayableBaselineDate} Inflation Index:', inflationBaseline)
            st.metric(f'{inflationMeasure} {displayableComparatorDate} Inflation Index:', currentInflation, f'{inflationPercentageDisplay}%')
            st.caption(f'Since {baselineInflationQuarter.year}')

        st.subheader('Calculation Breakdown')
        st.caption(f'Disclaimer: Figures given are approximate. To improve accuracy please manually select the banding for the 2002 contract.')
        # Show Calculation Details
        col1, col2,= st.columns(2)
        with col1:
            if contractSelected[0] == 2002: 
                st.write(f'{baselineInflationQuarter.year}')
                st.caption(f'Your Pay: £{payArrayOld[0]}')
                st.caption(f'Base Pay: £{payArrayOld[1]}')
                st.caption(f'Your Banding: {payArrayOld[3]} = {payArrayOld[2]} Multiplier to Base')
                st.caption('Based of the 2002 Contract')
            if contractSelected[0] == 2016:
                st.write(f'{baselineInflationQuarter.year}')
                st.caption(f'Your Pay: £{round(payArrayOld[0])}')
                st.caption(f'Base Pay: £{round(payArrayOld[1])}')
                st.caption(f'Antisocial Hours Supplement: £{round(payArrayOld[2])}')
                if ltft == False: 
                    st.caption(f'Weekend Supplement: £{round(payArrayOld[4])}')
                    st.caption(f'Non Resident On Call Supplement: £{round(payArrayOld[5])}')
                    if ltft == True: 
                        st.caption(f'Less Than Full Time Allowance: £{round(payArrayOld[6])}')
                    st.caption('Based of the 2016 Contract')
            
        with col2: 
            if contractSelected[1] == 2002: 
                st.write(f'{comparisonInflationQuarter.year}')
                st.caption(f'Your Pay: £{payArray[0]}')
                st.caption(f'Base Pay: £{payArray[1]}')
                st.caption(f'Your Banding: {payArray[3]} = {payArrayOld[2]} Multiplier to Base')
                st.caption('Based of the 2002 Contract')
            
            if contractSelected[1] == 2016:
                st.write(f'{comparisonInflationQuarter.year}')
                st.caption(f'Your Pay: £{round(payArray[0])}')
                st.caption(f'Base Pay: £{round(payArray[1])}')
                st.caption(f'Antisocial Hours Supplement: £{round(payArray[2])}')
                if ltft == False: 
                    st.caption(f'Supplement for > 40 Hours Per Week £{round(payArray[3])}')
                st.caption(f'Weekend Supplement: £{round(payArray[4])}')
                st.caption(f'Non Resident On Call Supplement: £{round(payArray[5])}')
                if ltft == True: 
                    st.caption(f'Less Than Full Time Allowance: £{round(payArray[6])}')
                st.caption('Based of the 2016 Contract')
    elif grade == 'Consultant':
        if country != 'Northern Ireland':    
            # Consultant Pay Section
            st.subheader('Programmed Activities')
            programmedActivities = st.slider('Average Number of Programmed Activities per Week', 1, 16, 10)
            st.subheader('Number of Years as a Consultant')
            yearsCompleted = st.slider('Years as a Consultant', 0, 30, 4)

            #Pull Data 
            payArrayOld = consultantContract(programmedActivities, baselineInflationQuarter.year, grade ,yearsCompleted)
            payArray = consultantContract(programmedActivities, comparisonInflationQuarter.year, grade ,yearsCompleted)

            # Determine Inflation Change 
            currentInflation = getInflationIndex(comparisonInflationQuarter, inflationMeasure)
            inflationBaseline = getInflationIndex(baselineInflationQuarter, inflationMeasure)
            inflationChange = float(currentInflation) - float(inflationBaseline)
            inflationPercentage = float(currentInflation) / float(inflationBaseline)

            # Inflation for Display
            inflationPercentageChange = float(inflationChange) / float(inflationBaseline)
            inflationPercentageDisplay = round(inflationPercentageChange * 100)

            # Calculate Lossess Adjusting for Inflation
            oldPayWithInflation = payArrayOld[0] * inflationPercentage
            relativePayLoss = round(payArray[0] - oldPayWithInflation)
            percentageLoss = round(relativePayLoss / payArray[0] * 100)
            change = ""
            if oldPayWithInflation < payArray[0]: 
                change = "+Gain"
            elif oldPayWithInflation > payArray[0]:
                change = "-Loss"
            
            # Monthly Percentage Loss
            monthlyPercentLoss = round((relativePayLoss / 12)/(payArray[0]/12)*100)

            # Show Pay + Inflation Details
            st.header('Summary')
            st.write(f'Pay changes from {baselineInflationQuarter.year} - {comparisonInflationQuarter.year} adjusted for inflation using {inflationMeasure} index ({displayableBaselineDate} - {displayableComparatorDate}')
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric('Yearly Change', f'£{relativePayLoss}', change)    
                st.metric('Montly Change', f'£{round(relativePayLoss / 12)}', f'{monthlyPercentLoss}%')
            with col2: 
                st.metric(f'{baselineInflationQuarter.year} Pay Adjusted For Inflation', f'£{round(oldPayWithInflation)}') 
                
            with col3:
                st.metric(f'{comparisonInflationQuarter.year} Pay', f'£{payArray[0]}', f'{percentageLoss}%')
                st.metric(f'{inflationMeasure} {displayableBaselineDate} Inflation Index:', inflationBaseline)
                st.metric(f'{inflationMeasure} {displayableComparatorDate} Inflation Index:', currentInflation, f'{inflationPercentageDisplay}%')
                st.caption(f'Since {baselineInflationQuarter.year}')

            st.subheader('Calculation Breakdown')
            st.caption(f'Disclaimer: Figures given are approximate only and purely based of your base salary. Based of 2003 Contract.')
            # Show Calculation Details
            col1, col2,= st.columns(2)
            with col1:
                st.write(f'{baselineInflationQuarter.year}')
                st.caption(f'Your Pay: £{payArrayOld[0]}')
                st.caption(f'Base Pay: £{payArrayOld[1]}')
                st.caption(f'Based On {programmedActivities} Programmed Activities per Week')
                st.caption(f'Nodal Point: {payArrayOld[2]}') 
                
            with col2: 
                st.write(f'{comparisonInflationQuarter.year}')
                st.caption(f'Your Pay: £{payArray[0]}')
                st.caption(f'Base Pay: £{payArray[1]}')
                st.caption(f'Based On {programmedActivities} Programmed Activities per Week')
                st.caption(f'Nodal Pay Point: {payArray[2]}')
        else: 
            st.subheader('Data Unavailable')
else: 
    st.write(f'Basic Salaray is not yet avaliable for {comparisonInflationQuarter.year}. Please select an early Quarter for comparison.')