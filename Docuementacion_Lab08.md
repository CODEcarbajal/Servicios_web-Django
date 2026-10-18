# Laboratorio 08 — API REST con Django REST Framework (Docuementacion_Lab08.md)

Proyecto: `ORM_IA` (blog con Django 6.1.1 + djangorestframework 3.18.3).

Adaptación del laboratorio de cuestionarios a este proyecto: el examen es un
**artículo**, la pregunta es una **categoría** y la opción es un **comentario**.
Los tres recursos expuestos son `articles`, `categories` y `comments`.

---

## 1. Instalación y aplicación

- Dependencia añadida en `requirements.txt`: `djangorestframework==3.18.3`.
- Declarado en `INSTALLED_APPS` (`blog/settings.py`) junto con la app del blog:

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'blog_app',
]
```

## 2. Configuración de `REST_FRAMEWORK` en `settings.py`

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 5,
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}
```

- Paginación por defecto: `PageNumberPagination` con 5 elementos por página.
- Permiso de partida: `AllowAny` (lectura y escritura abiertas en desarrollo).

## 3. Serializadores (`blog_app/serializers.py`)

| Serializador | Modelo | Campos expuestos | Solo lectura |
|---|---|---|---|
| `CategorySerializer` | `Category` | `id`, `name`, `slug`, `description`, `created_at` | `id`, `created_at` |
| `CommentSerializer` | `Comment` | `id`, `article`, `author_name`, `author_email`, `content`, `created_at`, `is_approved` | `id`, `created_at` |
| `ArticleSerializer` | `Article` | `id`, `title`, `slug`, `content`, `author`, `category`, `tags`, `published_at`, `updated_at`, `is_published`, `comments` | `id`, `published_at`, `updated_at` |

Los tres derivan de `ModelSerializer`: los campos del modelo definen la entrada
y la validación base (obligatorios, longitud, formato email/slug).

## 4. Cómo viajan las relaciones

| Relación | Decisión | Motivo |
|---|---|---|
| Comentarios → Artículo | **Anidados** dentro de `ArticleSerializer` (`comments = CommentSerializer(many=True, read_only=True)`) | El detalle de un artículo se lee con sus comentarios en una sola respuesta; solo lectura porque cada comentario se crea/modifica por su propio recurso |
| Artículo → Categoría | **Referida por identificador** (`PrimaryKeyRelatedField`, `allow_null=True`) | La categoría se administra en `/api/categories/`; el artículo solo apunta a su `id` |
| Categoría → Artículo | No viaja en el JSON | Se consultan los artículos filtrando: `/api/articles/?category=<slug>` |

Ejemplo de respuesta de `GET /api/articles/72/`:

```json
{
  "id": 72,
  "title": "Testing en Django",
  "category": 39,
  "is_published": true,
  "comments": [
    {"id": 1, "author_name": "Eva", "content": "...", "is_approved": true}
  ]
}
```

## 5. Validación propia

En `ArticleSerializer.validate()`:

```python
def validate(self, attrs):
    is_published = attrs.get('is_published', getattr(self.instance, 'is_published', True))
    category = attrs.get('category', getattr(self.instance, 'category', None))
    if is_published and category is None:
        raise serializers.ValidationError(
            'Un artículo publicado debe tener exactamente una categoría asignada.'
        )
    return attrs
```

Análogo del enunciado (pregunta con exactamente una opción correcta): no se
acepta un artículo publicado sin su categoría. Comprobado en la prueba de
errores (apartado 9).

## 6. Vistas y enrutador

`blog_app/views.py`:

| ViewSet | Queryset | Detalles |
|---|---|---|
| `CategoryViewSet` | `Category.objects.all()` | Detalle por `slug` (`lookup_field = 'slug'`) |
| `ArticleViewSet` | `Article.objects.prefetch_related('comments', 'tags')` | `SearchFilter` + filtro `?category=` |
| `CommentViewSet` | `Comment.objects.select_related('article')` | CRUD completo |

`blog_app/urls.py`:

```python
router = routers.DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('articles', ArticleViewSet)
router.register('comments', CommentViewSet)
urlpatterns = router.urls
```

Rutas raíz en `blog/urls.py` (equivalente a `config/urls.py`):

```python
path('api/', include('blog_app.urls')),
```

Direcciones resultantes: `/api/categories/`, `/api/articles/`, `/api/comments/`.

## 7. API navegable (paso 7)

Servidor: `python3 manage.py runserver 127.0.0.1:8080`.
Recorrido desde `GET /api/` en el navegador con códigos anotados:

| Operación | Dirección | Código |
|---|---|---|
| Listar | GET /api/articles/ | 200 |
| Detalle | GET /api/articles/72/ | 200 |
| Crear | POST /api/articles/ | 201 |
| Modificar parcial | PATCH /api/articles/73/ | 200 |
| Eliminar | DELETE /api/articles/73/ | 204 |

## 8. Cliente HTTP externo (paso 8)

Mismas operaciones con `curl` y cabecera `Content-Type: application/json`:

```bash
# Crear
curl -X POST http://127.0.0.1:8080/api/articles/ \
  -H "Content-Type: application/json" \
  -d '{"title":"Artículo de prueba API","slug":"articulo-prueba-api",
       "content":"Contenido creado desde curl.","author":41,"category":36,
       "is_published":true}'
# -> 201, id 73

# Modificar parcial
curl -X PATCH http://127.0.0.1:8080/api/articles/73/ \
  -H "Content-Type: application/json" -d '{"title":"Artículo de prueba API (editado)"}'
# -> 200

# Eliminar
curl -X DELETE http://127.0.0.1:8080/api/articles/73/
# -> 204
```

Resultado: cuerpo JSON y códigos idénticos a los de la API navegable.
Evidencia completa en `PRUEBAS_HTTP.md`.

## 9. Errores provocados a propósito (paso 9)

| Error | Cuerpo enviado | Código | Mensaje devuelto |
|---|---|---|---|
| Campo obligatorio ausente | sin `title` | 400 | `{"title":["This field is required."]}` |
| Tipo incorrecto | `"author":"abc"` | 400 | `{"author":["Incorrect type. Expected pk value, received str."]}` |
| Validación propia | `is_published:true` sin `category` | 400 | `{"non_field_errors":["Un artículo publicado debe tener exactamente una categoría asignada."]}` |

## 10. Filtrado, búsqueda y paginación (paso 10)

- **Filtrado por examen (categoría):** `GET /api/articles/?category=django`
  → `count: 4`, todos con `category: 36`.
- **Búsqueda por texto:** `GET /api/articles/?search=testing` con
  `search_fields = ['title', 'content']` → `count: 1` ("Testing en Django").
- **Paginación:** con 8 artículos y `PAGE_SIZE = 5` hay dos páginas:

| Página | Dirección | Resultados | `next` | `previous` |
|---|---|---|---|---|
| 1 | /api/articles/ | 5 | /api/articles/?page=2 | null |
| 2 | /api/articles/?page=2 | 3 | null | /api/articles/ |

## 11. Tabla de la API (entregable)

| Recurso | Dirección | Método | Cuerpo de ejemplo | Respuesta esperada |
|---|---|---|---|---|
| Categorías | GET /api/categories/ | GET | — | 200: JSON paginado `count/next/previous/results` |
| Categoría | GET /api/categories/django/ | GET | — | 200: `{"id":36,"name":"Django","slug":"django",...}` |
| Crear categoría | POST /api/categories/ | POST | `{"name":"Testing","slug":"testing","description":""}` | 201: JSON con `id` asignado |
| Modificar categoría | PATCH /api/categories/testing/ | PATCH | `{"name":"Testing y calidad"}` | 200: JSON con el campo actualizado |
| Eliminar categoría | DELETE /api/categories/testing/ | DELETE | — | 204: sin cuerpo |
| Artículos | GET /api/articles/ | GET | — | 200: paginado; `?category=slug` filtra, `?search=texto` busca |
| Artículo | GET /api/articles/72/ | GET | — | 200: JSON completo con `comments` anidados |
| Crear artículo | POST /api/articles/ | POST | `{"title":"T","slug":"t","content":"C","author":41,"category":36,"is_published":true}` | 201: JSON con `id` y `comments: []` |
| Modificar artículo | PATCH /api/articles/73/ | PATCH | `{"title":"T editado"}` | 200: JSON actualizado |
| Eliminar artículo | DELETE /api/articles/73/ | DELETE | — | 204: sin cuerpo |
| Errores de validación | POST /api/articles/ | POST | `{"slug":"x","content":"c","author":41}` (sin `title`) | 400: `{"title":["This field is required."]}` |
| Comentarios | GET /api/comments/ | GET | — | 200: paginado |
| Comentario | GET /api/comments/{id}/ | GET | — | 200: JSON con `article` por id |
| Crear comentario | POST /api/comments/ | POST | `{"article":72,"author_name":"Eva","author_email":"eva@test.com","content":"Hola","is_approved":true}` | 201: JSON con `id` y `created_at` |
| Modificar comentario | PATCH /api/comments/{id}/ | PATCH | `{"is_approved":false}` | 200: JSON actualizado |
| Eliminar comentario | DELETE /api/comments/{id}/ | DELETE | — | 204: sin cuerpo |

## 12. Repositorio y entrega

- Proyecto completo subido al repositorio git con 8 commits en español
  (ver `git log`).
- Entregable: este archivo `Docuementacion_Lab08.md` + `PRUEBAS_HTTP.md`
  con las evidencias de las pruebas HTTP.

### Commits del laboratorio

| # | Título |
|---|---|
| 1 | Instalar Django REST Framework y declararlo en INSTALLED_APPS con la app del blog |
| 2 | Configurar bloque REST_FRAMEWORK: paginación por defecto y permisos iniciales |
| 3 | Añadir serializadores de artículo, categoría y comentario con sus relaciones |
| 4 | Validar en el serializador que un artículo publicado tenga su categoría asignada |
| 5 | Exponer los tres recursos con conjuntos de vistas y enrutador en /api/ |
| 6 | Anotar los códigos de estado de las cinco operaciones probadas por HTTP |
| 7 | Probar errores, filtrado por categoría, búsqueda y paginación de dos páginas |
| 8 | Documentar el laboratorio con la tabla completa de la API |
