import plotly.express as px
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