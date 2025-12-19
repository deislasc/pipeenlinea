# 🎨 Sistema de Diseño - PipeEnLinea v2.0

## 📋 Tabla de Contenidos
1. [Introducción](#introducción)
2. [Paleta de Colores](#paleta-de-colores)
3. [Tipografía](#tipografía)
4. [Componentes](#componentes)
5. [Layout](#layout)
6. [Guía de Uso](#guía-de-uso)
7. [Ejemplos](#ejemplos)

---

## 🎯 Introducción

Sistema de diseño moderno y profesional para la aplicación de gestión de créditos **PipeEnLinea**.

### Características

✨ **Diseño Moderno**
- Paleta de colores profesional para Fintech
- Tipografía limpia con fuente Inter
- Componentes con sombras y bordes redondeados
- Animaciones suaves

🎨 **Framework Híbrido**
- **Bootstrap 5.3** - Grid system y componentes
- **CSS Custom Properties** - Variables CSS personalizadas
- **Bootstrap Icons** - Iconografía moderna
- **Chart.js 4.x** - Gráficas interactivas

📱 **Responsive Design**
- Mobile-first approach
- Breakpoints: 768px (tablet), 1024px (desktop)
- Sidebar colapsable
- Navegación optimizada para móvil

♿ **Accesibilidad**
- Contraste WCAG AA compliant
- Navegación por teclado
- ARIA labels
- Semántica HTML5

---

## 🎨 Paleta de Colores

### Colores Principales

```css
--primary-color: #2563eb;      /* Azul profesional */
--primary-dark: #1e40af;        /* Azul oscuro */
--primary-light: #3b82f6;       /* Azul claro */
--primary-lighter: #dbeafe;     /* Azul muy claro */
```

<div style="display:flex;gap:10px;">
  <div style="background:#2563eb;color:white;padding:20px;border-radius:8px;">#2563eb</div>
  <div style="background:#1e40af;color:white;padding:20px;border-radius:8px;">#1e40af</div>
  <div style="background:#3b82f6;color:white;padding:20px;border-radius:8px;">#3b82f6</div>
  <div style="background:#dbeafe;color:#0f172a;padding:20px;border-radius:8px;">#dbeafe</div>
</div>

### Colores Semánticos

| Color | Variable | Uso | Hex |
|-------|----------|-----|-----|
| 🟢 Success | `--secondary-color` | Aprobado, Positivo | `#10b981` |
| 🟠 Warning | `--warning-color` | Pendiente, Alerta | `#f59e0b` |
| 🔴 Danger | `--danger-color` | Rechazado, Error | `#ef4444` |
| 🔵 Info | `--info-color` | Información | `#0ea5e9` |
| 🟡 Accent | `--accent-color` | Destaque | `#f59e0b` |

### Colores de Fondo

```css
--bg-primary: #ffffff;       /* Fondo principal */
--bg-secondary: #f8fafc;     /* Fondo secundario */
--bg-tertiary: #f1f5f9;      /* Fondo terciario */
--bg-dark: #1e293b;          /* Fondo oscuro */
```

### Colores de Texto

```css
--text-primary: #0f172a;     /* Texto principal */
--text-secondary: #475569;   /* Texto secundario */
--text-tertiary: #94a3b8;    /* Texto terciario */
--text-light: #ffffff;       /* Texto claro */
```

---

## 📝 Tipografía

### Fuente Principal

**Inter** - Fuente sans-serif moderna y profesional

```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
```

### Escalas de Tamaño

| Clase | Tamaño | Uso |
|-------|--------|-----|
| `font-size-xs` | 0.75rem (12px) | Badges, labels pequeñas |
| `font-size-sm` | 0.875rem (14px) | Texto secundario |
| `font-size-base` | 1rem (16px) | Texto normal |
| `font-size-lg` | 1.125rem (18px) | Subtítulos |
| `font-size-xl` | 1.25rem (20px) | Títulos de card |
| `font-size-2xl` | 1.5rem (24px) | Títulos de sección |
| `font-size-3xl` | 1.875rem (30px) | Títulos principales |
| `font-size-4xl` | 2.25rem (36px) | Héroes, dashboards |

### Ejemplo de Uso

```html
<h1 class="card-title-modern">Título de Card</h1>
<p class="card-subtitle-modern">Subtítulo descriptivo</p>
```

---

## 🧩 Componentes

### 1. Navbar

Barra de navegación fija con gradiente y efectos de scroll.

```html
<nav class="modern-navbar" id="mainNavbar">
    <button class="navbar-toggle" id="sidebarToggle">
        <div class="hamburger">
            <span></span>
            <span></span>
            <span></span>
        </div>
    </button>

    <a href="/" class="navbar-brand">
        <img src="logo.png" alt="Logo">
        <span>PipeEnLinea</span>
    </a>
</nav>
```

**Características:**
- Altura: 64px
- Gradiente azul (primary → primary-dark)
- Sombra elevada
- Efecto al scroll
- Z-index: 1030

### 2. Sidebar

Menú lateral colapsable con categorías.

```html
<aside class="modern-sidebar" id="mainSidebar">
    <div class="sidebar-menu">
        <div class="menu-section-title">Principal</div>

        <div class="menu-item">
            <a href="/dashboard" class="menu-link active">
                <i class="bi bi-house-door menu-icon"></i>
                <span>Dashboard</span>
            </a>
        </div>
    </div>
</aside>
```

**Características:**
- Ancho: 280px
- Transición suave
- Categorías con títulos
- Iconos Bootstrap Icons
- Efecto hover

### 3. Cards

Contenedor principal de contenido.

```html
<div class="card-modern">
    <div class="card-header-modern">
        <div>
            <h3 class="card-title-modern">Título</h3>
            <p class="card-subtitle-modern">Subtítulo</p>
        </div>
        <div>
            <!-- Acciones -->
        </div>
    </div>

    <!-- Contenido del card -->
</div>
```

**Variantes:**
- `card-modern` - Card estándar
- `stat-card` - Card de estadística
- Con hover effect (levanta y sombra)

### 4. Botones

Botones modernos con iconos y estados.

```html
<!-- Primario -->
<button class="btn-modern btn-primary-modern">
    <i class="bi bi-plus-circle"></i>
    Crear Nuevo
</button>

<!-- Secundario -->
<button class="btn-modern btn-secondary-modern">
    <i class="bi bi-check"></i>
    Aprobar
</button>

<!-- Outline -->
<button class="btn-modern btn-outline-modern">
    <i class="bi bi-arrow-clockwise"></i>
    Actualizar
</button>
```

**Estados:**
- `:hover` - Elevación y sombra
- `:active` - Presionado
- `:disabled` - Deshabilitado (opacity 50%)

### 5. Badges

Etiquetas de estado y categorización.

```html
<span class="badge-modern badge-success">Aprobado</span>
<span class="badge-modern badge-warning">Pendiente</span>
<span class="badge-modern badge-danger">Rechazado</span>
<span class="badge-modern badge-info">En Revisión</span>
<span class="badge-modern badge-primary">Nuevo</span>
```

**Uso:**
- Estados de solicitudes
- Categorías
- Contadores
- Tags

### 6. Tablas

Tablas responsivas y modernas.

```html
<table class="table-modern">
    <thead>
        <tr>
            <th>ID</th>
            <th>Cliente</th>
            <th>Estado</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>#1234</td>
            <td>Juan Pérez</td>
            <td><span class="badge-modern badge-success">Aprobado</span></td>
        </tr>
    </tbody>
</table>
```

**Características:**
- Bordes redondeados
- Hover en filas
- Header con fondo gris claro
- Responsive (scroll horizontal en móvil)

### 7. Forms

Formularios con estilos modernos.

```html
<div class="form-group-modern">
    <label class="form-label-modern">Nombre del Cliente</label>
    <input type="text" class="form-input-modern" placeholder="Ej: Juan Pérez">
</div>

<div class="form-group-modern">
    <label class="form-label-modern">Empresa</label>
    <select class="form-select-modern">
        <option>Seleccionar...</option>
        <option>CAABSA</option>
        <option>MIPYMEX</option>
    </select>
</div>
```

**Características:**
- Focus con border azul
- Shadow al enfocarse
- Placeholders claros
- Validación visual

### 8. Stats Cards

Tarjetas de métricas y estadísticas.

```html
<div class="stats-grid">
    <div class="stat-card" style="border-left-color: var(--primary-color);">
        <div class="stat-label">Total Solicitudes</div>
        <div class="stat-value">1,234</div>
        <div class="stat-trend positive">
            <i class="bi bi-arrow-up"></i>
            <span>12% vs mes anterior</span>
        </div>
    </div>
</div>
```

**Características:**
- Grid responsive (4 columnas → 1 en móvil)
- Borde izquierdo de color
- Tendencias (positivo/negativo)
- Hover effect

---

## 📐 Layout

### Estructura Base

```
┌────────────────────────────────────────┐
│         Navbar (64px fija)             │
├──────────┬─────────────────────────────┤
│          │                             │
│ Sidebar  │      Main Content           │
│ (280px)  │      (flexible)             │
│          │                             │
│          │                             │
└──────────┴─────────────────────────────┘
```

### Grid System

Usa Bootstrap 5 Grid:

```html
<div class="row g-4">
    <div class="col-lg-8">
        <!-- Contenido principal -->
    </div>
    <div class="col-lg-4">
        <!-- Sidebar derecho -->
    </div>
</div>
```

### Espaciado

```css
--spacing-xs: 0.25rem;   /* 4px */
--spacing-sm: 0.5rem;    /* 8px */
--spacing-md: 1rem;      /* 16px */
--spacing-lg: 1.5rem;    /* 24px */
--spacing-xl: 2rem;      /* 32px */
--spacing-2xl: 3rem;     /* 48px */
```

---

## 📚 Guía de Uso

### 1. Crear una Nueva Página

```html
{% extends "base_modern.html" %}

{% block title %}Mi Página - PipeEnLinea{% endblock %}

{% block content_title %}Título de Mi Página{% endblock %}
{% block content_subtitle %}Descripción breve{% endblock %}

{% block header_actions %}
<button class="btn-modern btn-primary-modern">
    <i class="bi bi-plus"></i>
    Nueva Acción
</button>
{% endblock %}

{% block content %}
<div class="card-modern">
    <!-- Tu contenido aquí -->
</div>
{% endblock %}
```

### 2. Usar Variables CSS

```css
.mi-componente {
    background: var(--bg-primary);
    color: var(--text-primary);
    padding: var(--spacing-lg);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-md);
}
```

### 3. Agregar Animaciones

```html
<div class="fade-in">
    <!-- Contenido con animación de entrada -->
</div>

<div class="slide-in">
    <!-- Contenido con slide desde izquierda -->
</div>
```

### 4. Mostrar Notificaciones

```javascript
// Toast de éxito
showToast('Solicitud guardada correctamente', 'success');

// Toast de error
showToast('Error al procesar solicitud', 'danger');

// Toast de info
showToast('Nuevo mensaje recibido', 'info');
```

### 5. Formatear Datos

```javascript
// Formatear moneda
const montoFormateado = formatCurrency(50000);
// Resultado: $50,000.00

// Formatear fecha
const fechaFormateada = formatDate('2024-12-19');
// Resultado: 19 de diciembre de 2024

// Formatear fecha y hora
const fechaHoraFormateada = formatDateTime('2024-12-19T10:30:00');
// Resultado: 19 de diciembre de 2024, 10:30
```

---

## 💡 Ejemplos

### Ejemplo 1: Dashboard con Stats

```html
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-label">Ingresos del Mes</div>
        <div class="stat-value">$1.5M</div>
        <div class="stat-trend positive">
            <i class="bi bi-arrow-up"></i>
            <span>+15%</span>
        </div>
    </div>
</div>
```

### Ejemplo 2: Tabla de Solicitudes

```html
<div class="card-modern">
    <div class="card-header-modern">
        <h3 class="card-title-modern">Solicitudes</h3>
    </div>

    <table class="table-modern">
        <thead>
            <tr>
                <th>ID</th>
                <th>Cliente</th>
                <th>Monto</th>
                <th>Estado</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>#1234</td>
                <td>Juan Pérez</td>
                <td>$50,000</td>
                <td><span class="badge-modern badge-success">Aprobado</span></td>
            </tr>
        </tbody>
    </table>
</div>
```

### Ejemplo 3: Formulario de Solicitud

```html
<div class="card-modern">
    <div class="card-header-modern">
        <h3 class="card-title-modern">Nueva Solicitud</h3>
    </div>

    <form>
        <div class="form-group-modern">
            <label class="form-label-modern">Nombre Completo</label>
            <input type="text" class="form-input-modern" required>
        </div>

        <div class="form-group-modern">
            <label class="form-label-modern">Monto Solicitado</label>
            <input type="number" class="form-input-modern" required>
        </div>

        <button type="submit" class="btn-modern btn-primary-modern">
            <i class="bi bi-check-circle"></i>
            Enviar Solicitud
        </button>
    </form>
</div>
```

---

## 🎯 Best Practices

### ✅ DO (Hacer)

- Usar variables CSS para colores y espaciado
- Mantener consistencia en padding y márgenes
- Usar iconos Bootstrap Icons
- Aplicar transiciones suaves
- Usar grid responsive
- Agregar tooltips y ayudas visuales
- Validar formularios
- Mostrar feedback al usuario

### ❌ DON'T (No Hacer)

- Hardcodear colores en CSS inline
- Mezclar diferentes sistemas de spacing
- Usar fuentes que no sean Inter
- Crear componentes sin considerar responsive
- Ignorar la accesibilidad
- Olvidar los estados hover/focus/active

---

## 🔄 Migración desde UI Antigua

### Paso 1: Cambiar Base Template

```html
<!-- Antiguo -->
{% extends "base.html" %}

<!-- Nuevo -->
{% extends "base_modern.html" %}
```

### Paso 2: Actualizar Clases CSS

| Antiguo | Nuevo |
|---------|-------|
| `.panviewNavBar` | `.modern-navbar` |
| `.toogleMenu` | `.modern-sidebar` |
| `.menuItem` | `.menu-link` |
| `.container` | `.main-content` |

### Paso 3: Actualizar Componentes

- Cards: Usar `.card-modern` en lugar de divs custom
- Botones: Usar `.btn-modern .btn-primary-modern`
- Tablas: Usar `.table-modern`
- Formularios: Usar `.form-input-modern`

---

## 📞 Soporte

Para más información o problemas:
- Ver `dashboard_modern.html` para ejemplos completos
- Revisar `modern-theme.css` para todas las clases disponibles
- Consultar documentación de Bootstrap 5: https://getbootstrap.com/docs/5.3/

---

**Versión:** 2.0
**Última actualización:** 2024-12-19
**Autor:** PipeEnLinea Development Team
