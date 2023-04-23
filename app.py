import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly
import plotly.graph_objects as go
import plotly.offline as pyo

st.set_page_config(page_title="Covid 19 current")

st.title("World in Covid 19")


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

data=pd.DataFrame({"continent":continent,"country":country,"population":pops,"day":day,"active":active_case,"critical":critical_case,
           "recovered":recovered_case,"total_case":total_case,"total_death":total_death,"total_test":total_test})

data=treat_missing(data)



continent = st.sidebar.selectbox(

    "Choose desired continent",
    ["World"]+data["continent"].unique().tolist()
)


if(continent=="World"):

    df=pd.DataFrame([{"day":all[0]["day"],"active":all[0]["cases"]["active"],"critical":all[0]["cases"]["critical"],
                    "recovered":all[0]["cases"]["recovered"],"total":all[0]["cases"]["total"],"deaths":all[0]["deaths"]["total"],"total_test":data["total_test"].sum()}])
    
    pop=round(data["population"].sum(),2)
    day=df["day"].values[0]
    scontinent="World"
    scountry="All"
    active=round(df["active"].values[0],2)
    critical=round(df["critical"].values[0],2)
    death=round(df["deaths"].values[0],2)
    case=round(df["total"].values[0],2)
    recovered=round(df["recovered"].values[0],2)
    test=round(df["total_test"].values[0],2)
    


else:

    con=data["country"][(data["continent"]==continent)].values.tolist()    
    con_list=["All"]+con    
    country = st.sidebar.selectbox("Choose desired country ",con_list)   

    if(country!="All"):

        df=data[(data["country"]==country)]
        pop=round(df["population"],2)
        active=round(df["active"].values[0],2)
        critical=round(df["critical"].values[0],2)
        death=round(df["total_death"].values[0],2)
        case=round(df["total_case"].values[0],2)
        recovered=round(df["recovered"].values[0],2)
        test=round(df["total_test"].values[0],2)

    else:

        df=data[(data["continent"]==continent)]
        pop=round(df["population"].sum(),2)
        active=round(df["active"].mean(),2)
        critical=round(df["critical"].mean(),2)
        death=round(df["total_death"].mean(),2)
        case=round(df["total_case"].mean(),2)
        recovered=round(df["recovered"].mean(),2)
        test=round(df["total_test"].mean(),2)
    
    day=df["day"].values[0]
    scontinent=continent
    scountry=country

placeholder=st.empty()

with placeholder.container():

    cdate,fcountry,fcontinent,population=st.columns([20,10,10,20])

    cdate.metric(label="Date",value=day)    
    fcontinent.metric(label="Continent",value=scontinent)
    fcountry.metric(label="Country",value=scountry)
    population.metric(label="Population",value=pop)

    fig1,fig2,fcase=st.columns(3,gap="large")
    

    with fig1:

        x=["Active","Critical","Deaths"]
        y=[active,critical,death]
        fig1 = go.Figure([go.Bar(x=x,y=y)])
        fig1.update_layout(title="Active,Critical,Deaths",autosize=False, width=250, height=400)
        st.write(fig1)
    
    with fig2:

        x1=["Cases","Recovered","Tests"]
        y1=[case,recovered,test]
        fig2 = go.Figure([go.Bar(x=x1,y=y1)])
        fig2.update_layout(title="Cases,Recovered,Tests",autosize=False, width=250, height=400)
        st.write(fig2)


    fcase.metric(label="Total Cases",value=case)



st.info("This dashboard represents the current information of the Covid 19 suituation worldwide which is updated every 15 minutes, extracted from the Covid 19 api available on www.rapidapi.com. You can either have a overall overview of current Covid 19 suituation in the world as a whole or the continents as a whole or specifically in a country. You can observe the current population and the total no of covid cases till date , number of  active,critical,recovered cases and deaths reported.")
