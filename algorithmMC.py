import http.client
import json
import pandas as pd
import numpy as np
from numpy import random
import plotly as plt
import plotly.express as px

import TreatAlgorithm as TA


pdf_price = np.random.lognormal(12.5,0.5,size=1000000)
pdf_acre = np.random.lognormal(-0.5,0.75,size=1000000)
pdf_murd = np.random.normal(100,15,size=1000000)
pdf_rape = np.random.normal(100,15,size=1000000)
pdf_other = np.random.normal(100,15,size=1000000)
pdf_bed = np.random.randint(1,6,size=1000000)
mc_df = pd.DataFrame({"Price":pdf_price,"Acre":pdf_acre,"crmcymurd":pdf_murd,"crmcyrape":pdf_rape,"crmcyproc":pdf_other,"Bedrooms":pdf_bed})

vf = TA.pHouse(10,2,7,1,mc_df["Price"],mc_df["Acre"],mc_df[["crmcymurd","crmcyrape","crmcyproc"]],mc_df["Bedrooms"])

df = pd.DataFrame({"Value Factor":vf})
fig = px.histogram(df, x="Value Factor", nbins=100, title="Value Factor Monte Carlo")
fig.show()
