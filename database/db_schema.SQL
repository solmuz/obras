-- Sistema de Gestión de Accesorios de Izaje
-- Database Schema v1.1 — aligned with SQLAlchemy models

-- Users 
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'engineer', 'hse', 'consulta') DEFAULT 'hse' NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by_id INT,
    INDEX idx_username (username),
    INDEX idx_is_deleted (is_deleted)
);

-- Projects 
CREATE TABLE projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,
    description VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by_id INT,

    INDEX idx_name (name),
    INDEX idx_is_active (is_active),
    FOREIGN KEY (created_by_id) REFERENCES users(id)
);


-- Equipment (Accesorios de Izaje) 
CREATE TABLE equipment (
    id INT AUTO_INCREMENT PRIMARY KEY,

    -- Fixed / identifying fields
    code VARCHAR(50) UNIQUE NOT NULL,
    element_type ENUM('eslinga', 'grillete', 'gancho', 'otro') NOT NULL,
    brand VARCHAR(100) NOT NULL,
    empresa ENUM('GEO', 'SBCIMAS', 'PREFA', 'BESSAC') NOT NULL,
    serial VARCHAR(100),
    material VARCHAR(100),
    capacity_ton VARCHAR(200),          -- free text: Vertical / Choker / Basket values
    length_m FLOAT,
    diameter_inch VARCHAR(50),
    branch_count INT,                   -- only for eslingas

    -- Editabl / dynamic fields
    project VARCHAR(200),
    usage_status ENUM('en_uso', 'en_stock', 'tag_rojo') DEFAULT 'en_stock' NOT NULL,

    -- Photos
    photo_accessory VARCHAR(500),
    photo_manufacturer_label VARCHAR(500),
    photo_supplier_marking VARCHAR(500),

    -- Computed semaphore (recalculated on inspection create/update)
    semaphore_status ENUM('green', 'yellow', 'red') DEFAULT 'green' NOT NULL,

    -- Cached inspection dates for fast semaphore recalculation
    last_external_inspection_date DATETIME,
    next_external_inspection_date DATETIME,
    last_field_inspection_date DATETIME,
    next_field_inspection_date DATETIME,

    -- Soft delete
    is_deleted BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by_id INT,

    INDEX idx_code (code),
    INDEX idx_semaphore_status (semaphore_status),
    INDEX idx_usage_status (usage_status),
    INDEX idx_is_deleted (is_deleted),
    FOREIGN KEY (created_by_id) REFERENCES users(id)
);

-- External Inspections (Certificadas, every 6 months)
CREATE TABLE external_inspections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_id INT NOT NULL,

    inspection_date DATETIME NOT NULL,
    next_inspection_date DATETIME NOT NULL,   -- auto: inspection_date + 6 months
    inspection_status ENUM('vigente', 'vencida') DEFAULT 'vigente' NOT NULL,

    responsible_company VARCHAR(200) NOT NULL,
    final_criteria VARCHAR(500) NOT NULL,
    certificate_file VARCHAR(500),

    project VARCHAR(200),
    brand VARCHAR(100),
    empresa ENUM('GEO', 'SBCIMAS', 'PREFA', 'BESSAC'),
    equipment_usage_status VARCHAR(50),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_id INT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,

    INDEX idx_equipment_id (equipment_id),
    INDEX idx_next_inspection_date (next_inspection_date),
    INDEX idx_is_deleted (is_deleted),
    FOREIGN KEY (equipment_id) REFERENCES equipment(id),
    FOREIGN KEY (created_by_id) REFERENCES users(id)
);

-- Field Inspections (Programa Código de Color, every 2 months)
CREATE TABLE field_inspections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_id INT NOT NULL,

    inspection_date DATETIME NOT NULL,
    next_inspection_date DATETIME NOT NULL,   -- auto: inspection_date + 2 months
    inspection_status ENUM('vigente', 'vencida') DEFAULT 'vigente' NOT NULL,
    color_period ENUM('ene_feb', 'mar_abr', 'may_jun', 'jul_ago', 'sep_oct', 'nov_dic') NOT NULL,

    final_criteria ENUM('buen_estado', 'mal_estado', 'observaciones') NOT NULL,
    responsible VARCHAR(200) NOT NULL,
    photos TEXT,                              -- JSON array of file paths

    project VARCHAR(200),
    brand VARCHAR(100),
    empresa ENUM('GEO', 'SBCIMAS', 'PREFA', 'BESSAC'),
    equipment_usage_status VARCHAR(50),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_id INT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,

    INDEX idx_equipment_id (equipment_id),
    INDEX idx_next_inspection_date (next_inspection_date),
    INDEX idx_color_period (color_period),
    INDEX idx_is_deleted (is_deleted),
    FOREIGN KEY (equipment_id) REFERENCES equipment(id),
    FOREIGN KEY (created_by_id) REFERENCES users(id)
);

-- Deincorporation Reports (Actas de Baja)
CREATE TABLE deincorporation_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_id INT NOT NULL,

    deincorporation_date DATETIME NOT NULL,
    reason TEXT NOT NULL,
    photos TEXT,                              -- JSON array of file paths
    responsible VARCHAR(200) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_id INT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,

    INDEX idx_equipment_id (equipment_id),
    INDEX idx_is_deleted (is_deleted),
    FOREIGN KEY (equipment_id) REFERENCES equipment(id),
    FOREIGN KEY (created_by_id) REFERENCES users(id)
);

-- Audit Logs (doesnt change)
CREATE TABLE audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id INT,
    old_value TEXT,                           -- JSON snapshot before change
    new_value TEXT,                           -- JSON snapshot after change
    details TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_user_id (user_id),
    INDEX idx_entity_type (entity_type),
    INDEX idx_entity_id (entity_id),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- User-Project Assignments (Admin assigns users to projects)
CREATE TABLE user_project_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    project_id INT NOT NULL,
    assigned_by_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uq_user_project (user_id, project_id),
    INDEX idx_user_id (user_id),
    INDEX idx_project_id (project_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (assigned_by_id) REFERENCES users(id)
);

