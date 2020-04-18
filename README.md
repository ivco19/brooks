# Brooks

![logo](https://raw.githubusercontent.com/ivco19/brooks/master/site/brooks/static/logo.png)

Sistema de carga rápida de datos diseñado para la pandemia de COVID-19 en la
en Argentina.

Este proyecto esta distribuido con
licencia [BSD-3](https://github.com/ivco19/brooks/blob/master/LICENSE), y
disponible publicamente en: https://github.com/ivco19/brooks


**Brooks** es un proyecto de **Arcovid19**
Más proyectos del grupo se encuentran en:
[https://ivco19.github.io/](https://ivco19.github.io/)

[Gracias Fred!](http://www.cs.unc.edu/~brooks/)


## Miembros del grupo

-   Juan B Cabral (CIFASIS-UNR, IATE-OAC-UNC).
-   Vanessa Daza (IATE-OAC-UNC, FaMAF-UNC).
-   Diego García Lambas (IATE-OAC-UNC, FaMAF-UNC).
-   Marcelo Lares (IATE-OAC-UNC, FaMAF-UNC).
-   Nadia Luczywo (LIMI-FCEFyN-UNC, IED-FCE-UNC, FCA-IUA-UNDEF)
-   Dante Paz (IATE-OAC-UNC, FaMAF-UNC).
-   Rodrigo Quiroga (INFIQC-CFQ, FCQ-UNC).
-   Bruno Sanchez (Department of Physics, Duke University).
-   Federico Stasyszyn (IATE-OAC, FaMAF-UNC).

## Instituciones

-   [Centro Franco Argentino de Ciencias de la Información y de Sistemas (CIFASIS-UNR)](https://www.cifasis-conicet.gov.ar/)
-   [Instituto de Astronomía Teórica y Experimental (IATE-OAC-UNC)](http://iate.oac.uncor.edu/)
-   [Facultad de Matemática Astronomía Física y Computación (FaMAF-UNC)](https://www.famaf.unc.edu.ar/)
-   [Laboratorio de Ingeniería y Mantenimiento Industrial
    (LIMI-FCEFyN-UNC)](https://fcefyn.unc.edu.ar/facultad/secretarias/extension/prosecretaria-de-vinculacion-tecnologica/centro-de-transferencia-y-servicios/centro-de-vinculacion-del-centro-de-asesoramiento-matematico-a-procesos-organizacionales/)
-   [Instituto De Estadística Y Demografía - Facultad de Ciencias Económicas (IED-FCE-UNC)](http://www.eco.unc.edu.ar/instituto-de-estadistica-y-demografia)
-   [Department of Physics, Duke University](https://phy.duke.edu/)
-   [Facultad de Ciencias de la Administración (FCA-IUA-UNDEF)](https://www.iua.edu.ar/)
-   [Instituto de Investigaciones en Físico-Química de Córdoba (INFIQC-CONICET)](http://infiqc-fcq.psi.unc.edu.ar/)


## Contacto

[jbcabral@unc.edu.ar](jbcabral@unc.edu.ar)


----

## Instalación

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
$ cd site
$ python manage.py check
$ python manage.py migrate
```

- Y por ultimo creamos un usuario y activamos el servidor

```bash
$ python manage.py createsuperuser
...
$ python manage.py runserver
```

Por defecto la definición de modelos es la presente en `site/models.yaml`
