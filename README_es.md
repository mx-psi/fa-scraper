# filmAffinity a Letterboxd

(_[English version](README.md)_)

Genera un fichero CSV compatible con el importador de Letterboxd a partir de los
datos de un usuario de FilmAffinity dada su id.

_Este programa es exclusivamente para uso personal; por favor, asegúrate de que
la persona de la que obtienes los datos da su consentimiento de antemano y
comprueba qué regulaciones de privacidad y protección de datos podrían aplicarse
antes de utilizar el programa para obtener los datos de terceros._

## Instalación

### Con `pip`

Puedes instalarlo usando `pip` ([Python 3.5+](https://www.python.org/)):

```sh
pip install fa-scrapper
```

### Con Docker.

Necesitas instalar Docker. Una vez instalado, ejecuta:

```sh
docker build -t fa-image https://github.com/mx-psi/fa-scrapper.git#master
docker run --name fa-container fa-image fa-scrapper id
docker cp fa-container:/*.csv .
docker rm fa-container`
```

## Obtener IDs

Para conseguir tus datos de FilmAffinity necesitas saber cuál es tu ID de
FilmAffinity. Hay IDs diferentes para tus valoraciones de usuario y tus listas.

### Cómo conseguir tu ID personal

Ve a tu página de perfil y copia el campo `user_id` de la URL:

`filmaffinity.com/es/userratings.php?user_id=`**XXXXXX**

### Cómo conseguir una ID de lista

Ve a la página de listas (en el menú de la izquierda) y accede a la lista que
quieras (necesita ser pública).

Copia el campo `field_id` de la URL:

`filmaffinity.com/es/mylist.php?list_id=`**XXXXXX**

## Opciones

- `--list LIST` fija la ID de la lista pública que quieres exportar a `LIST`
- `--csv FILE` fija el archivo CSV para exportar a `FILE`
- `--lang LANG` fija el idioma a `LANG`. El importador de Letterboxd funciona
  mejor en inglés (la opción por defecto)

## Resolución de problemas

- `Could not set locale`: El script intenta adivinar tu
  [locale](<https://en.wikipedia.org/wiki/Locale_(computer_software)>) en tu
  sistema operativo. Si no lo consigue debes indicarlo tú. En Linux puedes
  conseguir los locale disponibles ejecutando `locale -a`.
