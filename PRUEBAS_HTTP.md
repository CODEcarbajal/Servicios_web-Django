# Evidencias de pruebas HTTP — Lab08

Servidor: `python3 manage.py runserver 127.0.0.1:8080`
Cliente externo: `curl` con cuerpo en `Content-Type: application/json`.

## blog_app (recursos del enrutador)

| Operación | Método y dirección | Código | Respuesta |
|---|---|---|---|
| Listar artículos | GET /api/articles/?page=1 | 200 | JSON paginado con `count`, `next`, `previous`, `results` |
| Detalle artículo | GET /api/articles/72/ | 200 | JSON completo incluida lista `comments` anidada |
| Crear artículo | POST /api/articles/ | 201 | JSON del artículo creado con `id` asignado (73) |
| Modificar parcial | PATCH /api/articles/73/ | 200 | JSON con el campo `title` actualizado |
| Eliminar artículo | DELETE /api/articles/73/ | 204 | Sin cuerpo |
| Listar categorías | GET /api/categories/ | 200 | JSON paginado |
| Detalle categoría (por slug) | GET /api/categories/django/ | 200 | JSON de la categoría |
| Crear comentario | POST /api/comments/ | 201 | JSON del comentario creado con `id` |
| Modificar parcial comentario | PATCH /api/comments/{id}/ | 200 | JSON con `is_approved=false` |
| Eliminar comentario | DELETE /api/comments/{id}/ | 204 | Sin cuerpo |
| Raíz de la API navegable | GET /api/ | 200 | Índice con enlaces a los 3 recursos |

## Comprobación de coincidencia

Las respuestas obtenidas con `curl` coinciden con las de la API navegable
(`/api/` en el navegador): mismo cuerpo JSON y mismo código de estado en las
cinco operaciones de los tres recursos.

## Errores provocados a propósito (POST /api/articles/)

| Error | Cuerpo enviado | Código | Mensaje devuelto |
|---|---|---|---|
| Campo obligatorio ausente | sin `title` | 400 | `{"title":["This field is required."]}` |
| Tipo incorrecto | `"author":"abc"` | 400 | `{"author":["Incorrect type. Expected pk value, received str."]}` |
| Validación propia (publicado sin categoría) | `is_published:true` sin `category` | 400 | `{"non_field_errors":["Un artículo publicado debe tener exactamente una categoría asignada."]}` |

## Filtrado, búsqueda y paginación

| Prueba | Dirección | Resultado |
|---|---|---|
| Filtrado por categoría (examen) | GET /api/articles/?category=django | `count: 4`, todos con `category: 36` |
| Búsqueda por texto | GET /api/articles/?search=testing | `count: 1`, "Testing en Django" |
| Página 1 de resultados | GET /api/articles/ | `count: 8`, 5 resultados, `next` apunta a `?page=2`, `previous: null` |
| Página 2 de resultados | GET /api/articles/?page=2 | 3 resultados, `next: null`, `previous` apunta a la raíz |
