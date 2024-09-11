# Studentest_Proyecto Backend con Django e IA - Generador de Preguntas desde PDF
Este proyecto utiliza Django como framework backend y la librería transformers con el modelo google/flan-t5-base para generar automáticamente preguntas de opción múltiple y verdadero/falso a partir de texto extraído de archivos PDF. El sistema está diseñado para crear exámenes que evalúan a los usuarios.

## Características:

 *Extracción de texto desde PDF: Se utiliza la librería PyMuPDF para extraer texto del archivo PDF.

 *Generación de preguntas automáticas: Con el modelo T5 de transformers, el sistema genera 5 preguntas de opción múltiple (con una respuesta correcta) y 5 preguntas de verdadero/falso.

 *API REST: Basada en Django REST Framework (DRF) para gestionar documentos, tests, preguntas y respuestas.

 *Autenticación JWT: Implementada con djangorestframework-simplejwt para el control de acceso seguro.

##  Requisitos:

   1-Python 3.8+

   2-Django 3.2+

   3-PyTorch

   4-Transformers (Hugging Face)

   5-Django REST Framework

   6-PyMuPDF(para la extracción de texto desde PDFs)

   7-djangorestframework-simplejwt (para autenticación)

## Instalación 

    Crea un fork del repositorio

Abre el repositorio Studentest_backend en GitHub y haz clic en el botón "Fork" en la esquina superior derecha de la página. Esto creará una copia del repositorio en tu propia cuenta de GitHub.

1.Clona tu repositorio fork

   Abre una terminal Git Bash y ejecuta el comando con el link de tu nuevo repositorio

#Clonar
 git clone https://github.com/tu-usuario/Studentest_backend.git

3. Abre Pycharm y abre el archivo que acabas de clonar

4. Para iniciar hay que crear el entorno virtual por la terminal y luego activarlo

*Crea el entorno virtual

    python -m venv venv

*Activa el entorno virtual

    venv\Scripts\activate

*Y si necesitas desactiva el entorno virtual

    venv\Scripts\deactivate

5. Realiza la otras intalaciones

   #Generará en la raíz del proyecto un fichero llamado requirements.txt

      pip freeze > requirements.txt

   #Instalación de los requerimientos

      pip install -r requirements.txt

6. Crea tu rama y comienza a trabajar!

   #Crea la rama

   git checkout -b feature/nombreDeTuRama

Desarrolladora 🖥️
Pilar Muiño
