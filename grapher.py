import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as pl
import pandas as pd
import xgboost
import shap
import pdb

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
		colors = {0: '#0044FF', 1:'#FF0D57', 2:'#48a832', 3:'#6b1075'}
		song_array = reduced_data['f'].unique()
		for i, song in enumerate(song_array):
		    tmp = reduced_data.loc[reduced_data['f'] == song, :].copy()
		    tmp['color'] = tmp['yhat'].apply(lambda x: colors[x])
		    tmp_fig = go.Scatter(x=tmp['x'], y=tmp['y'], name=str(i), mode='markers', marker_color=tmp['color'],
		                        text=tmp['f'], customdata = tmp)
		    fig.add_trace(tmp_fig)

		fig.update_traces(hovertemplate='<b>%{customdata[3]}</b><br>%{customdata[4]}<br>(%{x:.3f},%{y:.3f})<extra>%{customdata[2]}</extra>')
		fig.update_layout(
				plot_bgcolor='white',
				yaxis=dict(showgrid=True, gridcolor='WhiteSmoke', zerolinecolor='Gainsboro'),
				xaxis=dict(showgrid=True, gridcolor='WhiteSmoke', zerolinecolor='Gainsboro'),
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

	def draw_indicator_info(self, mindur, maxdur, songdur, cluster, song_name):
		fig = go.Figure(go.Indicator(
    value = songdur,
    mode = "gauge+number",
    title = {'text': "duración"},
    gauge = {'axis': {'range': [mindur, maxdur]},
    	'bar':{'color':'#FF0D57'}},
    domain = {'row': 0, 'column': 0}
    ))

		fig.add_trace(go.Indicator(
			mode = "number",
			value = cluster,
			title = {'text': "cluster predominante"},
			domain = {'row': 0, 'column': 1}))

		fig.update_layout( grid = {'rows': 1, 'columns': 2, 'pattern': "independent"})

		return fig

	def draw_shap_cluster_beeswarm(self, k, df_clas_original, labels):
		# train XGBoost model
		model = xgboost.XGBClassifier().fit(df_clas_original,labels[:,k])

		# compute SHAP values
		explainer = shap.Explainer(model, df_clas_original)
		shap_values = explainer(df_clas_original)
		#pdb.set_trace()

		df = pd.DataFrame(shap_values.values, columns=df_clas_original.columns)
		df['trx_id'] = df.index
		df['pred'] = labels[:,k]

		values = df.iloc[:,:-9].abs().mean(axis=0).sort_values().index
		df_plot = pd.melt(df, id_vars=['trx_id', 'pred'], value_vars=values, var_name='Feature', value_name='SHAP')

		fig = px.strip(df_plot, x='SHAP', y='Feature', color='pred', stripmode='overlay', height=500, width=500,
			color_discrete_sequence=['#FF0D57', '#1E88E5'])
		fig.update_layout(xaxis=dict(showgrid=True, gridcolor='WhiteSmoke', zerolinecolor='Gainsboro'),
		              yaxis=dict(showgrid=False, gridcolor='WhiteSmoke', zerolinecolor='Gainsboro')
		)
		fig.update_layout(plot_bgcolor='white', title=f'caracterización cluster: {k}')

		fig = (
		    fig
		    # Make it so there is no gap between the supporting boxes
		    .update_layout(boxgap=0)
		    # Increase the jitter so it reaches the sides of the boxes
		    .update_traces(jitter=1)
		)

		#fig.write_html('plotly_beeswarm_test.html')
		return fig