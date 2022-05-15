# Clasificación Musical
## Proyecto de Grado Maestría

### Descripción
Por realizar

### Configuración tablero de control

Clonar o descargar una copia del repositorio

para clonar el repositorio
<p style="background:black">
<code style="background:black;color:white">C:\MISDOCUMENTOS> git clone this_repo NOMBRECARPETA
</code>
</p>

descargarlo presionar en el botón descargar
![Descargar proyecto](assets/imagenes/download.PNG)

copiar canciones a analizar en la carpeta assets/Audio/ estoy trabajando con la muestra de canciones del repositorio compartido

Crear un ambiente de ejecución utilizando `virtualenv`
<p style="background:black">
<code style="background:black;color:white">C:\MISDOCUMENTOS\NOMBRECARPETA>virtualenv -m python NOMBREAMBIENTE
</code>
</p>

una vez se crean las carpetas se procede a activar el ambiente

<p style="background:black">
<code style="background:black;color:white">C:\MISDOCUMENTOS\NOMBRECARPETA>maestria/Scripts/activate.bat
</code>
</p>

Instalar las librerías necesarias

<p style="background:black">
<code style="background:black;color:white">C:\MISDOCUMENTOS\NOMBRECARPETA> pip install -r requirements.txt
</code>
</p>

Ejecutar el proyecto

<p style="background:black">
<code style="background:black;color:white">C:\MISDOCUMENTOS\NOMBRECARPETA> python app_server.py
</code>
</p>

si todo va bien se muestra la siguiente imagen
![tablero en ejecucion](assets/imagenes/running_process.PNG)

abrir un explorador en localhost:8050 y veremos la siguiente página web con el tablero de control
![Tablero de control](assets/imagenes/dashboard.PNG)

### Análisis exploratorio de datos

Definir y escribir proceso...

