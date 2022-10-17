from dash import Dash, dcc, html
import dash
import dash_auth
from dash.dependencies import Input, Output, State
from clasificacion import Song
import dash_bootstrap_components as dbc
import layout
import urllib.parse
import shap
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
	Output('image-song-1', 'src'), Output('image-song-2', 'src'), Output('inicators-graph', 'figure'),  Output('force-graph', 'figure')],
	Input('scatter_graph', 'clickData'), State('scatter_nclicks', 'children'), State('audio_player_1', 'src'), State('audio_player_2', 'src'),
	State('title-song-1', 'children'), State('title-song-2', 'children'), State('image-song-1', 'src'), State('image-song-2', 'src')
)
def refresh_audio_player(clickData, n_clicks, src1, src2, tit1, tit2, isrc1, isrc2):
	path = 'assets/Audio/'
	path_image='assets/spectograms/'

	if not clickData:
		raise dash.exceptions.PreventUpdate("cancel the callback")

	song = Song(path)
	song_name, part = clickData['points'][0]['customdata'][3], clickData['points'][0]['customdata'][4]
	song_section_name, spectogram_section = song.get_path_to_section(song_name, part)
	# rehacer graficas de indicadores 
	mindur, maxdur, songdur, cluster, df_data = layout.model_obj.read_all_data(song_name)
	graph = layout.graph_obj.draw_indicator_info(mindur, maxdur, songdur, cluster, song_name)
	# rehacer graficas de fuerza
	k, df_original, labels = clickData['points'][0]['customdata'][2], layout.df_original, layout.labels
	force_graph = layout.graph_obj.draw_shap_cluster_beeswarm(k, df_original, labels)

	# machete para nombres raros de canciones
	tmp_song_name = clickData['points'][0]['customdata'][3][:-4].replace('.', '')+'.png'
	n_clicks = int(n_clicks)
	n_clicks = n_clicks + 1
	ret_value = []
	if (n_clicks % 2) != 0:
		# para el input 1
		ret_value = [path + clickData['points'][0]['customdata'][3], clickData['points'][0]['customdata'][3],
		path_image + tmp_song_name , song_section_name, src2, n_clicks,
		f"{song_name} {part}", tit2 , spectogram_section, isrc2, graph, force_graph]
	else:
		# para el input 2
		ret_value = [path + clickData['points'][0]['customdata'][3], clickData['points'][0]['customdata'][3],
		path_image + tmp_song_name, src1, song_section_name, n_clicks,
		tit1, f"{song_name} {part}", isrc1, spectogram_section, graph, force_graph]

	return ret_value

@app.callback(
	Output('shap_force_graph', 'children'),
	Input('scatter_graph', 'hoverData')
)
def draw_shap_force_frame(hover):
	if not hover:
		raise dash.exceptions.PreventUpdate("cancel the callback")
	ind = hover['points'][0]['pointIndex']
	explainer, shap_values= layout.explainer, layout.shap_values
	choosen_instance = layout.df_original.loc[[ind]]
	shap_values = explainer.shap_values(choosen_instance)
	return _force_plot_html(explainer.expected_value[0], shap_values[1], choosen_instance)

def _force_plot_html(*args):
    force_plot = shap.force_plot(*args, matplotlib=False)
    shap_html = f"<head>{shap.getjs()}</head><body>{force_plot.html()}</body>"
    return html.Iframe(srcDoc=shap_html,
                       style={"width": "100%", "height": "200px", "border": 0})

if __name__ == '__main__':
	#app.run_server(host='localhost', debug=True) #local
	server.run() #aws