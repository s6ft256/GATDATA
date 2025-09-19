import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import base64
from io import BytesIO
import pandas as pd

def create_bar_chart(df, x_column, y_column, title="Bar Chart"):
    """
    Create a bar chart using Plotly
    """
    fig = px.bar(df, x=x_column, y=y_column, title=title)
    return fig.to_json()

def create_scatter_plot(df, x_column, y_column, color_column=None, title="Scatter Plot"):
    """
    Create a scatter plot using Plotly
    """
    fig = px.scatter(df, x=x_column, y=y_column, color=color_column, title=title)
    return fig.to_json()

def create_line_chart(df, x_column, y_column, title="Line Chart"):
    """
    Create a line chart using Plotly
    """
    fig = px.line(df, x=x_column, y=y_column, title=title)
    return fig.to_json()

def create_histogram(df, column, title="Histogram"):
    """
    Create a histogram using Plotly
    """
    fig = px.histogram(df, x=column, title=title)
    return fig.to_json()

def create_heatmap(df, title="Correlation Heatmap"):
    """
    Create a correlation heatmap using Plotly
    """
    # Select only numerical columns
    numerical_df = df.select_dtypes(include=['number'])
    correlation_matrix = numerical_df.corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=correlation_matrix.values,
        x=correlation_matrix.columns,
        y=correlation_matrix.columns,
        colorscale='Viridis'
    ))
    fig.update_layout(title=title)
    return fig.to_json()

def create_box_plot(df, column, title="Box Plot"):
    """
    Create a box plot using Plotly
    """
    fig = px.box(df, y=column, title=title)
    return fig.to_json()