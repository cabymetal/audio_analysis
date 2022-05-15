import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import librosa.display as plt_dis
import librosa
import os
import sys
import pdb

class Song(object):
	"""clase encargada de obtener características de un archivo de canción"""
	def __init__(self, path:str, sample_rate:int = 44100)->None:
		super(Song, self).__init__()
		self.path = path
		self.sr = sample_rate
		self.data= librosa.load(self.path, sr = self.sr)
		self.create_spectogram_image()


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
		plt.savefig(f'assets/spectograms/{self.get_name()[:-3].replace(".", "")}.png')
		plt.clf()
		plt.close('all')
		del fig
		del ax

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




if __name__ == '__main__':
	m = DataSongs()
	path = '.\\Victor\\Victor'
	df = m.create_data_frame_from_path(path)










