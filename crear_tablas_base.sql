-- =====================================================
-- CREACIÓN DE TABLAS BASE PARA SISTEMA DE ESTADOS
-- =====================================================

USE synapsis;

-- Crear tabla de roles
CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Crear tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    usuario VARCHAR(50) UNIQUE,
    password VARCHAR(255),
    rol_id INT,
    activo BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rol_id) REFERENCES roles(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Crear tabla de clientes
CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    documento VARCHAR(20),
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Crear tabla principal de devoluciones_dotacion
CREATE TABLE IF NOT EXISTS devoluciones_dotacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tecnico_id INT NOT NULL,
    cliente_id INT NOT NULL,
    fecha_devolucion DATE NOT NULL,
    motivo TEXT NOT NULL,
    observaciones TEXT,
    estado ENUM('REGISTRADA', 'PROCESANDO', 'COMPLETADA', 'CANCELADA') DEFAULT 'REGISTRADA',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (tecnico_id) REFERENCES usuarios(id),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    INDEX idx_estado (estado),
    INDEX idx_fecha (fecha_devolucion),
    INDEX idx_tecnico (tecnico_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar roles iniciales
INSERT IGNORE INTO roles (id, nombre, descripcion) VALUES
(1, 'Administrador', 'Administrador del sistema con acceso completo'),
(2, 'Usuario', 'Usuario básico del sistema'),
(3, 'Técnico Logística', 'Técnico encargado de registrar devoluciones'),
(4, 'Supervisor Logística', 'Supervisor que aprueba/rechaza devoluciones'),
(5, 'Administrador Logística', 'Administrador con control total sobre estados');

-- Insertar usuarios de prueba
INSERT IGNORE INTO usuarios (id, nombre, email, usuario, password, rol_id) VALUES
(1, 'Administrador Sistema', 'admin@sistema.com', 'admin', '$2b$12$hash_password', 1),
(2, 'Técnico Prueba', 'tecnico@logistica.com', 'tecnico1', '$2b$12$hash_password', 3),
(3, 'Supervisor Prueba', 'supervisor@logistica.com', 'supervisor1', '$2b$12$hash_password', 4),
(4, 'Admin Logística', 'adminlog@logistica.com', 'adminlog', '$2b$12$hash_password', 5);

-- Insertar clientes de prueba
INSERT IGNORE INTO clientes (id, nombre, documento, telefono) VALUES
(1, 'Cliente Prueba 1', '12345678', '3001234567'),
(2, 'Cliente Prueba 2', '87654321', '3007654321');

SELECT 'Tablas base creadas exitosamente' as resultado;