// Utilidades globales
// Función para normalizar horas a formato 'HH:MM'
function normalizarHora(hora) {
    try {
        if (hora === undefined || hora === null) return '';
        const str = String(hora).trim();

        // Si viene como 'HH:MM' o 'HH:MM:SS', recortar a HH:MM
        const match = str.match(/^\d{2}:\d{2}(:\d{2})?$/);
        if (match) {
            return str.slice(0, 5);
        }

        // Intentar parsear con Date y extraer HH:MM en hora local
        const d = new Date(str);
        if (!isNaN(d.getTime())) {
            const hh = String(d.getHours()).padStart(2, '0');
            const mm = String(d.getMinutes()).padStart(2, '0');
            return `${hh}:${mm}`;
        }

        // Si no se puede parsear, retornar vacío
        return '';
    } catch (e) {
        return '';
    }
}

// Exponer en el ámbito global
window.normalizarHora = normalizarHora;