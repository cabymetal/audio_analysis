from dash import Dash, dcc
import dash_auth
from dash.dependencies import Input, Output, State
from clasificacion import Song
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

VALID_USERNAME_PASSWORD_PAIRS = {
    'proyecto_clasificacion' : 'eafit2022'
}

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.themes.LUX], external_scripts=external_scripts,
  suppress_callback_exceptions=True, title = 'app music', update_title='Cargando...')

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

server = app.server
app.layout = layout.get_layout()


##### CALLBACKS #####

@app.callback(
	[Output('audio_player', 'src'), Output('title-song', 'children'), Output('image-song', 'src'),
	Output('audio_player_1', 'src'), Output('audio_player_2', 'src'), Output('scatter_nclicks', 'children'),
	Output('title-song-1', 'children'), Output('title-song-2', 'children'),
	Output('image-song-1', 'src'), Output('image-song-2', 'src')],
	Input('scatter_graph', 'clickData'), State('scatter_nclicks', 'children'), State('audio_player_1', 'src'), State('audio_player_2', 'src'),
	State('title-song-1', 'children'), State('title-song-2', 'children'), State('image-song-1', 'src'), State('image-song-2', 'src')
)
def refresh_audio_player(clickData, n_clicks, src1, src2, tit1, tit2, isrc1, isrc2):
	path = 'assets/Audio/'
	path_image='assets/spectograms/'

	if not clickData:
		return [path + 'Death on the Balcony - Tempt Of Fate.wav', 'Death on the Balcony - Tempt Of Fate.wav',
			path_image + 'Death on the Balcony - Tempt Of Fate.png','','', 0, tit1, tit2, isrc1, isrc2]

	song = Song(path)
	song_name, part = clickData['points'][0]['customdata'][3], clickData['points'][0]['customdata'][4]
	song_section_name, spectogram_section = song.get_path_to_section(song_name, part)
	# machete para nombres raros de canciones
	tmp_song_name = clickData['points'][0]['customdata'][3][:-4].replace('.', '')+'.png'
	n_clicks = int(n_clicks)
	n_clicks = n_clicks + 1
	ret_value = []
	if (n_clicks % 2) != 0:
		# para el input 1
		ret_value = [path + clickData['points'][0]['customdata'][3], clickData['points'][0]['customdata'][3],
		path_image + tmp_song_name , song_section_name, src2, n_clicks,
		f"{song_name} {part}", tit2 , spectogram_section, isrc2]
	else:
		# para el input 2
		ret_value = [path + clickData['points'][0]['customdata'][3], clickData['points'][0]['customdata'][3],
		path_image + tmp_song_name, src1, song_section_name, n_clicks,
		tit1, f"{song_name} {part}", isrc1, spectogram_section]

	return ret_value

if __name__ == '__main__':
	app.run_server(host='localhost', debug=True)