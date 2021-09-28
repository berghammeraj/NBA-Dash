import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# see https://community.plot.ly/t/nolayoutexception-on-deployment-of-multi-page-dash-app-example-code/12463/2?u=dcomfort
from app import server
from app import app
from layouts import player_layout
import callbacks

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# This callback changes the layout of the page based on the URL
# For each layout read the current URL page "http://127.0.0.1:5000/pagename" and return the layout
@app.callback(Output('page-content', 'children'), #this changes the content
              [Input('url', 'pathname')]) #this listens for the url in use
def display_page(pathname):
    if pathname == '/':
        return player_layout

    else:
        return '404' #If page not found return 404

#Runs the server at http://127.0.0.1:5000/      
if __name__ == '__main__':
    app.run_server(port=5000, host= '127.0.01',debug=True)