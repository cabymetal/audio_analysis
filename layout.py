from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import grapher
from clasificacion import DataSongs

#leer data
m = DataSongs()
path = './assets/Audio/'
#df = m.create_data_frame_from_path(path) #exportar data para que no se demore en la prueba.
df = pd.read_csv('tmp_data.csv')
#instanciar gráfias
fig_graph = grapher.GraphData(df, 'nombre', 'duration', 'tempo', 'zero_crossing_rate').draw_figure()




def get_layout():
	layout = html.Div(children=[
		dbc.Container(fluid=False, children=[
			dbc.Row([
				html.H1(children='Grafica Canciones'),
		    html.Div(children='''
		        Dash: Aplicación para mostrar canciones.
		    ''')
			]),
			dbc.Row([
				dbc.Col([dcc.Graph(id='scatter_graph', figure=fig_graph)], width=8),
				dbc.Col([
					html.Div(
			    	id = 'title-song',
			    	children='''
			        Mostrar canciones
			      '''),
					html.Audio(id='audio_player',
			    	controls=True,
			    	children=["Tu explorador no soporta audio"]
			    )
				], width=4),

			]),
			dbc.Row([
				dbc.Col([
					html.H2("Detalle de canción"),
					html.Img(id='image-song', src='assets/spectograms/Death on the Balcony - Tempt Of Fate.png', style={'width':'90%'})
				])
			])


	    
		])
    
  ])

	return layout