EXAM SIMULATOR
--------------

Herramienta de escritorio para crear y practicar exámenes de selección múltiple.
Funciona en Windows, macOS y Linux sin conexión a internet.

---

CONTENIDO DEL PAQUETE
---------------------

``
ExamSimulator/
├── exam_simulator.exe      ← El simulador de exámenes
├── exam_generator.exe      ← El generador de preguntas
├── questions_bank/         ← Aquí van tus archivos de preguntas (.json)
│   └── informatica_basico.json
└── resources/
    └── icon.png
`

---

REQUISITOS
----------

Ninguno. Solo descomprime el .zip y haz doble clic.

---

EXAM SIMULATOR
--------------

El simulador es el programa principal. Te permite hacer exámenes a partir de los archivos
de preguntas que tengas en la carpeta questions_bank.

CÓMO USARLO
-----------

1. Abre exam_simulator.exe
2. Verás el Banco de preguntas con los archivos disponibles
3. Selecciona el que quieras o pulsa Cargar todo para combinarlos
4. Configura el examen:
   - Número de preguntas
   - Mezclar preguntas (sí/no)
   - Mezclar orden de opciones (sí/no)
5. Pulsa Comenzar
6. Responde cada pregunta — puedes saltar con S o salir con Q
7. Al terminar verás tu puntuación con la dona animada
8. Pulsa Ver revisión para repasar las respuestas

BOTONES DEL BANCO
-----------------

   Botón    Función   

   📂 Abrir banco    Abre la carpeta questions_bank en el explorador   
   ⬆ Importar JSON    Carga un archivo .json desde cualquier ubicación   
   🔄 Refresh    Recarga el listado sin reiniciar la app   
   ✏ Generar examen    Abre el Generador de preguntas   

---

EXAM GENERATOR
--------------

El generador te permite crear tus propios archivos de preguntas sin tocar código.

CÓMO CREAR UN EXAMEN
--------------------

1. Abre exam_generator.exe
2. Escribe el título y la descripción del examen
3. Pulsa Empezar
4. Para cada pregunta rellena:
   - Categoría (opcional, por defecto "default")
   - Pregunta
   - Respuestas (mínimo 2, máximo 6) — marca con el botón circular cuál es la correcta
   - Explicación de la respuesta correcta
5. Pulsa Añadir para guardar la pregunta y crear otra
6. Cuando termines pulsa Finalizar para ir a la revisión
7. En la revisión puedes editar o borrar preguntas
8. Pulsa Exportar para guardar el archivo .json

GENERAR PREGUNTAS CON IA
------------------------

Si quieres generar preguntas usando ChatGPT, Claude, Gemini u otra IA:

1. Pulsa 🤖 Generar con IA en la pantalla de inicio
2. Copia el prompt que aparece
3. Pégalo en tu IA favorita y cuéntale el tema
4. La IA te devolverá un bloque de código — cópialo todo
5. Abre el Bloc de notas, pega el texto y guárdalo con extensión .json
   (por ejemplo: mi_examen.json)
6. Guárdalo dentro de la carpeta questions_bank
7. Vuelve al Simulador y pulsa 🔄 Refresh

IMPORTAR UN JSON EXISTENTE
--------------------------

Si ya tienes un archivo .json y quieres editarlo:

1. Pulsa 📂 Importar JSON en la pantalla de inicio del Generador
2. Navega hasta el archivo y ábrelo
3. Se cargará directamente en la pantalla de revisión para editar

---

FORMATO DEL ARCHIVO DE PREGUNTAS
--------------------------------

Si quieres crear o editar los archivos .json manualmente, este es el formato:

`json
{
  "title": "Título del examen",
  "description": "Descripción breve",
  "questions": [
    {
      "question": "Texto de la pregunta",
      "options": {
        "A": "Primera opción",
        "B": "Segunda opción",
        "C": "Tercera opción",
        "D": "Cuarta opción"
      },
      "correct": "A",
      "explanation": "Por qué esta opción es correcta",
      "category": "Tema"
    }
  ]
}
`

Campos obligatorios: question, options, correct
Campos opcionales: explanation, category
Número de opciones: mínimo 2, máximo las que necesites

---

PREGUNTAS FRECUENTES
--------------------

¿Dónde guardo mis archivos de preguntas?
Dentro de la carpeta questions_bank, junto al ejecutable. Puedes organizarlos en subcarpetas por tema y el simulador las detectará automáticamente.

¿Puedo mezclar preguntas de varios archivos?
Sí. Selecciona una carpeta en el banco para cargar todos los archivos que contiene, o pulsa Cargar todo para combinar absolutamente todos.

¿Se guardan mis resultados?
No, los resultados son solo de la sesión actual. Al cerrar el programa no se almacena nada.

El archivo que me dio la IA no carga correctamente
Asegúrate de que el archivo esté guardado con extensión .json y que el texto empiece por { y termine por }. Si la IA incluyó texto antes o después del bloque de código, bórralo.

---

ESTRUCTURA DE CARPETAS RECOMENDADA
----------------------------------

`
questions_bank/
├── informatica/
│   ├── redes.json
│   └── hardware.json
├── ciberseguridad/
│   ├── pentesting.json
│   └── active_directory.json
└── programacion.json
``

---

*Exam Simulator — Hecho con PyQt6*
