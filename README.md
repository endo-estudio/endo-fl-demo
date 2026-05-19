# DEMO Find Landing

Visor territorial interactivo basado en datos KMZ convertidos a GeoJSON.

## Estructura del proyecto

```
DEMO Find Landing/
├── assets/
│   └── geojson/
│       └── capas-base.geojson   # Capas territoriales convertidas del KMZ
├── data/
│   ├── capas.json               # Metadatos y configuración de capas
│   └── lotes.json               # Base de datos de lotes (editable)
├── Brief_Territorial__endo_V4.html
├── conversion-log.txt
└── convert_kmz.py
```

## Cómo actualizar el GeoJSON desde un nuevo KMZ

1. Reemplazar el archivo fuente:
   ```
   KMZ Base Completo.kmz  →  nueva versión
   ```

2. Ejecutar la conversión:
   ```bash
   python3 convert_kmz.py
   ```

3. El archivo actualizado se guarda en `assets/geojson/capas-base.geojson`  
   y el log en `conversion-log.txt`.

4. Hacer commit:
   ```bash
   git add assets/geojson/capas-base.geojson conversion-log.txt
   git commit -m "Update: nuevo KMZ a GeoJSON"
   ```

## Cómo agregar o editar lotes en `data/lotes.json`

Cada lote sigue esta estructura:

```json
{
  "id": "LOTE-001",
  "nombre": "Nombre del lote",
  "zona": "ZONAS",
  "capa_ref": "zonas",
  "estado": "disponible",
  "superficie_m2": 500,
  "precio_usd": 75000,
  "precio_m2_usd": 150,
  "coordenadas": { "lat": -34.123, "lng": -58.456 },
  "propiedades": {
    "descripcion": "Descripción del lote",
    "acceso": "Calle principal",
    "servicios": ["agua", "luz", "gas"],
    "observaciones": ""
  }
}
```

**Estados posibles:** `disponible` · `reservado` · `vendido` · `consultar`

## Cómo actualizar `data/capas.json`

Editar los campos de cada capa para ajustar visualización:

| Campo | Descripción |
|-------|-------------|
| `visible` | `true` / `false` — mostrar u ocultar la capa |
| `color` | Color hex de la capa en el mapa |
| `opacidad` | Valor entre `0.0` y `1.0` |
| `descripcion` | Texto informativo de la capa |

## Capas disponibles

| ID | Nombre | Geometría | Features |
|----|--------|-----------|---------|
| `cou` | COU | Polygon, LineString | 26 |
| `zonas` | ZONAS | Polygon | 6 |
| `zona_completamiento` | Zona de completamiento | Polygon | 2 |
| `vias` | VIAS | LineString | 10 |
| `precio_zonas` | PRECIO POR ZONAS | Point | 6 |

---

Conversión realizada con `convert_kmz.py` · Fuente: `KMZ Base Completo.kmz`
