# Brooks

Sistema de soporte para el análisis de datos
de la pandemia de COVID-19 en la provincia de
Córdoba.

Este proyecto esta distribuido con
licencia [BSD-3](https://github.com/ivco19/brooks/blob/master/LICENSE), y
disponible publicamente en: https://github.com/ivco19/brooks

El desarrollo e investigación fue
llevado adelante por

- Juan B Cabral (CIFASIS-UNR, IATE-OAC-UNC).
- Vanessa Daza (IATE-OAC-UNC, FaMAF-UNC).
- Mariano Dominguez (IATE-OAC-UNC, FaMAF-UNC).
- Marcelo Lares (IATE-OAC-UNC, FaMAF-UNC).
- Nadia Luczywo (LIMI-FCEFyN-UNC, IED-FCE-UNC, FCA-IUA-UNDEF)
- Dante Paz (IATE-OAC-UNC, FaMAF-UNC).
- Rodrigo Quiroga (INFIQC-CFQ, FCQ-UNC).
- Martín de los Ríos (ICTP-SAIFR).
- Bruno Sanchez (Department of Physics, Duke University).
- Federico Stasyszyn (IATE-OAC, FaMAF-UNC).

**Afiliaciones:**

- [Centro Franco Argentino de Ciencias de la Información y de Sistemas (CIFASIS-UNR)](https://www.cifasis-conicet.gov.ar/)
- [Instituto de Astronomía Téorico y Experimental (IATE-OAC-UNC)](http://iate.oac.uncor.edu/)
- [Facultad de Matemática Física y Computación (FaMAF-UNC)](https://www.famaf.unc.edu.ar/)
- [Laboratorio de Ingeniería y Mantenimiento Industrial (LIMI-FCEFyN-UNC)](https://fcefyn.unc.edu.ar/facultad/secretarias/investigacion-y-posgrado/-investigacion/laboratorio-de-ingenieria-y-mantenimiento-industrial/)
- [Instituto De Estadística Y Demografía - Facultad de Ciencias Económicas (IED-FCE-UNC)](http://www.eco.unc.edu.ar/instituto-de-estadistica-y-demografia)
- [Department of Physics, Duke University](https://phy.duke.edu/)
- [Facultad de Ciencias de la Administación (FCA-IUA-UNDEF)](https://www.iua.edu.ar/)
- [Instituto de Investigaciones en Físico-Química de Córdoba (INFIQC-CONICET)](http://infiqc-fcq.psi.unc.edu.ar/)
- [ICTP South American Institute for Fundamental Research (ICTP-SAIFR)](ICTP-SAIFR)


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