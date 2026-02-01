
import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
    CheckCircleIcon,
    XCircleIcon,
    FunnelIcon,
    ArrowPathIcon,
    DocumentMagnifyingGlassIcon,
    XMarkIcon
} from '@heroicons/react/24/outline'
import api, { TrackerSummary, Application, AuditLog } from '../services/api'
import { useToast } from '../context/ToastContext'

export default function TrackerPage() {
    const [summary, setSummary] = useState<TrackerSummary | null>(null)
    const [applications, setApplications] = useState<Application[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    // Filters
    const [statusFilter, setStatusFilter] = useState<string>('')
    const [companyFilter, setCompanyFilter] = useState<string>('')

    // Audit Modal
    const [selectedJobId, setSelectedJobId] = useState<string | null>(null)
    const [auditLogs, setAuditLogs] = useState<AuditLog[]>([])
    const [loadingAudit, setLoadingAudit] = useState(false)

    const { showToast } = useToast()

    useEffect(() => {
        loadData()
    }, [])

    useEffect(() => {
        loadApplications()
    }, [statusFilter, companyFilter])

    const loadData = async () => {
        try {
            const sumRes = await api.getTrackerSummary()
            setSummary(sumRes.data)
            await loadApplications()
        } catch (err) {
            setError('Failed to load tracker data')
            showToast('Failed to load tracker data', 'error')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const loadApplications = async () => {
        try {
            const filters: any = {}
            if (statusFilter) filters.status = statusFilter
            if (companyFilter) filters.company = companyFilter

            const appsRes = await api.getTrackerApplications(filters)
            setApplications(appsRes.data)
        } catch (err) {
            console.error('Failed to load applications', err)
            showToast('Failed to load applications', 'error')
        }
    }

    const handleRetry = async (appId: string) => {
        if (!confirm('Retry this application?')) return
        try {
            await api.retryApplication(appId)
            showToast('Application queued for retry', 'success')
            loadData() // Reload to see status change
        } catch (err) {
            showToast('Retry failed', 'error')
        }
    }

    const viewAudit = async (jobId: string) => {
        setSelectedJobId(jobId)
        setLoadingAudit(true)
        setAuditLogs([])
        try {
            const res = await api.getApplicationAudit(jobId)
            setAuditLogs(res.data)
        } catch (err) {
            console.error('Failed to load audit logs', err)
            setAuditLogs([])
        } finally {
            setLoadingAudit(false)
        }
    }

    const closeAudit = () => {
        setSelectedJobId(null)
        setAuditLogs([])
    }

    const exportCSV = () => {
        const headers = ['Company', 'Job Title', 'Status', 'Date', 'Notes']
        const csvContent = [
            headers.join(','),
            ...applications.map(app => [
                app.company_name,
                app.job_title,
                app.status,
                new Date(app.updated_at || Date.now()).toLocaleDateString(),
                `"${(app.notes || '').replace(/"/g, '""')}"`
            ].join(','))
        ].join('\n')

        const blob = new Blob([csvContent], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `applications_export_${new Date().toISOString().split('T')[0]}.csv`
        a.click()
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <header className="bg-white shadow-sm sticky top-0 z-30 -mx-4 sm:-mx-6 lg:-mx-8 px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Link to="/dashboard" className="text-gray-500 hover:text-gray-700">← Back</Link>
                    <h1 className="text-2xl font-bold text-gray-900">Application Tracker</h1>
                </div>
                <button onClick={exportCSV} className="text-blue-600 hover:text-blue-800 font-medium text-sm">
                    Export CSV
                </button>
            </header>

            <main className="max-w-7xl mx-auto">
                {error && (
                    <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                        {error}
                    </div>
                )}

                {/* Summary Cards */}
                {summary && (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                            <p className="text-sm text-gray-500">Total Applications</p>
                            <p className="text-3xl font-bold text-gray-900">{summary.total_applications}</p>
                        </div>
                        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                            <p className="text-sm text-gray-500">Success Rate</p>
                            <p className="text-3xl font-bold text-green-600">{Math.round(summary.success_rate * 100)}%</p>
                        </div>
                        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                            <p className="text-sm text-gray-500">Submitted Today</p>
                            <p className="text-3xl font-bold text-blue-600">
                                {summary.recent_activity.filter(a => new Date(a.updated_at).toDateString() === new Date().toDateString()).length}
                            </p>
                        </div>
                        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                            <p className="text-sm text-gray-500">Failed</p>
                            <p className="text-3xl font-bold text-red-600">{summary.status_breakdown['failed'] || 0}</p>
                        </div>
                    </div>
                )}

                {/* Filters */}
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 mb-6 flex flex-wrap gap-4 items-center">
                    <div className="flex items-center gap-2 text-gray-500">
                        <FunnelIcon className="w-5 h-5" />
                        <span className="font-medium">Filters:</span>
                    </div>
                    <select
                        className="border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                    >
                        <option value="">All Statuses</option>
                        <option value="submitted">Submitted</option>
                        <option value="failed">Failed</option>
                        <option value="pending">Pending</option>
                    </select>
                    <input
                        type="text"
                        placeholder="Filter by Company..."
                        className="border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                        value={companyFilter}
                        onChange={(e) => setCompanyFilter(e.target.value)}
                    />
                </div>

                {/* Applications Table */}
                <div className="bg-white shadow-sm rounded-lg overflow-hidden border border-gray-200">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Company</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {applications.map((app) => (
                                <tr key={app.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">{app.company_name}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-gray-500">{app.job_title}</td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                                            ${app.status === 'submitted' ? 'bg-green-100 text-green-800' :
                                                app.status === 'failed' ? 'bg-red-100 text-red-800' :
                                                    'bg-yellow-100 text-yellow-800'}`}>
                                            {app.status}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-gray-500 text-sm">
                                        {new Date(app.updated_at || Date.now()).toLocaleDateString()}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium flex justify-end gap-3">
                                        <button
                                            onClick={() => viewAudit(app.job_id || app.id)} // Prefer job_id for audit lookup if based on job
                                            className="text-gray-400 hover:text-blue-600"
                                            title="View Audit Log"
                                        >
                                            <DocumentMagnifyingGlassIcon className="w-5 h-5" />
                                        </button>
                                        {app.status === 'failed' && (
                                            <button
                                                onClick={() => handleRetry(app.id)}
                                                className="text-red-600 hover:text-red-900 flex items-center gap-1"
                                            >
                                                <ArrowPathIcon className="w-4 h-4" /> Retry
                                            </button>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {!loading && applications.length === 0 && (
                        <div className="p-8 text-center text-gray-500">
                            No applications found matching your filters.
                        </div>
                    )}
                </div>
            </main>

            {/* Audit Log Modal */}
            {selectedJobId && (
                <div className="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
                    <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
                        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={closeAudit}></div>
                        <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
                        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
                            <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                                <div className="flex justify-between items-start mb-4">
                                    <h3 className="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                                        Application Audit Trail
                                    </h3>
                                    <button onClick={closeAudit} className="text-gray-400 hover:text-gray-500">
                                        <XMarkIcon className="w-6 h-6" />
                                    </button>
                                </div>
                                <div className="mt-2 text-sm text-gray-500 max-h-96 overflow-y-auto">
                                    {loadingAudit ? (
                                        <div className="flex justify-center p-4">
                                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                                        </div>
                                    ) : auditLogs.length === 0 ? (
                                        <p>No audit logs found for this application.</p>
                                    ) : (
                                        <div className="relative border-l-2 border-blue-200 ml-3 space-y-6 pl-6 py-2">
                                            {auditLogs.map((log) => (
                                                <div key={log.id} className="relative">
                                                    <div className="absolute -left-8 mt-1.5 w-4 h-4 rounded-full bg-blue-500 border-2 border-white"></div>
                                                    <div>
                                                        <span className="text-xs font-bold text-blue-600 uppercase tracking-wide">
                                                            {log.step}
                                                        </span>
                                                        <span className="ml-2 text-xs text-gray-400">
                                                            {new Date(log.timestamp || Date.now()).toLocaleTimeString()}
                                                        </span>
                                                        <h4 className="text-md font-semibold text-gray-900 capitalize mt-1">
                                                            {log.event_type.replace('_', ' ')}
                                                        </h4>
                                                        <div className="mt-2 bg-gray-50 rounded p-3 text-xs font-mono overflow-x-auto border border-gray-100">
                                                            <pre>{JSON.stringify(log.details, null, 2)}</pre>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
