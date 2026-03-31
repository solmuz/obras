// Authentication types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'ADMIN' | 'INGENIERO_HSE' | 'CONSULTA';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  email: string;
  full_name: string;
  password: string;
  role?: 'ADMIN' | 'INGENIERO_HSE' | 'CONSULTA';
}

export interface UserUpdate {
  full_name?: string;
  role?: 'ADMIN' | 'INGENIERO_HSE' | 'CONSULTA';
  is_active?: boolean;
}

// Project types
export type ProjectStatus = 'ACTIVO' | 'INACTIVO';

export interface Project {
  id: string;
  name: string;
  description?: string;
  status: ProjectStatus;
  start_date: string;
  created_at: string;
  updated_at: string;
  employee_count: number;
  accessory_count: number;
}

export interface ProjectDetail extends Omit<Project, 'employee_count'> {
  employees: User[];
  accessory_count: number;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  status?: ProjectStatus;
  start_date: string;
}

export interface ProjectUpdate {
  name?: string;
  description?: string;
  status?: ProjectStatus;
}

// Accessory types
export type AccessoryStatus = 'EN_USO' | 'EN_STOCK' | 'TAG_ROJO';
export type ElementType = 'ESLINGAS' | 'GRILLETES' | 'GANCHOS' | 'OTROS';
export type Brand = 'BRAND_1' | 'BRAND_2' | 'BRAND_3';

export enum SemaforoStatus {
  VERDE = 'VERDE',
  AMARILLO = 'AMARILLO',
  ROJO = 'ROJO',
}

export interface Accessory {
  id: string;
  code_internal: string;
  element_type: ElementType;
  brand: Brand;
  serial: string;
  material: string;
  capacity_vertical?: string;
  capacity_choker?: string;
  capacity_basket?: string;
  length_m?: number;
  diameter_inches?: string;
  num_ramales?: number;
  project_id: string;
  status: AccessoryStatus;
  photo_accessory?: string;
  photo_manufacturer_label?: string;
  photo_provider_marking?: string;
  version: number;
  created_at: string;
  updated_at: string;
  semaforo_status?: string;
}

export interface AccessoryCreate {
  code_internal: string;
  element_type: ElementType;
  brand: Brand;
  serial: string;
  material: string;
  capacity_vertical?: string;
  capacity_choker?: string;
  capacity_basket?: string;
  length_m?: number;
  diameter_inches?: string;
  num_ramales?: number;
  project_id: string;
  status?: AccessoryStatus;
}

export interface AccessoryUpdate {
  project_id?: string;
  status?: AccessoryStatus;
}

export interface AccessoryListItem {
  id: string;
  code_internal: string;
  element_type: ElementType;
  brand: Brand;
  status: AccessoryStatus;
  semaforo_status: string;
}

// Inspection types
export type InspectionStatus = 'VIGENTE' | 'VENCIDA';
export type InspectionCompany = 'GEO' | 'SBCIMAS' | 'PREFA' | 'BESSAC';
export type SiteInspectionResult = 'BUEN_ESTADO' | 'MAL_ESTADO' | 'OBSERVACIONES';
export type ColorPeriod = 'ENE_FEB' | 'MAR_ABR' | 'MAY_JUN' | 'JUL_AGO' | 'SEP_OCT' | 'NOV_DIC';

export interface ExternalInspection {
  id: string;
  accessory_id: string;
  inspection_date: string;
  company: InspectionCompany;
  company_responsible: string;
  final_criterion: string;
  next_inspection_date: string;
  status: InspectionStatus;
  certificate_number?: string;
  certificate_pdf: string;
  project_name: string;
  equipment_status: string;
  created_at: string;
  updated_at: string;
}

export interface ExternalInspectionCreate {
  accessory_id: string;
  inspection_date: string;
  company: InspectionCompany;
  company_responsible: string;
  final_criterion: string;
  certificate_number?: string;
  project_name: string;
  equipment_status: string;
}

export interface SiteInspection {
  id: string;
  accessory_id: string;
  inspection_date: string;
  final_criterion: SiteInspectionResult;
  inspector_name: string;
  company: InspectionCompany;
  color_period: ColorPeriod;
  next_inspection_date: string;
  status: InspectionStatus;
  photo_urls?: string[];
  project_name: string;
  equipment_status: string;
  created_at: string;
  updated_at: string;
}

export interface SiteInspectionCreate {
  accessory_id: string;
  inspection_date: string;
  final_criterion: SiteInspectionResult;
  inspector_name: string;
  company: InspectionCompany;
  project_name: string;
  equipment_status: string;
}

// Decommission types
export interface Decommission {
  id: string;
  accessory_id: string;
  decommission_date: string;
  reason: string;
  responsible_name: string;
  photo_urls?: string[];
  created_at: string;
  updated_at: string;
}

export interface DecommissionCreate {
  accessory_id: string;
  decommission_date: string;
  reason: string;
  responsible_name: string;
}

// Audit types
export interface AuditLog {
  id: string;
  user_id: string;
  entity_type: string;
  entity_id: string;
  action: 'CREATE' | 'UPDATE' | 'DELETE';
  old_values?: Record<string, unknown>;
  new_values?: Record<string, unknown>;
  change_description?: string;
  created_at: string;
}

// Report types
export interface SemaforoReport {
  accessory_id: string;
  code_internal: string;
  status: SemaforoStatus;
  external_inspection_date?: string;
  site_inspection_date?: string;
  next_external_date?: string;
  next_site_date?: string;
}

// Pagination helper
export interface PaginationParams {
  skip?: number;
  limit?: number;
}
