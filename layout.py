from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import grapher
from clasificacion import DataSongs
from clasificacion import DataProcessing

#leer data
m = DataSongs()
path = './assets/Audio/'
#df = m.create_data_frame_from_path(path) #exportar data para que no se demore en la prueba.
df = pd.read_csv('tmp_data.csv')
model_obj = DataProcessing('./out_dataset_1.csv')
red_df, red_cen = model_obj.reduce_variables_pca()
#instanciar gráfias
fig_graph = grapher.GraphData(df, 'nombre', 'duration', 'tempo', 'zero_crossing_rate').draw_figure()
clas_graph = grapher.GraphData(df, 'nombre', 'duration', 'tempo', 'zero_crossing_rate').draw_scatter_classification(red_df, red_cen)



def get_layout():
	layout = html.Div(children=[
		dbc.Container(fluid=False, children=[
			dbc.Row([
				html.H1(children='Grafica Canciones'),
		    html.Div(children='''
		        Dash: Aplicación para mostrar canciones, se realiza separación de la canción en secciones de 15 segundos como se muestra
		        en el Jupyter Notebook de análisis del proyecto.
		    ''')
			]),
			html.Hr(),html.Br(),
			dbc.Row([
				dbc.Col([dcc.Graph(id='scatter_graph', figure=clas_graph), html.P(id="scatter_nclicks", children="0", hidden=True)], width=8),
				dbc.Col([
					dbc.Row(html.Div(
			    	className = 'audio_section_title',
			    	children=['''
			    				        Canción completa:
			    				      ''', html.Span(id='title-song', children='', className="fs-6")])
					),
					html.Br(),
					dbc.Row(
						html.Audio(id='audio_player',
			    		controls=True,
			    		children=["Tu explorador no soporta audio"]
			    	)
					),
					html.Hr(),
					html.Br(),
					dbc.Row(html.Div(
			    	className = 'audio_section_title',
			    	children=[html.P(children= ['Sección: ']),
			    				     html.P(id='title-song-1', children='', className="fs-6")])
					),
					html.Br(),
					dbc.Row(
						html.Audio(id='audio_player_1',
			    		controls=True,
			    		children=["Tu explorador no soporta audio"]
			    	)
					),
					html.Hr(),
					html.Br(),
					dbc.Row(html.Div(
			    	className = 'audio_section_title',
			    	children=[html.P(children= ['Sección: ']),
			    				    html.P(id='title-song-2', children='', className="fs-6")])
					),
					html.Br(),
					dbc.Row(
						html.Audio(id='audio_player_2',
			    		controls=True,
			    		children=["Tu explorador no soporta audio"]
			    	)
					),
				], width=4),

			]),
			html.Hr(),
			html.Br(),
			dbc.Row([
				dbc.Col([
					html.H2("Detalle de canción"),
					html.Img(id='image-song', src='assets/spectograms/Death on the Balcony - Tempt Of Fate.png', style={'width':'90%'})
				]),
				dbc.Col([
					dbc.Row([
						html.H4("Spectograma sección 1"),
						html.Img(id='image-song-1', src='assets/spectograms/Death on the Balcony - Tempt Of Fate.png', style={'width':'40%'})
					]),
					dbc.Row([
						html.H4("Spectograma sección 2"),
						html.Img(id='image-song-2', src='assets/spectograms/Death on the Balcony - Tempt Of Fate.png', style={'width':'40%'})
					])
				])
			])


	    
		])
    
  ])

	return layout