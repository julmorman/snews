# S-NEWS: Proyecto de Noticias para Colegio

## Prompt Original
Hola quiero armar un proyecto para un colegio donde en pantallas en espacios comunes se va a presentar un resumen de las noticias de la semana, noticias del mundo en diferentes categorias: geopolitica, nacional, ciencias, sustentabilidad, la audiencia son adolescentes y esto la idea es que sea un video en un loop que dure no mas de 5 min con diferentes pantallas (la cantidad a definir, dependera de los segundos que se muestren) titulos, imagenes, un poco de texto y un QR que con sus celulares puedan escanear para saber mas y que te lleve a un sitio hosteado donde haya mas info. Mi idea inicial es que un proceso automatico elija potenciales noticias (esto es semanal) y esa lista pre curada, una persona (yo) la termine de definir, luego un proceso automatizado resuma esas noticias seleccionadas y me ayude a armar el maquetado final para tener esas pantallas listas y armar el video, tambien el html o sitio con mas info adonde apunte el QR de cada pantalla. El video lo puedo yo pasar a traves de un pendrive a una computadora del colegio, si necesito el sitio con la info extra de los QRs, no tengo presupuesto inicialmente asi que se debe apuntar a servicios gratuitos. Armame un plan, dividilo en fases, resumimelo aca en pantalla y escribi la version larga del plan en un .md en este mismo directorio. Inclui este prompt al inicio del file

## Objetivo del Proyecto
Crear un sistema automatizado para la generación de un video informativo semanal y un sitio web de respaldo para un colegio, enfocado en adolescentes, utilizando herramientas gratuitas.

## Fase 1: Extracción y Curaduría (Automatización de Selección)
- **Fuentes:** Utilizar RSS feeds o APIs de noticias gratuitas (ej. NewsAPI - nivel gratuito).
- **Herramienta:** Script en Python para extraer noticias de las categorías: Geopolítica, Nacional, Ciencias, Sustentabilidad.
- **Intervención Humana:** El script generará un archivo (JSON o CSV) con las noticias potenciales. El usuario marcará las seleccionadas para la semana.

## Fase 2: Procesamiento y Transparencia (Fomento al Pensamiento Crítico)
- **Resumen Dual:** Uso de IA para generar un texto "de impacto" para la pantalla (15-20 palabras) y un resumen informativo para la web.
- **Validación Multi-fuente:** El sistema buscará y agrupará enlaces de diferentes medios para una misma noticia, permitiendo a los alumnos contrastar información.
- **Sin QRs en Pantalla:** Se prioriza la estética y el interés visual, eliminando códigos individuales para evitar barreras sociales.

## Fase 3: El "Hub" de Noticias y Generación Visual
- **Sitio Web (Archivo Central):** Uso de **GitHub Pages** para alojar una bitácora semanal. Cada entrada incluirá:
    - El video de la semana (embebido o link).
    - Resumen extendido de cada noticia.
    - Enlaces directos a las múltiples fuentes consultadas.
- **Maquetado de Pantallas:** Generación de diapositivas limpias con: Título, Imagen de fondo (u opaca), mini-resumen.
- **Producción de Video:** Automatización con `MoviePy` para crear un loop de ~5 min, calculando el tiempo de lectura adecuado por slide.

## Fase 4: Flujo Semanal y Mantenimiento
- **Ciclo de Trabajo:**
    1. **Recolección:** El script busca noticias automáticamente.
    2. **Curaduría:** El usuario selecciona las noticias definitivas en un archivo JSON/YAML simple.
    3. **Generación:** El script crea las pantallas, el video y la entrada del blog/web.
    4. **Publicación:** Carga automática a GitHub Pages y copia manual del video al pendrive.
- **Mantenimiento:** El sistema es estático (sin servidor), lo que garantiza estabilidad total sin costos.

## Tecnologías Sugeridas (Stack Gratuito)
- **Lenguaje:** Python.
- **Hosting:** GitHub Pages.
- **Imágenes/Video:** Pillow, MoviePy.
- **QR:** qrcode (librería python).
- **IA:** OpenAI (tier gratis) o integración con LLMs locales.

---
*Este plan es una base técnica para iniciar el desarrollo del sistema S-NEWS.*
