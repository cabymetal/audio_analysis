import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

class GraphData(object):
	"""Clase encargada de generar la gráfica de puntos de la página
	 Recibe un dataframe """

	def __init__(self, data:pd.DataFrame, des_name:str, x_name:str, y_name:str, color_name:str=None) -> None:
		self.data = data
		self.color_name = color_name
		self.des_name = des_name
		self.x_name = x_name
		self.y_name = y_name
		self.__prepare_data()


	def __prepare_data(self):
		# do something to prepare data
		columns = [self.des_name, self.x_name, self.y_name]
		if self.color_name:
			columns.append(self.color_name)

		self.data = self.data.loc[:, columns]
		

	def draw_figure(self):
		if self.color_name:
			fig = px.scatter(self.data, x=self.x_name, y=self.y_name, hover_data=[self.des_name], color=self.color_name)
		else:
			fig = px.scatter(self.data, x=self.x_name, y=self.y_name, hover_data=[self.des_name])
		fig.update_layout(clickmode='event+select')
		return fig

	def draw_scatter_classification(self, reduced_data, reduced_centers):
		fig = go.Figure()
		colors = {0: '#0044FF', 1:'#751017', 2:'#48a832', 3:'#6b1075'}
		song_array = reduced_data['f'].unique()
		for i, song in enumerate(song_array):
		    tmp = reduced_data.loc[reduced_data['f'] == song, :].copy()
		    tmp['color'] = tmp['yhat'].apply(lambda x: colors[x])
		    tmp_fig = go.Scatter(x=tmp['x'], y=tmp['y'], name=str(i), mode='markers', marker_color=tmp['color'],
		                        text=tmp['f'], customdata = tmp)
		    fig.add_trace(tmp_fig)

		fig.update_traces(hovertemplate='<b>%{customdata[3]}</b><br>%{customdata[4]}<br>(%{x:.3f},%{y:.3f})<extra>%{customdata[2]}</extra>')
		fig.update_layout(
		    legend=dict(
		        font=dict(
		            family="Courier",
		            size=10,
		            color="black"
		        ),
		        bgcolor="LightBlue",
		        bordercolor="Black",
		        borderwidth=1
		    ),
		    clickmode = "event+select",
		    xaxis_range=(reduced_data['x'].min()-0.1, reduced_data['x'].max()+0.1),
		    yaxis_range=(reduced_data['y'].min()-0.1, reduced_data['y'].max()+0.1),
		    title="Clasificación de secciones importantes de canciones"
		)

		fig.add_trace(go.Scatter(x=reduced_centers['x'], y=reduced_centers['y'], mode='markers',
		                        marker={'size':16, 'color':'black', 'opacity':0.6},
		                        line=dict(
		                            color='MediumPurple',
		                            width=2),
		                        showlegend=False)) #centroides
		return fig