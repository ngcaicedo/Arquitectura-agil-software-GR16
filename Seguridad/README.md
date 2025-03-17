# Experimento 2

## Integrantes del Proyecto

| Nombre            | Rol              |Correo                                |
|-------------------|------------------|--------------------------------------|
| Diego Santamaria  | Product Owner    |jd.santamariab1@uniandes.edu.co       |
| John Casallas     | Scrum Master     |j.casallasp@uniandes.edu.co           |
| Nicolas Caicedo   | Desarrollador    |ng.caicedo@uniandes.edu.co            |
| Jose Rodriguez    | Desarrollador    |jd.rodriguezg1234567@uniandes.edu.co  |

## Pasos para ejecutar el aplicativo
1. Clone el repositorio en su equipo local. Como requisitos debe tener instalado python y docker
2. Ejecute el comando ```docker compose up --build``` para caso de linux y ```docker-compose up --build``` en windows
3. Ejecute el script ```$ python Seguridad/scripts/check_venta.py``` ubicándose en la raiz del proyecto
4. Valide el resultado en los archivos generados en la ruta ```Seguridad/scripts/``` con nombres ```valida_acceso.csv``` y ```valida_modificacion_venta.csv```