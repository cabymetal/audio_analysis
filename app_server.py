from dash import Dash, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import layout
import urllib.parse
import pdb

############################# create app ########################################################

external_scripts = [{
  'defer': 'defer',
  'src': 'https://use.fontawesome.com/releases/v5.0.13/js/solid.js',
  'integrity': 'sha384-tzzSw1/Vo+0N5UhStP3bvwWPq+uvzCMfrN1fEFe+xBmv1C/AtVX5K0uZtmcHitFZ',
  'crossorigin': 'anonymous'
 },
 {
  'defer': 'defer',
  'src': 'https://use.fontawesome.com/releases/v5.0.13/js/fontawesome.js',
  'integrity': 'sha384-6OIrr52G08NpOFSZdxxz1xdNSndlD4vdcf/q2myIUVO0VsqaGHJsB0RaBE01VTOY',
  'crossorigin': 'anonymous'
 },
 {
  'src': 'https://code.jquery.com/jquery-3.3.1.slim.min.js',
  'integrity': 'sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo',
  'crossorigin': 'anonymous'
 },
 {
  'src': 'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.0/umd/popper.min.js',
  'integrity': 'sha384-cs/chFZiN24E4KMATLdqdvsezGxaGsi4hLGOzlXwp5UZB1LY//20VyM2taTB4QvJ',
  'crossorigin': 'anonymous'
 },
 {
  'src': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/js/bootstrap.min.js',
  'integrity': 'sha384-uefMccjFJAIv6A+rW+L4AHf99KvxDjWSu1z9VI8SKNVmz4sk7buKt/6v9KI65qnm',
  'crossorigin': 'anonymous'
 }

]

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.themes.LUX], external_scripts=external_scripts,
  suppress_callback_exceptions=True, title = 'app music', update_title='Cargando...')

app.layout = layout.get_layout()


##### CALLBACKS #####

@app.callback(
	[Output('audio_player', 'src'),  Output('title-song', 'children'), Output('image-song', 'src')],
	Input('scatter_graph', 'clickData')
)
def refresh_audio_player(clickData):
	path = '/assets/Audio/'
	path_image='/assets/spectograms/'
	if not clickData:
		return [path + 'Death on the Balcony - Tempt Of Fate.wav', 'Death on the Balcony - Tempt Of Fate.wav', 
			path_image + 'Death on the Balcony - Tempt Of Fate.png']



	return [path + clickData['points'][0]['customdata'][0], clickData['points'][0]['customdata'][0],
		path_image + clickData['points'][0]['customdata'][0][:-3] + 'PNG' ]

if __name__ == '__main__':
	app.run_server(host='localhost', debug=True)