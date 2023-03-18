import streamlit as st
import pandas as pd
import numpy as np
import requests

st.set_page_config(page_title="Covid 19 current")
#st.title("Covid 19 Current")

def treat_missing(df):
    
    df.dropna(subset=["continent"],inplace=True)
    df.dropna(subset=["population"],inplace=True)
    df["active"].fillna(0.0,inplace=True)
    df["total_death"].fillna(0.0,inplace=True)
    df["critical"].fillna(0.0,inplace=True)
    for i in df[df.recovered.isnull()].index:
        
        df.loc[i, 'recovered'] = df.loc[i, 'total_case']-(df.loc[i, 'active']+df.loc[i, 'critical']+df.loc[i, 'total_death']) 
    
    mean_tt=round((((df["total_test"][(df["continent"]=="Oceania")].mean()+df["total_test"][(df["continent"]=="Africa")].mean())/2)/16),1)
    df["total_test"].fillna(mean_tt,inplace=True)
    
    return df


def treat_outlier(df):

    for col in df.select_dtypes(include=np.number).columns.to_list():# Taking all numeric columns

        # Calculating interquartile range for each numeric column
        q1=df[col].quantile(.25)
        q3=df[col].quantile(.75)
        iqr=q3-q1
    
        lower=q1-1.5*iqr
        upper=q3+1.5*iqr
    
        # Capping all colums between upper and lower limit
        df[col]=np.where(df[col]>upper,upper,np.where(df[col]<lower,lower,df[col]))
    
    return df


url_all = "https://covid-193.p.rapidapi.com/statistics?country=all"

url_specs = "https://covid-193.p.rapidapi.com/statistics"

headers = {
	"X-RapidAPI-Key": "ba5d9bc283mshe6584b01fb2b71fp145ee1jsn5c75f2c30dda",
	"X-RapidAPI-Host": "covid-193.p.rapidapi.com"
}

response_all = requests.request("GET", url_all, headers=headers)
response_specs = requests.request("GET", url_specs, headers=headers)

data_all=response_all.json()
raw_data=response_specs.json()

all=data_all["response"]
result=raw_data["response"]

continent=[]
country=[]
pops=[]
day=[]
active_case=[]
critical_case=[]
recovered_case=[]
total_case=[]
total_death=[]
total_test=[]


for i  in result:
    
    continent.append(i["continent"])
    country.append(i["country"])
    pops.append(i["population"])
    day.append(i["day"])
    active_case.append(i["cases"]["active"])
    critical_case.append(i["cases"]["critical"])
    recovered_case.append(i["cases"]["recovered"])
    total_case.append(i["cases"]["total"])
    total_death.append(i["deaths"]["total"])
    total_test.append(i["tests"]["total"])

data_dict={"continent":continent,"country":country,"population":pops,"day":day,"active":active_case,"critical":critical_case,
           "recovered":recovered_case,"total_case":total_case,"total_death":total_death,"total_test":total_test}
          
data=pd.DataFrame(data_dict)

data=treat_missing(data)
data=treat_outlier(data)


continent = st.sidebar.selectbox(

    "Choose desired continent",
    ["World"]+data["continent"].unique().tolist()
)

if(continent=="World"):

    con=data["country"].tolist()
    con_list=["All"]+con
    country = st.sidebar.selectbox("Choose desired country ",con_list)
    df=data.copy()
    st.write("Country Selected is: ",country)

else:

    con=data["country"][(data["continent"]==continent)].values.tolist()
    df=data[(data["continent"]==continent)]
    con_list=["All"]+con    
    country = st.sidebar.selectbox("Choose desired country ",con_list)
    st.write("Continent Selected is: ",continent)
    st.write("Country Selected is: ",country)

if(country!="All"):

    df=df[(df["country"]==country)]