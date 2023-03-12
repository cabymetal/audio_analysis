from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import dash_daq as daq
import plotly.express as px
import pandas as pd
import grapher
from clasificacion import DataSongs, Song
from clasificacion import DataProcessing
from clasificacion import DataNeuralNetwork
import urllib.parse
import pdb

############################################### AUX FUNCTIONS ##################################################################
def draw_controls(df_clas):
  aux_df = df_clas.reset_index().copy()
  songs = aux_df['filename'].drop_duplicates().values
  parts1 = aux_df.loc[aux_df['filename'] == songs[0], 'part'].values
  parts2 = aux_df.loc[aux_df['filename'] == songs[1], 'part'].values
  songs_dropdown_original = dcc.Dropdown(
              id='dropdown-songs-original',
              options=[{'label': x, 'value': x} for x in songs],
              value=songs[0],
              multi= True,
              className="form-control form-control-sm" )
  songs_dropdown_compare = dcc.Dropdown(
              id='dropdown-songs-compare',
              options=[{'label': x, 'value': x} for x in songs],
              value=songs[1],
              multi= True,
              className="form-control form-control-sm" )
  
  dropdown_part_original = dcc.Dropdown(
      id='dropdown-part-original',
      options=[{'label': x, 'value': x} for x in parts1],
      value=parts1[0],
      multi=True,
      className='form-control form-control-sm')
  dropdown_part_compare = dcc.Dropdown(
      id='dropdown-part-compare',
      options=[{'label': x, 'value': x} for x in parts2],
      value=parts2[0],
      multi=True,
      className='form-control form-control-sm')

  check_cluster1 = dcc.Checklist(
    id = 'checklist-cluster-original',
    options = ['0', '1', '2', '3'],
    value = ['0', '1', '2', '3'],
    inline=True,
    className='form-group'
  )
  check_cluster2 = dcc.Checklist(
    id = 'checklist-cluster-compare',
    options = ['0', '1', '2', '3'],
    value = ['0', '1', '2', '3'],
    inline=True,
    className='form-group'
  )

  check_cluster_neural = dcc.Checklist(
    id = 'checklist-cluster-neural',
    options = ['0', '1', '2', '3'],
    value = ['0', '1', '2', '3'],
    inline=True,
    className='form-group'
  )

  switch = daq.ToggleSwitch(
    id="mean-or-median-toogle",
    size=50,
    label= "Media o Mediana"
  )

  df_song_1 = aux_df.loc[aux_df['filename']== songs[0], :].copy()
  df_song_2 = aux_df.loc[aux_df['filename']== songs[1], :].copy()

  
  #return dict
  array_control_elements = {
    'drop_songs_original': songs_dropdown_original,
    'drop_songs_compare': songs_dropdown_compare,
    'drop_part_original' : dropdown_part_original,
    'drop_part_compare' : dropdown_part_compare,
    'check_cluster_original' : check_cluster1,
    'check_cluster_compare': check_cluster2,
    'data_bar_chart_1' : df_song_1,
    'data_bar_chart_2' : df_song_2,
    'song_selection_1' : [songs[0]],
    'song_selection_2' : [songs[1]],
    'parts_selection_1' : parts1,
    'parts_selection_2' : parts2,
    'check_neural': check_cluster_neural,
    'switch': switch,
  }

  return array_control_elements

def draw_controls_neural(df_reduced):
  aux_df = df_reduced.reset_index().copy()
  songs = aux_df['f'].drop_duplicates().values
  parts1 = aux_df.loc[aux_df['f'] == songs[0], 'part'].drop_duplicates().values
  songs_dropdown_neural = dcc.Dropdown(
              id='dropdown-songs-neural',
              options=[{'label': x, 'value': x} for x in songs],
              value='selecciona un valor',
              multi= True,
              className="form-control form-control" )
  
  dropdown_part_neural = dcc.Dropdown(
      id='dropdown-part-original',
      options=[{'label': x, 'value': x} for x in parts1],
      value='selecciona una cancion',
      multi=True,
      className='form-control form-control')
  
  array_control_elements = {
    'drop_songs_neural': songs_dropdown_neural,
    'drop_part_neural' : dropdown_part_neural
  }

  return array_control_elements

#################################################### logica de ejecucion ##############################################

#leer data
m = DataSongs()
path = './assets/Audio/'
#df = m.create_data_frame_from_path(path) #exportar data para que no se demore en la prueba.
df = pd.read_csv('tmp_data.csv')
model_obj = DataProcessing('./out_dataset_1.csv')
red_df, red_cen = model_obj.reduce_variables_pca()
song_name = 'Death on the Balcony - Tempt Of Fate.wav'
song = Song(path)
part = 'part_0'
song_section_name, spectogram_section = song.get_path_to_section(song_name, part)
mindur, maxdur, songdur, cluster, df_data = model_obj.read_all_data(song_name)
df_original, labels, explainer, shap_values = model_obj.shapley_force_data()
graph_obj = grapher.GraphData(df, 'nombre', 'duration', 'tempo', 'zero_crossing_rate')
#instanciar gráficas
fig_graph = graph_obj.draw_figure()
clas_graph = graph_obj.draw_scatter_classification(red_df, red_cen)
ind_graph = graph_obj.draw_indicator_info(mindur, maxdur, songdur, cluster, song_name)
force_graph = graph_obj.draw_shap_cluster_beeswarm(0, df_original, labels)
controls = draw_controls(model_obj.df_clas_helper)
data = DataNeuralNetwork('assets/data_neural_network.csv', 
                           'assets/data_centers_neural.csv')
controls_1 = draw_controls_neural(data.reduced_data)

############################################### FUNCTION FOR SECTIONS ##########################################################
def get_control_for_dashboard_classic():
  controls_for_dashboard = dbc.Row([
        html.H3(children="Controles"),
        dbc.Col([
          dbc.Col(children=[
            html.Div(className="form-group-row", children=[
              html.Label("Seleccionar Canción:", htmlFor="dropdown-songs-original"), 
              controls['drop_songs_original'] 
            ]),
            html.Div(className="form-group-row", children=[
              html.Label("Seleccionar Secciones canción 1:", htmlFor="dropdown-part-original"), 
              controls['drop_part_original'] 
            ]),
            # html.Div(className="form-group-row", children=[
            #  html.Label("selección Cluster (1):", htmlFor="checklist-cluster-original"), 
            #  controls['check_cluster_original']
            #]), # not used
            html.Button('Actualizar bloque 1', id='button-refresh-song1')
          ]
            
          ),          
        ], width= 6),
        dbc.Col([
          dbc.Col(children=[
            html.Div(className="form-group-row", children=[
              html.Label("Seleccionar Canción:", htmlFor="dropdown-songs-compare"), 
              controls['drop_songs_compare'] 
            ]),
            html.Div(className="form-group-row", children=[
              html.Label("Seleccionar Secciones canción 2:", htmlFor="dropdown-part-compare"), 
              controls['drop_part_compare'] 
            ]),
            # html.Div(className="form-group-row", children=[
            #  html.Label("selección Cluster (2):", htmlFor="checklist-cluster-compare"), 
            #   controls['check_cluster_compare']
            #]), # not used
            html.Button('Actualizar bloque 2', id='button-refresh-song2'),
          ] 
         ),
        ], width=6)
    ])#outer row

  return controls_for_dashboard

def get_audio_controls(songs_selected, parts_selected):
  
  html_response = []
  tmp = model_obj.df_clas_helper.reset_index().copy()
  if songs_selected == None:
    songs_selected = tmp.loc[:, 'filename'].drop_duplicates().values
  if parts_selected == None:
    parts_selected = tmp.loc[(tmp['filename'].isin(songs_selected)), 'part'].drop_duplicates().values
  for song in songs_selected:
    for part in parts_selected:
      cluster = tmp.loc[(tmp['filename']==song) & (tmp['part']==part), 'label'].values
      if len(cluster) == 0:
        continue
      cluster = cluster[0]
      song_part = f"{song[:-4]}_{part}.wav"
      src_audio = "assets/Audio/"
      src_audio = f"{src_audio}{song_part}"
      
      row = dbc.Row([
              dbc.Col([html.Span(song_part, className="song-name-string")], width=7),
              dbc.Col([html.Span(cluster, className="song-name-cluster")], width=1),
              dbc.Col([html.Audio(
                      controls=True,
                      src = urllib.parse.quote(src_audio),
                      children=["Tu explorador no soporta audio"]
              )], width=4)
            ])
      html_response.append(row)
  return html_response

def get_table_detailed(songs_selected, parts_selected, id='1'):
  tmp = model_obj.df_clas_without_norm.reset_index().copy()
  tmp = tmp.loc[(tmp['filename'].isin(songs_selected)) \
                            & (tmp['part'].isin(parts_selected)), :]
  html_response = [
                    dash_table.DataTable(
                      tmp.to_dict('records'),
                      [{"name": i, "id": i} for i in tmp.columns],
                      id=f'table-{id}',
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
                    ),
                    dbc.Alert(id=f'tbl-out-{id}')
                  ]
  
  return html_response
  

def get_first_row_to_compare():	
  first_row_layout = dbc.Row([
		dbc.Col([ 
				html.Div( className="card", children=[
          html.Div(className="card-header", children=[
            dbc.Row([
              dbc.Col([html.H5("Bloque análisis 1: "), html.Span( className="title-song-1")], width=11),
              dbc.Col(html.Button(html.I(className="fas fa-eye"), className="btn"), width=1),
            ], id='tooltip-tcol-share-tgrupo'),
            dbc.Tooltip(
                "Sección muestra características generales de la canción",
                target="tooltip-tcol-share-tgrupo",
            ),
          ]), #titulo card
          html.Div(className="card-body", children=[
            dbc.Tabs([
                dbc.Tab(dcc.Graph( id='graph-bar-cluster-1', figure= graph_obj.create_bar_chart(controls['data_bar_chart_1'],	controls['song_selection_1'])), 
                        label="Discriminación de Clústers"),
                dbc.Tab(
                  get_audio_controls(controls['song_selection_1'], controls['parts_selection_1'][:1])
                , label="Sección(es) Audio 1", id="tabs-content-audio-1"),
                dbc.Tab(get_table_detailed(controls['song_selection_1'], controls['parts_selection_1'][:1], '1')
                , label="Detalle selección", id="tabs-table-audio-1")
            ])
          ])
		    ]) #close Div
		], width=6), # primer columna
    dbc.Col(
			[ html.Div( className="card", children=[
          html.Div(className="card-header", children=[
            dbc.Row([
              dbc.Col([html.H5("Bloque analisis 2: "), html.Span( className="title-song-2")], width=11),
              dbc.Col(html.Button(html.I(className="fas fa-eye"), className="btn"), width=1),
            ], id='tooltip-tcol-share-tgrupo'),
            dbc.Tooltip(
                "Sección muestra características generales de la canción",
                target="tooltip-tcol-share-tgrupo",
            ),
          ]), #titulo card
          html.Div(className="card-body", children=[
            dbc.Tabs([
              dbc.Tab(dcc.Graph( id='graph-bar-cluster-2', 
                                 figure= graph_obj.create_bar_chart(controls['data_bar_chart_2'], controls['song_selection_2'])
                                )
                      , label="Discriminación clústers"),
                dbc.Tab(get_audio_controls(controls['song_selection_2'], controls['parts_selection_2'][:1])
                , label="Sección(es) Audio 2", id="tabs-content-audio-2"),
                dbc.Tab(get_table_detailed(controls['song_selection_2'], controls['parts_selection_2'][:1], '2')
                , label="Detalle selección", id="tabs-table-audio-2")
              ])
			      ]), #close Div
					])
	  ], width=6)
  ])

  return first_row_layout

def get_third_row_to_compare():
  html_response = dbc.Row([
        
      dbc.Col(children=
        [ 
          html.P(children= ['Canción Completa: ']),
          html.P(id='title-song', children='', className="fs-6 title-song-1"),
          html.Audio(id='audio_player',className="audio-section",
            controls=True,
            src="",
            children=["Tu explorador no soporta audio"]
          )
        ],        
      ),
      dbc.Col( children= 
        [
          html.P(children= ['Sección: ']),
          html.P(id='title-song-1', children='', className="fs-6 title-song-1"),
          html.Audio(id='audio_player_1', className="audio-section",
            controls=True,
            children=["Tu explorador no soporta audio"]),
           
        ],
        id='song-content-1',
        className="",
      ),
      dbc.Col(  children=[
        html.P(children= ['Sección: ']),
        html.P(id='title-song-2', children='', className="fs-6"),
        html.Audio(id='audio_player_2',className="audio-section",
          controls=True,
          src = "",
          children=["Tu explorador no soporta audio"]
        )
        ],
        id='song-content-2',
        className=""
      ) 
    ],
    style={'height': '200px'})
  return html_response

def get_fourth_row_to_compare():
  html_response = dbc.Row( children=[
    dbc.Col([
      html.H4("Detalle de canción"),
      html.Img(id='image-song', src=spectogram_section,
               style={'width':'90%'})
    ]),
    dbc.Col([
      html.H4("Spectograma sección 1"),
      html.Img(id='image-song-1', src=spectogram_section, style={'width':'90%'})
    ]),
    dbc.Col([
      html.H4("Spectograma sección 2"),
      html.Img(id='image-song-2', src=spectogram_section, style={'width':'90%'})
    ])  
  ])
  return html_response


def get_home_layout():
  layout = dbc.Container(fluid=False, children=[
      dbc.Row([
        html.H1(children='Grafica Canciones'),
        html.Div(children='''
            Dash: Aplicación para mostrar canciones, se realiza separación de la canción en secciones de 15 segundos como se muestra
            en el Jupyter Notebook de análisis del proyecto.
        ''')
      ]),
      get_control_for_dashboard_classic(),  
      html.Hr(),html.Br(),
      get_first_row_to_compare(),
      dbc.Row([
        dbc.Col([dcc.Graph(id='scatter_graph', figure=clas_graph), html.P(id="scatter_nclicks", children="0", hidden=True)], width=8),
        dbc.Col([html.Div(id='shap_force_graph', children=[])], width=4),
      ]),
      get_third_row_to_compare(),
      get_fourth_row_to_compare()
  ])

  return layout

def get_readme_markdown():
  fp = open('README.md', 'r', encoding='utf-8')
  read_content = fp.read()
  fp.close()
  readme_layout= dbc.Container(fluid=False, children=[
    dcc.Markdown(read_content, dangerously_allow_html =True)
  ])
  return readme_layout
##################################### neural page functions ###############################
def get_row_controls_and_scatter(list_clusters):
  list_clusters = [ int(x) for x in list_clusters]
  tmp = data.df_centers.iloc[list_clusters, :]
  fig1 = graph_obj.create_scatterpolar(tmp)
  list_cols = [
    html.H3(children="Controles"),
    dbc.Col([
      dbc.Col(children=[
        html.Div(className="form-group-row", children=[
          html.Label("selección Cluster:", htmlFor="checklist-cluster-neural"), 
          controls['check_neural']
        ]),
        html.Div(children=[
          html.Span("Media o Mediana:"),
          controls['switch']
        ]),
        html.Br(),
        html.Div(html.Button('Actualizar información', id='button_refresh_neural', className='btn btn-primary'))
      ]
        
      ),          
    ], width= 4),
    dbc.Col(dcc.Graph(id='graph-scatterpolar', figure= fig1), width=8)
  ]
  row_layout = dbc.Row(children=list_cols)
  return row_layout
  

def get_row_of_cluster_titles(list_clusters):
  list_cols = []
  for k in list_clusters:
    col = dbc.Col(children=[
      html.H2(f"K-{k}", className="text-center")
    ], width=12/len(list_clusters))
    list_cols.append(col)
  
  row_layout = dbc.Row(dbc.Row( children=list_cols , id='cluster-titles'))
  return row_layout

def get_row_of_clasification_graph(list_clusters, is_mean=False):
  list_cols = []
  for k in list_clusters:
    name = 'activation_mean.jpg'
    if is_mean:
      name = 'activation_median.jpg'
    col = dbc.Col(children=[
      html.Img(src=f'assets/analysis_spectograms/{k}/{name}', style={'width':'90%'})
    ], width=12/len(list_clusters))
    list_cols.append(col)
  
  row_layout = dbc.Row( children=list_cols, id='cluster-activation' )
  return row_layout

def get_row_of_shap_figures(list_clusters):
  list_cols = []
  for k in list_clusters:
    name = 'shap_figure.jpg'
    col = dbc.Col(children=[
      html.Img(src=f'assets/analysis_spectograms/{k}/{name}', style={'width':'90%'})
    ], width=12/len(list_clusters))
    list_cols.append(col)
  
  row_layout = dbc.Row( children=list_cols,id='cluster-shap' )
  return row_layout

def get_row_controls_neural():
  controls_for_dashboard = dbc.Row([
        html.H3(children="Controles"),
        dbc.Col([
          dbc.Col(children=[
            html.Div(children=[
              html.Div(className="form-group-row", children=[
              html.Label("Seleccionar Canción:", htmlFor="dropdown-songs-neural"), 
              controls_1['drop_songs_neural'] 
              ]),
              html.Div(className="form-group-row", children=[
                html.Label("Seleccionar Secciones canción 1:", htmlFor="dropdown-part-neural"), 
                controls_1['drop_part_neural'] 
              ]),
              html.Button('Actualizar gráfica', id='button-refresh-neural', className='btn btn-primary')    
            ]),
              html.Br(),
              html.Hr(),
              html.Br(),
              html.Div(
                children=[],
                id = "summary-section-song"
              )
            
          ]
            
          ),          
        ], width=5),
        dbc.Col(children=[
          html.Div( className="card", children=[
            html.Div(className="card-header", children=[
              dbc.Row([
                dbc.Col([html.H5("Resumen Seleccion"), html.Span( className="title-song-2")], width=11),
                dbc.Col(html.Button(html.I(className="fas fa-eye"), className="btn"), width=1),
              ], id='tooltip-tcol-share-tgrupo'),
              dbc.Tooltip(
                  "Reconstruye secciones de un segundo para analizar la información de manera completa",
                  target="tooltip-tcol-share-tgrupo",
              ),
            ]), #titulo card
            html.Div(className="card-body", children=[
              dbc.Tabs([
                dbc.Tab(dcc.Graph( id='graph-bar-neural', 
                                  figure= graph_obj.create_bar_chart_neural(data.df_feats.reset_index(), controls['song_selection_1'])
                                  )
                        , label="Discriminación clústers"),
                  dbc.Tab(get_audio_controls(controls['song_selection_1'], controls['parts_selection_1'][:1])
                  , label="Sección(es) Audio", style={'max-height': '400px', 'overflow-y': 'auto'}, id="tabs-content-audio-neural")
                ])
              ]), #close Div
					])
        ], width=7)
    ])#outer row

  return controls_for_dashboard

def get_row_clasification_fragments():
  row_layout = dbc.Row(children=[
    dbc.Col([dcc.Graph(id='scatter_graph_neural', 
                       figure=graph_obj.create_neural_point_distribution(data.reduced_data, 
                                                                         data.reduced_centers)
                      ), 
              html.P(id="scatter_nclicks_neural", children="0", hidden=True)
            ])
  ])

  return row_layout


def get_neural_network_page():
  neural_layout = dbc.Container(fluid=False, children=[
      dbc.Row([
        html.H1(children='Selección caracteristicas redes'),
        html.Div(children='''
            Visualización de cluster utilizando slección de caracteríscas preentrenadas
        ''')
      ]),
      get_row_controls_and_scatter(['0', '1', '2', '3']),
      get_row_of_cluster_titles(['0', '1', '2', '3']),
      get_row_of_clasification_graph(['0', '1', '2', '3']),
      get_row_of_shap_figures(['0', '1', '2', '3']),
      html.Hr(),
      dbc.Row([
        html.H1(children='Análisis de segmentos de canciones'),
        html.Div(children='''
            
        ''')
      ]),
      get_row_controls_neural(),
      get_row_clasification_fragments()
  ])

  return neural_layout

def summary_methods_kmeans():
  # calcular nuevo dataframe
  classic_df = model_obj.df_clas_helper.reset_index().loc[:, ['filename', 'part', 'label']].copy()
  neural_df = data.df_feats.reset_index().loc[:,['filename', 'part', 'cluster']].copy()
  neural_df = neural_df.groupby(['filename', 'part'])['cluster'].agg(pd.Series.mode).reset_index()
  neural_df['indice'] = neural_df.index
  final_df = classic_df.merge(neural_df).astype(str)
  similar = sum(sum([final_df['label']==final_df['cluster']]))/final_df.shape[0] * 100
  final_df.rename({'filename':'Nombre Cancion', 'part': 'Seccion Cancion', 'label': 'K Variables Clásicas', 'cluster':'K Redes Neuronales'}, axis=1, inplace=True)
  
  table = dash_table.DataTable(
            final_df.to_dict('records'),
            [{"name": i, "id": i} for i in final_df.columns],
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
            id= 'table-summary'
          )

  summary_layout = dbc.Container(fluid=False, children=[
      dbc.Row([
        html.H1(children='Selección caracteristicas redes'),
        html.Div(children='''
            En esta pagina se muestra una tabla en la que para cada sección y canción se determina el cluster en el que cada
            método incluye la canción
        ''')
      ]),
      dbc.Row([
        html.Div(id='song-part-to-compare')
      ]),
      dbc.Row([
        table
      ])
      
  ])
  return summary_layout

main_layout = html.Div(className="wrapper", children=[
  dcc.Location(id='url', refresh=False),
  html.Nav(id= "sidebar", children=[
      html.Div(className="sidebar-header", children=[
        html.Img(src='assets/imagenes/logo-eafit-negro.png', style={'width':'90%'})
      ]),
      html.Ul(className="list-unlisted components", children=[
        #html.P("Modalidad"),
        html.Li(children=[ html.A(href="/", children="Read me")]),
        html.Li(className="active", children=[
          html.A(href="#homeSubmenu", **{"data-toggle":"collapse", 'aria-expanded': "false"}, className="dropdown-toggle",
            children="Vista"),
          html.Ul(className="collapse list-unstyled", id="homeSubmenu", children=[
            html.Li(children=[
              html.A(href="variables_clasicas", children="Características Clásicas")
            ]),
            html.Li(children=[
              html.A(href="redes_neuronales", children="Redes Neuronales")
            ]),
            html.Li(children=[
              html.A(href="resumen", children="Comparacion métodos")
            ])
          ])
        ])
      ])
    ]),
  html.Div(id= "content", children=[
    
  ])
])


