import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import librosa.display as plt_dis
import soundfile as sf
import librosa
import math
import os
import sys
from sklearn.preprocessing import normalize
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import label_binarize
import shap
import urllib.parse
import pdb

class Song(object):
	"""clase encargada de obtener características de un archivo de canción"""
	def __init__(self, path:str, sample_rate:int = 44100)->None:
		self.path = path
		self.sr = sample_rate
		#self.data= librosa.load(self.path, sr = self.sr)
		#self.create_spectogram_image()


	def get_name(self) -> str:
		return self.path.split('/')[-1]

	def get_duration_from_song(self) -> float:
		duration = librosa.get_duration(y=self.data[0], sr=self.sr)
		return duration #duración en segundos

	def get_tempo(self)->float:
		tempo = librosa.beat.beat_track(y=self.data[0], sr=self.sr)
		return tempo[0]

	def get_zero_crossing_rate(self)->float:
		zcr = librosa.feature.zero_crossing_rate(y=self.data[0])
		return int(np.sum(zcr))

	def create_spectogram_image(self)->None:
		fig, ax = plt.subplots(figsize=(8,8))
		data_length = int(len(self.data[0])/1.9)
		spectogram_matrix = librosa.amplitude_to_db(np.abs(librosa.stft(self.data[0][0:data_length])), ref=np.max)
		colormesh = plt_dis.specshow(spectogram_matrix ,y_axis='linear', x_axis='time', sr=self.sr, cmap='inferno', ax=ax)
		plt.savefig(f'assets/spectograms/{self.get_name()[:-3].replace(".", "")}.jpg')
		plt.clf()
		plt.close('all')
		del fig
		del ax

	def get_section_from_audio(self, audio_data, sr, seconds = 15):
		dur = math.ceil(librosa.get_duration(y=audio_data, sr=sr))
		steps = (dur // seconds) - 1
		section = len(audio_data) // steps
		for i in range(steps):
			yield audio_data[section*i: section*(i+1)], f'part_{i}'

	def create_spectogram_image_section(self, song_path, audio_data):
		spectogram_path = f'{song_path[:-4]}.jpg'
		if os.path.exists(song_path):
			return spectogram_path
		fig, ax = plt.subplots(figsize=(8,8))
		spectogram_matrix = librosa.amplitude_to_db(np.abs(librosa.stft(audio_data)), ref=np.max)
		colormesh = plt_dis.specshow(spectogram_matrix ,y_axis='log', x_axis='time', sr=self.sr, cmap='inferno', ax=ax)
		plt.savefig(spectogram_path)

	def get_path_to_section(self, song_name, part):
		song_prefix, extension = song_name[:-4], song_name[-4:] #remove the .wav ending
		song_prefix = song_prefix.replace(".", '')
		new_song_name = f'{self.path}{song_prefix}_{part}{extension}'
		new_song_spectogram_path = f'./assets/spectograms/{song_prefix}_{part}.jpg'
		if os.path.exists(new_song_name):
			return urllib.parse.quote(new_song_name), urllib.parse.quote(new_song_spectogram_path)

		section_data, sr = librosa.load(f'{self.path}{song_name}', sr = self.sr)
		for i, x in self.get_section_from_audio(section_data, self.sr):
			if x == part:
				audio_section = i
				break

		
		spectogram_path = self.create_spectogram_image_section(new_song_spectogram_path, audio_section)
		sf.write(new_song_name, audio_section, self.sr)
		return new_song_name, urllib.parse.quote(spectogram_path) 




class DataSongs(object):

	def get_initial_metadata(self, row):
		complete_path = os.path.join(row['path'], row['nombre'])
		song = Song(complete_path)
		duration = song.get_duration_from_song()
		tempo = song.get_tempo()
		zcr = song.get_zero_crossing_rate()
		return duration, tempo, zcr
	
	def create_data_frame_from_path(self, path):
		songs = os.listdir(path)
		df = pd.DataFrame(data = {'path': [path] * len(songs),'nombre': songs})
		df[['duration', 'tempo', 'zero_crossing_rate']] = df.apply(self.get_initial_metadata, axis=1, result_type='expand')
		return df


class DataProcessing(object):
	def __init__(self, dataset_path):
		df = pd.read_csv(dataset_path, delimiter=';')
		df_clas = df.iloc[:, 2:-6]
		df_clas.set_index([df_clas.index, 'filename', 'part'], inplace=True)
		columns = ['amplitude_envelope', 'rmse', 'zero_crossing_rate', 'spectral_centroid']
		mfcc_cols = [f'mfcc{x+1}' for x in range(13)]
		columns = columns + mfcc_cols
		self.df_clas = df_clas.loc[:, columns]
		self.df_clas_without_norm = df_clas.loc[:, columns].copy()
		self.df_clas = self.normalize_data()
		self.fit_class_model()
		self.df_clas_helper = self.df_clas.copy()
		self.df_clas_helper['label'] = self.yhat
		self.df_summary = self.df_clas.copy()
		self.df_summary['label'] = self.yhat
		self.df_summary = self.get_summary_data(self.df_summary)
		


	def normalize_data(self):
		df_clas = pd.DataFrame(
			normalize(
				self.df_clas, axis=0
			), columns=self.df_clas.columns, index=self.df_clas.index
			).drop_duplicates()
		return df_clas

	def fit_class_model(self, k=4):
		self.model = KMeans(n_clusters=k)
		self.fitted_model = self.model.fit(self.df_clas)
		self.yhat = self.model.predict(self.df_clas)

		centers = self.model.cluster_centers_
		self.centers = pd.DataFrame(centers)
		self.centers.columns = self.df_clas.columns

	def reduce_variables_pca(self):
		pca = PCA(n_components=2)

		reduced_data = pca.fit_transform(self.df_clas)
		reduced_data = pd.DataFrame(reduced_data, columns=['x', 'y'])
		reduced_data['yhat'] = self.yhat
		reduced_data['yhat'] = reduced_data['yhat'].astype('category')
		reduced_data['f'] = self.df_clas.reset_index([1])['filename'].tolist()
		reduced_data['f'] = reduced_data['f'].astype('category')
		reduced_data['p'] = self.df_clas.reset_index([2])['part'].tolist()
		reduced_data['p'] = reduced_data['p'].astype('category')

		# apply the same for centers
		reduced_centers = pca.fit_transform(self.centers)
		reduced_centers = pd.DataFrame(reduced_centers, columns=['x', 'y'])

		return (reduced_data, reduced_centers)

	def get_duration(self, song_name) -> float:
		audio_data, sr = librosa.load(song_name, sr=44100)
		duration = librosa.get_duration(y=audio_data, sr=sr)
		return duration

	def get_summary_data(self, df):
		df = df.groupby(['filename'])['label'].agg(lambda x: x.value_counts().index[0]).reset_index()
		df['duration'] = df['filename'].apply(lambda x: self.get_duration('assets/Audio/' + x))
		return df
	
	def read_all_data(self, song_name):
		df = pd.read_csv('out_dataset_1.csv', delimiter=';')
		df2 = self.df_summary.copy()
		mindur, maxdur = df2['duration'].min(), df2['duration'].max()
		cluster = df2.loc[df2['filename'] == song_name, 'label'].values[0]
		songdur = df2.loc[df2['filename'] == song_name, 'duration'].values[0]
		df = df.loc[df['filename'] == song_name, :]

		return mindur, maxdur, songdur, cluster, df

	def shapley_force_data (self):
		columns = ['amplitude_envelope', 'rmse', 'zero_crossing_rate', 'spectral_centroid']
		mfcc_cols = [f'mfcc{x+1}' for x in range(13)]
		columns = columns + mfcc_cols
		clas_result = self.fitted_model.labels_ #resultado de la calsificación 'yhat'
		clas_result = label_binarize(clas_result, classes=[0,1,2,3])
		df = pd.read_csv('./out_dataset_1.csv', delimiter=';') #data original antes de escalar
		df_clas_original = df.iloc[:, 2:-6]
		df_clas_original = df_clas_original.loc[:, columns].drop_duplicates()
		clf=RandomForestClassifier(max_depth=4)
		clf.fit(df_clas_original,clas_result)
		explainer= shap.TreeExplainer(clf)
		shap_values = explainer(df_clas_original)

		return df_clas_original, clas_result, explainer, shap_values















