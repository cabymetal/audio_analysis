from dash import Dash, dcc, html, dash_table
import dash
import dash_auth
from dash.dependencies import Input, Output, State, ClientsideFunction, ALL, MATCH
from dash.exceptions import PreventUpdate
from clasificacion import Song
import dash_bootstrap_components as dbc
import layout as lout
import shap
import pandas as pd

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
app.layout =  lout.main_layout # layout.get_layout()


####################################### CALLBACKS ##############################################
@app.callback([Output('sidebarCollapse', 'className'), Output('sidebar', 'className')], 
[Input('sidebarCollapse', 'n_clicks')])
def update_classname(n_clicks):
    if n_clicks==None:
      n_clicks = 0
    if (n_clicks%2)==0:
      return ['navbar-btn active', 'active']
    else:
      return ['', '']

# Update the index
@app.callback(Output('content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
	if pathname=='/':
		return lout.get_readme_markdown()
	elif pathname=='/variables_clasicas':
		return lout.get_home_layout()
	elif pathname=='/redes_neuronales':
		return lout.get_neural_network_page()
	elif pathname=='/resumen':
		return lout.summary_methods_kmeans()
	pass


##### CALLBACKS #####

@app.callback(
	Output('graph-bar-cluster-1', 'figure'), Output('tabs-content-audio-1', 'children'), Output('tabs-table-audio-1', 'children'),
	Input('button-refresh-song1', 'n_clicks'),
	State('dropdown-songs-original', 'value'), State('dropdown-part-original', 'value'), State('checklist-cluster-original', 'value')
)
def refresh_block_1(clickData, songs, parts, clusters):
	if not clickData:
		raise dash.exceptions.PreventUpdate("cancel callback")
	aux_df = lout.model_obj.df_clas_helper.reset_index().copy()
	if isinstance(songs, str):
		songs = [songs]
	if isinstance(parts, str):
		parts = [parts]
	figure = lout.graph_obj.create_bar_chart(aux_df, songs)
	audio_html = lout.get_audio_controls(songs, parts)
	table_html = lout.get_table_detailed(songs, parts, '2')
	return figure, audio_html, table_html

@app.callback(
	Output('graph-bar-cluster-2', 'figure'), Output('tabs-content-audio-2', 'children'), Output('tabs-table-audio-2', 'children'),
	Input('button-refresh-song2', 'n_clicks'),
	State('dropdown-songs-compare', 'value'), State('dropdown-part-compare', 'value'), State('checklist-cluster-compare', 'value')
)
def refresh_block_2(clickData, songs, parts, clusters):
	if not clickData:
		raise dash.exceptions.PreventUpdate("cancel callback")
	aux_df = lout.model_obj.df_clas_helper.reset_index().copy()
	if isinstance(songs, str):
		songs = [songs]
	if isinstance(parts, str):
		parts = [parts]
	figure = lout.graph_obj.create_bar_chart(aux_df, songs)
	audio_html = lout.get_audio_controls(songs, parts)
	table_html = lout.get_table_detailed(songs, parts, '2')
	return figure, audio_html, table_html

@app.callback(
	Output('tbl-out-1', 'children'),
	Input('table-1', 'active_cell'),
	State('dropdown-songs-original', 'value'), State('dropdown-part-original', 'value'), State('checklist-cluster-original', 'value')
)
def update_graphs_1(active_cell, songs, parts, clusters):
	if isinstance(songs, str):
		songs = [songs]
	if isinstance(parts, str):
		parts = [parts]
	if active_cell:
		row, col, col_name = active_cell['row'], active_cell['column'], active_cell['column_id']
		tmp = lout.model_obj.df_clas_without_norm.reset_index().copy()
		tmp = tmp.loc[(tmp['filename'].isin(songs)) \
                            & (tmp['part'].isin(parts)), :]
		song_name = tmp['filename'].iat[row]
		part = tmp['part'].iat[row]
		val_anorm = tmp[col_name].iat[row]
		tmp = lout.model_obj.df_clas_helper.reset_index().copy()
		tmp = tmp.loc[(tmp['filename'].isin(songs)) \
                            & (tmp['part'].isin(parts)), :]
		val_norm = tmp[col_name].iat[row] # valor normalizado
		cluster = tmp['label'].iat[row] # label
		tmp = lout.model_obj.centers.copy()
		val_center = tmp.iloc[cluster, ].values[0]

		ret_value = dcc.Markdown(f"""
		Para la cancion: {song_name}
		en la sección {part}, el valor de la columna {col_name}:
		* antes de normalizar es *{val_anorm}*
		* el valor normalizado es: *{val_norm}*
		* esta sección pertenece al cluster: **{cluster}**
		* y el valor del centroide en este punto es: **{val_center}**
		""")
		return ret_value
	else:
		return "selecciona un valor"
    

@app.callback(
	Output('tbl-out-2', 'children'),
	Input('table-2', 'active_cell'),
	State('dropdown-songs-compare', 'value'), State('dropdown-part-compare', 'value'), State('checklist-cluster-compare', 'value')
)
def update_graphs_2(active_cell, songs, parts, clusters):
	if isinstance(songs, str):
		songs = [songs]
	if isinstance(parts, str):
		parts = [parts]
	if active_cell:
		row, col, col_name = active_cell['row'], active_cell['column'], active_cell['column_id']
		tmp = lout.model_obj.df_clas_without_norm.reset_index().copy()
		tmp = tmp.loc[(tmp['filename'].isin(songs)) \
                            & (tmp['part'].isin(parts)), :]
		song_name = tmp['filename'].iat[row]
		part = tmp['part'].iat[row]
		val_anorm = tmp[col_name].iat[row]
		tmp = lout.model_obj.df_clas_helper.reset_index().copy()
		tmp = tmp.loc[(tmp['filename'].isin(songs)) \
                            & (tmp['part'].isin(parts)), :]
		val_norm = tmp[col_name].iat[row] # valor normalizado
		cluster = tmp['label'].iat[row] # label
		tmp = lout.model_obj.centers.copy()
		val_center = tmp.iloc[cluster, ].values[0]

		ret_value = dcc.Markdown(f"""
		Para la cancion: {song_name} 
		en la sección {part}, el valor de la columna {col_name}:
		* antes de normalizar es *{val_anorm}*
		* el valor normalizado es: *{val_norm}*
		* esta sección pertenece al cluster: **{cluster}**
		* y el valor del centroide en este punto es: **{val_center}**
		""")
		return ret_value
	else:
		return "selecciona un valor"

@app.callback(
	[Output('audio_player', 'src'), Output('title-song', 'children'), Output('image-song', 'src'),
	Output('audio_player_1', 'src'), Output('audio_player_2', 'src'), Output('scatter_nclicks', 'children'),
	Output('title-song-1', 'children'), Output('title-song-2', 'children'),
	Output('image-song-1', 'src'), Output('image-song-2', 'src')], Output('song-content-1', 'className') ,Output('song-content-2', 'className'),
	# Output('inicators-graph', 'figure'),  Output('force-graph', 'figure')],
	Input('scatter_graph', 'clickData'), State('scatter_nclicks', 'children'), State('audio_player_1', 'src'), State('audio_player_2', 'src'),
	State('title-song-1', 'children'), State('title-song-2', 'children'), State('image-song-1', 'src'), State('image-song-2', 'src'),
	prevent_initial_call=True
)
def refresh_audio_player(clickData, n_clicks, src1, src2, tit1, tit2, isrc1, isrc2):
	path = 'assets/Audio/'
	path_image='assets/spectograms/'

	song = Song(path)
	song_name, part = clickData['points'][0]['customdata'][3], clickData['points'][0]['customdata'][4]
	song_section_name, spectogram_section = song.get_path_to_section(song_name, part)

	# machete para nombres raros de canciones
	tmp_song_name = clickData['points'][0]['customdata'][3][:-4].replace('.', '')+'.jpg'
	n_clicks = int(n_clicks)
	n_clicks = n_clicks + 1
	ret_value = []
	if (n_clicks % 2) != 0:
		# para el input 1
		ret_value = [path + clickData['points'][0]['customdata'][3], clickData['points'][0]['customdata'][3],
		path_image + tmp_song_name , song_section_name, src2, n_clicks,
		f"{song_name} {part}", tit2 , spectogram_section, isrc2, 'song-active', '']
	else:
		# para el input 2
		ret_value = [path + clickData['points'][0]['customdata'][3], clickData['points'][0]['customdata'][3],
		path_image + tmp_song_name, src1, song_section_name, n_clicks,
		tit1, f"{song_name} {part}", isrc1, spectogram_section,  '', 'song-active']

	return ret_value

@app.callback(
	Output('shap_force_graph', 'children'),
	Input('scatter_graph', 'hoverData')
)
def draw_shap_force_frame(hover):
	if not hover:
		raise dash.exceptions.PreventUpdate("cancel the callback")
	ind = hover['points'][0]['pointIndex']
	explainer, shap_values= lout.explainer, lout.shap_values
	choosen_instance = lout.df_original.loc[[ind]]
	shap_values = explainer.shap_values(choosen_instance)
	return _force_plot_html(explainer.expected_value[0], shap_values[1], choosen_instance)

def _force_plot_html(*args):
    force_plot = shap.force_plot(*args, matplotlib=False)
    shap_html = f"<head>{shap.getjs()}</head><body>{force_plot.html()}</body>"
    return html.Iframe(srcDoc=shap_html,
                       style={"width": "100%", "height": "200px", "border": 0})

@app.callback(
	[Output('graph-scatterpolar', 'figure'), Output('cluster-titles', 'children'),
	 Output('cluster-shap', 'children'),  Output('cluster-activation', 'children')],
	Input('button_refresh_neural', 'n_clicks'),
	State('mean-or-median-toogle', 'value'), State('checklist-cluster-neural', 'value'),
	prevent_initial_call=True
)
def update_neural_page(clickData, meantoogle, clusterlist):
	list_clusters = [ int(x) for x in clusterlist]
	tmp = lout.data.df_centers.iloc[list_clusters, :]
	fig1 = lout.graph_obj.create_scatterpolar(tmp)
	
	return [fig1, lout.get_row_of_cluster_titles(clusterlist),
		lout.get_row_of_shap_figures(clusterlist),
		lout.get_row_of_clasification_graph(clusterlist, meantoogle)]

@app.callback(
	Output('graph-bar-neural', 'figure'), Output('tabs-content-audio-neural', 'children'), 
	Output('scatter_graph_neural', 'figure'), Input('button-refresh-neural', 'n_clicks'), 
	State('dropdown-songs-neural', 'value'), State('dropdown-part-original', 'value'), 
	prevent_initial_call=True
)
def update_neural_graphs_page(clickData, songs, parts):
	aux_cen = lout.data.reduced_centers.copy()
	aux_dat = lout.data.reduced_data.copy()
	aux = lout.data.df_feats.reset_index().copy()

	if isinstance(songs, str):
		songs = [songs]
	if isinstance(parts, str):
		parts = [parts]
	
	fig_bar = lout.graph_obj.create_bar_chart_neural(aux, songs, parts)
	audio_bar = lout.get_audio_controls(songs, parts)
	if songs == None:
		scatter = lout.graph_obj.create_neural_point_distribution(
																aux_dat, aux_cen)
	else:
		if parts == None:
			scatter = lout.graph_obj.create_neural_point_distribution(
			aux_dat.loc[aux_dat['f'].isin(songs), :], 
			aux_cen)
		else:
			scatter = lout.graph_obj.create_neural_point_distribution(
			aux_dat.loc[(aux_dat['f'].isin(songs)) & aux_dat['part'].isin(parts), :], 
			aux_cen)

	return fig_bar, audio_bar, scatter

@app.callback(
	Output('summary-section-song', 'children'),
	Input('scatter_graph_neural', 'clickData'),
	prevent_initial_call=True

)
def create_summary_info_from_section(clickData):
	aux = lout.data.df_feats.reset_index()
	song_name, part = clickData['points'][0]['customdata'][3], clickData['points'][0]['customdata'][6]
	title = [html.H3(song_name),html.Br(),html.H5(part), "- Generalidades de la seccion"]
	tmp = aux.loc[(aux['filename']== song_name) & (aux['part']==part), :].copy()
	mode_df = tmp.groupby(['filename', 'part'])['cluster'].agg(pd.Series.mode).reset_index()
	table = dash_table.DataTable(
                      mode_df.to_dict('records'),
                      [{"name": i, "id": i} for i in mode_df.columns],
                      style_data={
                          'color': 'black',
                          'backgroundColor': 'white'
                      },
                      style_data_conditional=[
                          {
                              'if': {'row_index': 'odd'},
                              'backgroundColor': 'rgb(220, 220, 220)',
                          }
                      ],
                    )
	
	audio_html = lout.get_audio_controls([song_name], [part])
	
	ret_list = title + [table] + audio_html
	return ret_list

@app.callback(
	Output('song-part-to-compare', 'children'), Output('song-part-to-compare', 'style'),
	Input('table-summary', 'active_cell'),
	prevent_initial_call=True
)
def update_song_part_in_summary(click_data_table):
	path = 'assets/Audio/'
	if click_data_table:
		row, col, col_name = click_data_table['row'], click_data_table['column'], click_data_table['column_id']
		tmp = lout.model_obj.df_clas_without_norm.reset_index().copy()
		song_name = tmp['filename'].iat[row]
		part = tmp['part'].iat[row]
		song = Song(path)
		song_section_name, _ = song.get_path_to_section(song_name, part)
		ret_value = [ 
          html.P(children= ['Segmento Seleccionado: ', song_name]),
          html.P(children= part , className="fs-6 title-song-1"),
          html.Audio(className="audio-section",
            controls=True,
            src=song_section_name,
            children=["Tu explorador no soporta audio"]
          )
		]
		return ret_value, {'height':'150px'}
	else:
		return "", {}


if __name__ == '__main__':
	app.run_server(host='localhost', debug=True) #local
	# server.run() #aws