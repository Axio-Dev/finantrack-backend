## Resumen del proyecto
- FinanTrack nace de la necesidad de contar con una herramienta que me permitiera manejar mis finanzas de una manera más sencilla.
- La aplicaciones que he utilizado hasta ahora no ofrecen, en un mismo lugar, las funcionalidades que necesito para llevar el control de mi dinero. Es por esto que, he decidido desarrollar esta aplicación, esperando que sea de ayuda para todas las personas que se encuentran con esta necesidad de manejar sus finanzas personales sin depender de hojas de cálculo, varias aplicaciones o cálculos mentales.
- Este repo es para el Backend de la aplicación, por lo qué acontinuación veremos las reglas y estilo de código a seguir para esta porción del código

## Reglas del estilo de código
- En este proyecto se está usando Django con su subframework Rest Framework
- Para la construcción de este proyecto, estaremos siguiendo los líneamientos de 'Django Style Guide' por lo qué todo el código deberá seguir los patrones mencionados en la guía ya mencionada
- La estrucutura es un repo de tipo 'Monolito Modular' con el patrón de diseño 'Servce Layer'

## Arquitectura del proyecto

- El backend usa Django y Django REST Framework.
- El repo sigue un monolito modular.
- El patrón principal es Service Layer.
- Las views deben coordinar request/response, permisos y serialización, pero no contener lógica de negocio compleja.
- Los serializers deben validar/transformar datos, no ejecutar flujos de negocio grandes.
- Los servicios encapsulan casos de uso y cambios de estado.
- Las consultas reutilizables o complejas deben vivir en selectors/query helpers cuando aplique.

## Code Review Rules

- Antes de revisar un PR, lee la descripción del PR y úsala como fuente principal para entender objetivo, alcance, decisiones esperadas y criterios de aceptación.
- Si no puedes acceder a la descripción del PR, dilo explícitamente al inicio de la revisión y pide que se pegue el texto o resume la revisión solo con el diff disponible.
- Evalúa si los cambios cumplen con la arquitectura del proyecto: Django + Django REST Framework, monolito modular y Service Layer.
- Mantén la lógica de negocio en servicios; evita mover reglas de negocio a views, serializers, signals o modelos salvo que ya sea un patrón existente.
- Prioriza hallazgos de bugs, regresiones, seguridad, integridad de datos, permisos, transacciones y contratos API. No marques preferencias de estilo si ya las cubre lint/format.