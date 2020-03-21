# Brooks

Sistema de soporte para el análisis de datos
de la pandemia de COVID-19 en la provincia de
Córdoba.

Este proyecto esta distribuido con
licencia [BSD-3](https://github.com/ivco19/dashboard/blob/master/LICENSE), y
disponible publicamente en: https://github.com/ivco19/brooks

El desarrollo e investigación fue
llevado adelante por

- Vanesa Daza (IATE-FAMaF).
- Bruno Sanchez (Duke University).
- Federico Stasyszyn (IATE-FAMaF).
- Mariano Dominguez (IATE-FAMaF).
- Nadia Luczywo (LIMI-FCEFyN-UNC, FCE-UNC)
- Marcelo Lares (IATE-FAMaF).
- Juan B Cabral (IATE-FAMaF, CIFASIS-UNR).

----

## Instalacion

- Utiliza "python3.7" o superior
- Recomiendo crear un environment con virtualenv o anaconda

```bash
$ virtualenv -p $(which python3.7) brooks
source brooks/bin/activate

```

o

```bash
$ conda create -n brooks python=3.7
$ conda activate brooks
```

- Luego instalamos las dependencias

```bash
$ pip install -r requirements.txt
```

- Despues hay que crear la base datos

```bash
$ cd dashboard
$ python manage.py migrate
```

- Y por ultimo creamos un usuario y activamos el servidor

```bash
$ python manage.py createsuperuser
...
$ python manage.py runserver
```