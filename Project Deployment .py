import pickle as pkl
import streamlit as st
import pandas as pd

# we will upload the data 
data=pkl.load(open(r"C:\Users\mohamed salman\Desktop\Depi final project\Used Cars Price.sav",'rb'))

st.title('Used Car Prices Web App')
st.info('Easy Application for used car prices')

st.slidebar.header('Feature Selection')

brand=st.text_input("brand")
model= st.text_input("model")
year=st.text_input("year")
mileage= st.text_input("mileage")
fuel_type=st.text_input("fuel_type")
engine=st.text_input("engine")
transmission=st.text_input("transmission")
ext_col=st.text_input("ext_col")
int_col=st.text_input("int_col")
accident=st.text_input("accident")
clean_title=st.text_input("clean_title")
df=pd.Dataframe({"brand":[brand],"model":[model],"year":[year],"mileage":[mileage],"fuel_type":[fuel_type],
              "engine":[engine],"transmission":[transmission],
             "ext_col":[ext_col],"int_col":[int_col],"accident":[accident]
              ,"clean_title":[clean_title] },index=[0])
con=st.sidebar.button("Confirm")
if con :
    result=data.predect(df)
    st.sidebat.write(result)








