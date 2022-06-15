Autenticación en Odoo via ID Uruguay
--------------------------

Adiciona la posibilidad de autenticarse en Odoo haciendo uso de un usuario ID Uruguay.

* Comunicación con ID Uruguay para la gestión de usuarios
* Enlace de autenticación ID Uruguay con la seguridad convencional de Odoo

Cuando se accede por primera ocasión al sistema de Odoo con su usuario de ID Uruguay
el sistema automáticamente crea un nuevo usuario tomando como seguridad por defecto la 
establecida para el usuario "Default User" tal y como lo propone el funcionamiento
estándar de Odoo.

Configuración inicial
--------------------------
El addon automáticamente crea un OAuth Provider que se ubica en la ruta:
Ajustes/Usuarios y compañías/Proveedores OAuth con el nombre de "Id Uruguay".
Esta configuración por defecto debe ser ajustada para que cumpla con los parámetros
propios de la instalación de Odoo.
Ej:

* URL Autenticación: URL contra la que Odoo va a realizar el login
* URL de validación: URL a la que Odoo va a validar el token
* URL de los datos: URL a la que Odoo va a solicitar los datos del usuario
* URL de redirección: URL a la que ID Uruguay va a responder. Normalmente es una URL del
sistema Odoo.
  
<b>NOTA</b>
Estos parámetros ya vienen con una propuesta y se recomienda solamente cambiar las partes
donde explícitamente el sistema recomienda. Ejemplo:
https://<b>URL_Base_Id_UY</b>/oidc/v1/authorize
