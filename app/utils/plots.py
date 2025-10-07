import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot(query, ref, query_term, ref_term, agg_years=1):
    merged = {'Year': [], 'Query': [], 'Reference': [], 'Normalized': []} # add header row
    for key in sorted(query.keys() & ref.keys()):
        merged['Year'].append(f'{key}' if agg_years==1 else f'{int(key)-agg_years+1}-{key}')
        merged['Query'].append(query[key])
        merged['Reference'].append(ref[key])
        if ref[key] != 0:
            merged['Normalized'].append(query[key] / ref[key])
        else:
            merged['Normalized'].append(pd.NA)

    df = pd.DataFrame.from_records(merged)
    fig = make_subplots()
    fig.add_trace(
        go.Scatter(
            x=df['Year'],
            y=df['Query'],
            name=f"# {query_term}",
            line=dict(color='green'),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df['Year'],
            y=df['Reference'],
            name=f"# {ref_term}",
            line=dict(color='blue'),
            yaxis="y2",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df['Year'],
            y=df['Normalized'],
            name=f"# {query_term}/{ref_term}",
            line=dict(color='red'),
            yaxis="y3",
        )
    )
    fig.update_layout(
        title=f"PubMed Statistics for {query_term}; reference {ref_term}",
        yaxis=dict(
            title=f"# {query_term}",
            linewidth=1.5,
            linecolor="black",
        ),
        yaxis2=dict(
            title=f"# {ref_term}",
            overlaying="y",
            side='right',
            position=0.9,
            linewidth=1.5,
            linecolor="black",
        ),
        yaxis3=dict(
            title=f"# {query_term}/{ref_term}",
            overlaying="y",
            side="right",
            position=1,
            linewidth=1.5,
            linecolor="black",
        ),
        showlegend=True,
        plot_bgcolor='white',  # White background for the plotting area
        paper_bgcolor='white',  # White background for the whole figure
        xaxis=dict(
            tickangle=45,
            linecolor='black',
            linewidth=1.5,
            domain=[0.0, 0.90]
        ),
        margin=dict(l=50, r=80, b=50, t=50),  # Reduced margins
        legend=dict(
            x=0.5,
            y=1.05,
            xanchor='center',
            yanchor='top',
            orientation='h'
        ),
    )
    #fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    
    return fig.to_json()
        