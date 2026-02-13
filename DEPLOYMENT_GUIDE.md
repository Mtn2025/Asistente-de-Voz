# Guía de Despliegue: Resolución de Advertencias en Coolify

Esta guía explica cómo eliminar la advertencia `Build-time environment variable warning: APP_ENV=development` en Coolify.

## El Problema
Coolify inyecta variables de entorno durante la construcción (build) del contenedor Docker por defecto. Si tu variable `APP_ENV` está configurada como `development` (o no está definida y toma ese valor por defecto), algunas herramientas de construcción pueden emitir advertencias o comportarse de manera no optimizada para producción.

## La Solución
Debes configurar explícitamente la variable `APP_ENV` en Coolify para que solo esté disponible en **Tiempo de Ejecución (Runtime)**, o establecerla correctamente para el **Tiempo de Construcción (Build)** si es necesario.

### Pasos en Coolify

1.  Ve a tu **Proyecto** en Coolify.
2.  Selecciona el recurso **Application** (tu servicio `app`).
3.  Ve a la pestaña **Environment Variables**.
4.  Busca la variable `APP_ENV`.
5.  Edítala y asegúrate de que **Build Variable** esté **DESACTIVADO** (unchecked).
    *   Esto asegura que `APP_ENV` solo se inyecte cuando el contenedor se inicia, no cuando se construye.
6.  (Opcional) Si necesitas una variable específica para el build (ej. para optimizar instalaciones), puedes crear una nueva variable explícita llamada `BUILD_APP_ENV` o similar, pero generalmente para Python/FastAPI no es crítico.

### Verificación
Después de cambiar la configuración:
1.  Haz clic en **Redeploy**.
2.  Observa los logs de construcción.
3.  La advertencia `Build-time environment variable warning` debería haber desaparecido o cambiado, y el despliegue debería ser exitoso.

## Notas sobre el Dockerfile
He actualizado el `Dockerfile` para aceptar `ARG APP_ENV`. Esto significa que si decides pasar la variable durante el build, Docker la aceptará silenciosamente y la usará, evitando advertencias de "variable no consumida".
