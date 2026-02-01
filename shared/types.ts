/**
 * Shared Type Definitions
 *
 * Types defined here are shared between frontend and backend.
 * Keep these in sync with backend Pydantic schemas.
 */

// API Response Types
export interface ApiResponse<T> {
    data?: T
    error?: ApiError
}

export interface ApiError {
    code: string
    message: string
    details?: Record<string, unknown>
}

// Pagination Types
export interface PaginatedResponse<T> {
    items: T[]
    total: number
    page: number
    pageSize: number
    totalPages: number
}

export interface PaginationParams {
    page?: number
    pageSize?: number
}

// Health Check Types
export interface HealthStatus {
    status: 'healthy' | 'unhealthy'
    service: string
}

export interface DatabaseHealthStatus extends HealthStatus {
    database: 'connected' | 'disconnected'
    error?: string
}

// Base Entity Types
export interface BaseEntity {
    id: string
    createdAt: string
    updatedAt: string
}

// User Types (placeholder for future implementation)
export interface User extends BaseEntity {
    email: string
    name: string
    isActive: boolean
}

// Job Application Types (placeholder for future implementation)
export interface JobApplication extends BaseEntity {
    userId: string
    companyName: string
    jobTitle: string
    status: ApplicationStatus
    appliedAt?: string
    notes?: string
}

export type ApplicationStatus =
    | 'pending'
    | 'applied'
    | 'interview'
    | 'offer'
    | 'rejected'
    | 'withdrawn'
