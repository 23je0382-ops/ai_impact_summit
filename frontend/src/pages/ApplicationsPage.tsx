import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api, { Application } from '../services/api'

export default function ApplicationsPage() {
    const [applications, setApplications] = useState<Application[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [statusFilter, setStatusFilter] = useState<string>('')
    const [searchQuery, setSearchQuery] = useState('')
    const [showNewForm, setShowNewForm] = useState(false)

    useEffect(() => {
        loadApplications()
    }, [statusFilter])

    const loadApplications = async () => {
        try {
            setLoading(true)
            const params: { status?: string; search?: string } = {}
            if (statusFilter) params.status = statusFilter
            if (searchQuery) params.search = searchQuery

            const response = await api.getApplications(params)
            setApplications(response.data.applications)
        } catch (err) {
            setError('Failed to load applications')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const handleSearch = () => {
        loadApplications()
    }

    const handleStatusChange = async (id: string, newStatus: string) => {
        try {
            await api.updateApplicationStatus(id, newStatus)
            loadApplications()
        } catch (err) {
            console.error('Failed to update status:', err)
        }
    }

    const handleDelete = async (id: string) => {
        if (!window.confirm('Are you sure you want to delete this application?')) return

        try {
            await api.deleteApplication(id)
            loadApplications()
        } catch (err) {
            console.error('Failed to delete:', err)
        }
    }

    const getStatusColor = (status: string) => {
        const colors: Record<string, string> = {
            pending: 'bg-yellow-100 text-yellow-800 border-yellow-200',
            applied: 'bg-blue-100 text-blue-800 border-blue-200',
            interviewing: 'bg-purple-100 text-purple-800 border-purple-200',
            offered: 'bg-green-100 text-green-800 border-green-200',
            rejected: 'bg-red-100 text-red-800 border-red-200',
            withdrawn: 'bg-gray-100 text-gray-800 border-gray-200',
        }
        return colors[status] || 'bg-gray-100 text-gray-800 border-gray-200'
    }

    const statuses = ['pending', 'applied', 'interviewing', 'offered', 'rejected', 'withdrawn']

    return (
        <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50">
            {/* Header */}
            <header className="glass sticky top-0 z-50 border-b border-secondary-200">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex items-center justify-between">
                        <Link to="/" className="text-2xl font-bold text-primary-600">
                            Job Application Automation
                        </Link>
                        <nav className="flex items-center space-x-4">
                            <Link to="/dashboard" className="text-secondary-600 hover:text-primary-600 transition-colors">
                                Dashboard
                            </Link>
                            <Link to="/jobs" className="text-secondary-600 hover:text-primary-600 transition-colors">
                                Jobs
                            </Link>
                            <Link to="/applications" className="text-primary-600 font-medium">
                                Applications
                            </Link>
                            <Link to="/profile" className="text-secondary-600 hover:text-primary-600 transition-colors">
                                Profile
                            </Link>
                        </nav>
                    </div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="flex items-center justify-between mb-8">
                    <h1 className="text-3xl font-bold text-secondary-900">Applications</h1>
                    <button
                        onClick={() => setShowNewForm(true)}
                        className="btn-primary"
                    >
                        + New Application
                    </button>
                </div>

                {/* Filters */}
                <div className="card mb-6">
                    <div className="flex flex-wrap gap-4">
                        <div className="flex-1 min-w-[200px]">
                            <input
                                type="text"
                                placeholder="Search company or job title..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                                className="input"
                            />
                        </div>
                        <select
                            value={statusFilter}
                            onChange={(e) => setStatusFilter(e.target.value)}
                            className="input w-auto"
                        >
                            <option value="">All Statuses</option>
                            {statuses.map((status) => (
                                <option key={status} value={status}>
                                    {status.charAt(0).toUpperCase() + status.slice(1)}
                                </option>
                            ))}
                        </select>
                        <button onClick={handleSearch} className="btn-secondary">
                            Search
                        </button>
                    </div>
                </div>

                {error && (
                    <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                        {error}
                    </div>
                )}

                {/* Applications List */}
                {loading ? (
                    <div className="flex items-center justify-center py-12">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
                    </div>
                ) : applications.length === 0 ? (
                    <div className="card text-center py-12">
                        <svg className="w-16 h-16 mx-auto text-secondary-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <h3 className="text-lg font-medium text-secondary-900 mb-2">No applications yet</h3>
                        <p className="text-secondary-500 mb-4">Start tracking your job applications</p>
                        <button onClick={() => setShowNewForm(true)} className="btn-primary">
                            Add Your First Application
                        </button>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {applications.map((app) => (
                            <div key={app.id} className="card hover:shadow-lg transition-shadow">
                                <div className="flex flex-wrap items-start justify-between gap-4">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-3 mb-2">
                                            <h3 className="text-lg font-semibold text-secondary-900">{app.job_title}</h3>
                                            <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(app.status)}`}>
                                                {app.status}
                                            </span>
                                        </div>
                                        <p className="text-secondary-600 mb-2">{app.company_name}</p>
                                        <div className="flex flex-wrap gap-4 text-sm text-secondary-500">
                                            {app.location && (
                                                <span className="flex items-center gap-1">
                                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                                    </svg>
                                                    {app.location}
                                                </span>
                                            )}
                                            {app.remote && (
                                                <span className="text-green-600 font-medium">Remote</span>
                                            )}
                                            {app.applied_at && (
                                                <span>Applied: {new Date(app.applied_at).toLocaleDateString()}</span>
                                            )}
                                        </div>
                                        {app.notes && (
                                            <p className="mt-2 text-sm text-secondary-600 bg-secondary-50 p-2 rounded">
                                                {app.notes}
                                            </p>
                                        )}
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <select
                                            value={app.status}
                                            onChange={(e) => handleStatusChange(app.id, e.target.value)}
                                            className="input w-auto text-sm py-1"
                                        >
                                            {statuses.map((status) => (
                                                <option key={status} value={status}>
                                                    {status.charAt(0).toUpperCase() + status.slice(1)}
                                                </option>
                                            ))}
                                        </select>
                                        {app.job_url && (
                                            <a
                                                href={app.job_url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="p-2 text-secondary-500 hover:text-primary-600 transition-colors"
                                                title="Open job posting"
                                            >
                                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                                </svg>
                                            </a>
                                        )}
                                        <button
                                            onClick={() => handleDelete(app.id)}
                                            className="p-2 text-red-500 hover:text-red-700 transition-colors"
                                            title="Delete"
                                        >
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* New Application Modal */}
                {showNewForm && (
                    <NewApplicationModal
                        onClose={() => setShowNewForm(false)}
                        onSave={() => {
                            setShowNewForm(false)
                            loadApplications()
                        }}
                    />
                )}
            </main>
        </div>
    )
}

// New Application Modal Component
function NewApplicationModal({ onClose, onSave }: { onClose: () => void; onSave: () => void }) {
    const [formData, setFormData] = useState({
        company_name: '',
        job_title: '',
        job_url: '',
        status: 'pending',
        location: '',
        remote: false,
        notes: '',
    })
    const [saving, setSaving] = useState(false)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        try {
            setSaving(true)
            await api.createApplication({
                ...formData,
                tags: [],
            })
            onSave()
        } catch (err) {
            console.error('Failed to create application:', err)
        } finally {
            setSaving(false)
        }
    }

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
                <div className="p-6">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-xl font-semibold text-secondary-900">New Application</h2>
                        <button onClick={onClose} className="text-secondary-400 hover:text-secondary-600">
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-secondary-700 mb-1">
                                Company Name *
                            </label>
                            <input
                                type="text"
                                required
                                value={formData.company_name}
                                onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                                className="input"
                                placeholder="e.g., Google"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-secondary-700 mb-1">
                                Job Title *
                            </label>
                            <input
                                type="text"
                                required
                                value={formData.job_title}
                                onChange={(e) => setFormData({ ...formData, job_title: e.target.value })}
                                className="input"
                                placeholder="e.g., Software Engineer"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-secondary-700 mb-1">
                                Job URL
                            </label>
                            <input
                                type="url"
                                value={formData.job_url}
                                onChange={(e) => setFormData({ ...formData, job_url: e.target.value })}
                                className="input"
                                placeholder="https://..."
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-secondary-700 mb-1">
                                Location
                            </label>
                            <input
                                type="text"
                                value={formData.location}
                                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                                className="input"
                                placeholder="e.g., San Francisco, CA"
                            />
                        </div>

                        <div className="flex items-center gap-2">
                            <input
                                type="checkbox"
                                id="remote"
                                checked={formData.remote}
                                onChange={(e) => setFormData({ ...formData, remote: e.target.checked })}
                                className="w-4 h-4 text-primary-600 rounded border-secondary-300 focus:ring-primary-500"
                            />
                            <label htmlFor="remote" className="text-sm text-secondary-700">
                                Remote position
                            </label>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-secondary-700 mb-1">
                                Status
                            </label>
                            <select
                                value={formData.status}
                                onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                                className="input"
                            >
                                <option value="pending">Pending</option>
                                <option value="applied">Applied</option>
                                <option value="interviewing">Interviewing</option>
                                <option value="offered">Offered</option>
                                <option value="rejected">Rejected</option>
                                <option value="withdrawn">Withdrawn</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-secondary-700 mb-1">
                                Notes
                            </label>
                            <textarea
                                value={formData.notes}
                                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                                className="input"
                                rows={3}
                                placeholder="Any additional notes..."
                            />
                        </div>

                        <div className="flex justify-end gap-3 pt-4">
                            <button type="button" onClick={onClose} className="btn-secondary">
                                Cancel
                            </button>
                            <button type="submit" disabled={saving} className="btn-primary">
                                {saving ? 'Saving...' : 'Save Application'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    )
}
