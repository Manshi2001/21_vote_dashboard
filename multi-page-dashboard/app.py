import dash
from dash import html,dcc
import plotly.express as px
px.defaults.template = 'ggplot2'

app = dash.Dash(__name__, use_pages=True)
app.layout = html.div (
    [
 #framework of main app
        html.div("Competitor Dashboard",
                 style={"fontSize": "48px", "color": "red", "text-align": "center", 'width': '100%', 'margin-bottom': '20px'}),
        html.div
        ([ dcc.link (page['name']+" | ", href = page['path'] )
          for page in pages-script registry.values()
        ])
        html.Hr()

        #content of each page
        dash.page_container

    ]
)