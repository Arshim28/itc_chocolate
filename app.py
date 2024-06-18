import streamlit as st
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from plotly.offline import plot


# Load JSON data
df = pd.read_json('results.json')

# Adjust the DataFrame columns
df.columns = ['Composition', 'SFC & Temperature']

st.title("SFC Profile Analysis")

st.sidebar.header("Filter Compositions")
pop_min = st.sidebar.slider("POP min", 0.0, 1.0, 0.0, 0.01)
pop_max = st.sidebar.slider("POP max", 0.0, 1.0, 1.0, 0.01)
sos_min = st.sidebar.slider("SOS min", 0.0, 1.0, 0.0, 0.01)
sos_max = st.sidebar.slider("SOS max", 0.0, 1.0, 1.0, 0.01)

temp = 35
closest_temp = 0
min_diff = 1000

for i in range(len(df['SFC & Temperature'])):
    for j in range(len(df['SFC & Temperature'][i])):
        diff = abs(df['SFC & Temperature'][i][j][1] - temp)
        if diff < min_diff:
            min_diff = diff
            closest_temp = df['SFC & Temperature'][i][j][1] 

# Find the frequency of the closest temperature to 35C
idx = 0
for i in range(len(df['SFC & Temperature'])):
    for j in range(len(df['SFC & Temperature'][i])):
        if df['SFC & Temperature'][i][j][1] == closest_temp:
            idx = j

# Filter DataFrame based on POP and SOS mole fractions
filtered_df = df[
    (df['Composition'].apply(lambda x: pop_min <= x[0] <= pop_max)) &
    (df['Composition'].apply(lambda x: sos_min <= x[2] <= sos_max))
]

filtered_df = filtered_df.reset_index(drop=True)

top_10_compositions = []
for i in range(len(filtered_df)):
    if filtered_df['SFC & Temperature'][i][idx][1] == temp:
        #Round the composition, sfc and temperature values to 2 decimal places
        filtered_df['Composition'][i] = tuple([round(x, 2) for x in filtered_df['Composition'][i]])
        filtered_df['SFC & Temperature'][i][idx] = tuple([round(x, 2) for x in filtered_df['SFC & Temperature'][i][idx]])

        top_10_compositions.append((filtered_df['Composition'][i], filtered_df['SFC & Temperature'][i][idx][0]))

top_10_compositions = sorted(top_10_compositions, key=lambda x: x[1], reverse=True)
top_10_compositions = top_10_compositions[:10]



sfc, tmp = [[] for _ in range(10)], [[] for _ in range(10)]

for i in range(10):
    composition = top_10_compositions[i][0]
    idx = 0
    for j in range(len(filtered_df)):
        if filtered_df['Composition'][j] == composition:
            idx = j
            sfc_Temp = filtered_df['SFC & Temperature'][idx] 
            for k in range(len(sfc_Temp)):
                sfc[i].append(sfc_Temp[k][0])
                tmp[i].append(sfc_Temp[k][1])

fig = go.Figure()

for i in range(10):
    fig.add_trace(go.Scatter(x=tmp[i], y=sfc[i], mode='lines', name=f"Comp {i+1}: POP={top_10_compositions[i][0][0]}, SOS={top_10_compositions[i][0][2]}"))

fig.update_layout(title='Top 10 compositions with closest temperature to 35C', xaxis_title='Temperature', yaxis_title='SFC')
#Make the plot size bigger
fig.update_layout(
    autosize=False,
    width=1200,
    height=600,
    margin=dict(
        l=20,
        r=50,
        b=100,
        t=100,
        pad=4
    )
)
st.plotly_chart(fig)

                  
