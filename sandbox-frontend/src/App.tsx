
import React, { useState, useEffect } from 'react'
import axios from 'axios'
import {
    Briefcase,
    MapPin,
    Clock,
    CheckCircle,
    AlertCircle,
    Search,
    Menu,
    ShieldCheck,
    ArrowRight,
    Upload,
    Trash2
} from 'lucide-react'

const SANDBOX_API = 'http://localhost:8001'
const API_KEY = 'sandbox_demo_key_2026'

interface Job {
    id: string
    title: string
    company: string
    location: string
    job_type: string
    experience_level: string
    salary_range?: string
    description?: string
    requirements?: string[]
    responsibilities?: string[]
    skills_required: string[]
    benefits?: string[]
    posted_date: string
    is_remote: boolean
}

interface ApplicationForm {
    applicant_name: string
    email: string
    phone: string
    resume_text: string
    cover_letter: string
    work_authorization: string
    availability: string
}

interface Application {
    id: string
    job_id: string
    job_title: string
    company: string
    submitted_at: string
    status: string
    applicant: ApplicationForm
}

function App() {
    const [jobs, setJobs] = useState<Job[]>([])
    const [applications, setApplications] = useState<Application[]>([])
    const [loading, setLoading] = useState(true)
    const [loadingMore, setLoadingMore] = useState(false)
    const [searchTerm, setSearchTerm] = useState('')
    const [view, setView] = useState<'public' | 'admin' | 'job_detail' | 'apply_form' | 'artifact_detail'>('public')
    const [selectedJob, setSelectedJob] = useState<Job | null>(null)
    const [selectedApplication, setSelectedApplication] = useState<Application | null>(null)
    const [page, setPage] = useState(1)
    const [hasMore, setHasMore] = useState(true)
    const [submitting, setSubmitting] = useState(false)
    const [resumeFile, setResumeFile] = useState<string | null>(null)

    const fetchJobs = async (pageToFetch = 1, append = false) => {
        try {
            if (append) setLoadingMore(true);
            const res = await axios.get(`${SANDBOX_API}/sandbox/jobs`, {
                params: { page: pageToFetch, per_page: 20 }
            })

            const newJobs = res.data.jobs;
            if (append) {
                setJobs(prev => [...prev, ...newJobs]);
            } else {
                setJobs(newJobs);
            }

            setHasMore(res.data.page * res.data.per_page < res.data.total);
            setPage(pageToFetch);
        } catch (err) {
            console.error('Failed to fetch jobs', err)
        } finally {
            setLoadingMore(false);
        }
    }

    const fetchApplications = async () => {
        try {
            const res = await axios.get(`${SANDBOX_API}/sandbox/applications`, {
                headers: { 'X-API-Key': API_KEY }
            })
            setApplications(res.data)
        } catch (err) {
            console.error('Failed to fetch applications', err)
        }
    }

    const handleLoadMore = () => {
        fetchJobs(page + 1, true);
    };

    const handleViewJob = async (id: string) => {
        try {
            setLoading(true)
            const res = await axios.get(`${SANDBOX_API}/sandbox/jobs/${id}`)
            setSelectedJob(res.data)
            setView('job_detail')
        } catch (err) {
            console.error('Failed to fetch job details', err)
        } finally {
            setLoading(false)
        }
    }

    const handleSubmitApplication = async (formData: ApplicationForm) => {
        if (!selectedJob) return

        try {
            setSubmitting(true)
            const res = await axios.post(`${SANDBOX_API}/sandbox/jobs/${selectedJob.id}/apply`, formData, {
                headers: { 'X-API-Key': API_KEY }
            })

            if (res.data.application_id) {
                alert(`Application submitted successfully! Tracking ID: ${res.data.application_id}`)
                await fetchApplications()
                setResumeFile(null)
                setView('admin')
            }
        } catch (err) {
            console.error('Application failed', err)
            alert('Failed to submit application. Please check your network or API key.')
        } finally {
            setSubmitting(false)
        }
    }

    const handleDeleteApplication = async (appId: string) => {
        try {
            await axios.delete(`${SANDBOX_API}/sandbox/applications/${appId}`, {
                headers: { 'X-API-Key': API_KEY }
            })
            setApplications(applications.filter(a => a.id !== appId))
        } catch (err) {
            console.error('Failed to delete application', err)
        }
    }

    useEffect(() => {
        window.scrollTo(0, 0)
    }, [view])

    useEffect(() => {
        const init = async () => {
            setLoading(true)
            await fetchJobs(1, false)
            await fetchApplications()
            setLoading(false)
        }
        init()

        // Poll for new applications every 5 seconds for the "Real-time" effect
        const interval = setInterval(fetchApplications, 5000)
        return () => clearInterval(interval)
    }, [])

    const filteredJobs = jobs.filter(job =>
        job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.company.toLowerCase().includes(searchTerm.toLowerCase())
    )

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
            {/* Navigation */}
            <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16 items-center">
                        <div className="flex items-center gap-2">
                            <div className="bg-sandbox-600 p-2 rounded-lg text-white">
                                <ShieldCheck size={24} />
                            </div>
                            <span className="text-xl font-bold text-gray-900 tracking-tight">SandboxPortal</span>
                            <span className="bg-sandbox-100 text-sandbox-700 text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ml-1">Mock Job Board</span>
                        </div>

                        <div className="hidden md:flex items-center gap-6">
                            <button
                                onClick={() => setView('public')}
                                className={`text-sm font-medium ${view === 'public' || view === 'job_detail' || view === 'apply_form' ? 'text-sandbox-600' : 'text-gray-500 hover:text-gray-900'}`}
                            >
                                Job Listings
                            </button>
                            <button
                                onClick={() => setView('admin')}
                                className={`text-sm font-medium ${view === 'admin' ? 'text-sandbox-600' : 'text-gray-500 hover:text-gray-900'}`}
                            >
                                Incoming Applications
                                {applications.length > 0 && (
                                    <span className="ml-2 bg-red-500 text-white text-[10px] px-1.5 py-0.5 rounded-full">
                                        {applications.length}
                                    </span>
                                )}
                            </button>
                        </div>

                        <div className="flex items-center gap-4">
                            <div className="text-xs text-gray-400 hidden sm:block">
                                API: localhost:8001
                            </div>
                            <button className="md:hidden p-2 text-gray-500">
                                <Menu size={20} />
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Sub-header / Search */}
            {view === 'public' && (
                <div className="bg-sandbox-900 py-12 px-4 shadow-inner">
                    <div className="max-w-4xl mx-auto text-center">
                        <h1 className="text-3xl font-extrabold text-white sm:text-4xl">
                            Find your next career move.
                        </h1>
                        <p className="mt-3 text-lg text-sandbox-200 max-w-2xl mx-auto">
                            The sandbox environment simulates a real production job board to stress-test your autonomous agent.
                        </p>

                        <div className="mt-8 flex max-w-lg mx-auto bg-white rounded-xl shadow-2xl overflow-hidden focus-within:ring-2 focus-within:ring-sandbox-500">
                            <div className="pl-4 flex items-center text-gray-400">
                                <Search size={20} />
                            </div>
                            <input
                                type="text"
                                placeholder="Search by job title or company..."
                                className="flex-1 px-4 py-4 text-gray-900 focus:outline-none"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </div>
                    </div>
                </div>
            )}

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full">
                {view === 'public' ? (
                    <div className="space-y-6">
                        <div className="flex justify-between items-end">
                            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-widest">
                                Showing {filteredJobs.length} Job Postings
                            </h2>
                        </div>

                        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                            {filteredJobs.map(job => (
                                <div key={job.id} className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow group flex flex-col">
                                    <div className="flex justify-between items-start mb-4">
                                        <div>
                                            <h3 className="text-lg font-bold text-gray-900 group-hover:text-sandbox-600 transition-colors">
                                                {job.title}
                                            </h3>
                                            <div className="text-sandbox-600 font-medium text-sm flex items-center gap-1 mt-1">
                                                <Briefcase size={14} />
                                                {job.company}
                                            </div>
                                        </div>
                                        <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase ${job.job_type === 'internship' ? 'bg-orange-100 text-orange-700' : 'bg-blue-100 text-blue-700'
                                            }`}>
                                            {job.job_type}
                                        </span>
                                    </div>

                                    <div className="grid grid-cols-2 gap-y-2 text-sm text-gray-500 mb-4">
                                        <div className="flex items-center gap-2">
                                            <MapPin size={14} className="text-gray-300" />
                                            {job.location}
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <Clock size={14} className="text-gray-300" />
                                            Posted {job.posted_date}
                                        </div>
                                    </div>

                                    <div className="flex flex-wrap gap-2 mb-6">
                                        {job.skills_required.map(skill => (
                                            <span key={skill} className="bg-gray-100 text-gray-600 px-2 py-1 rounded-md text-xs">
                                                {skill}
                                            </span>
                                        ))}
                                    </div>

                                    <div className="mt-auto pt-4 border-t border-gray-50 flex justify-between items-center">
                                        <div className="text-xs text-gray-400 font-mono">ID: {job.id.substring(0, 8)}...</div>
                                        <button
                                            onClick={() => handleViewJob(job.id)}
                                            className="bg-sandbox-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-sandbox-700 transition-colors flex items-center gap-2"
                                        >
                                            Apply Now <ArrowRight size={14} />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {hasMore && (
                            <div className="flex justify-center py-8">
                                <button
                                    onClick={handleLoadMore}
                                    disabled={loadingMore}
                                    className="px-8 py-3 bg-white border border-gray-200 rounded-xl text-sm font-bold text-gray-700 hover:bg-gray-50 hover:border-sandbox-300 transition-all shadow-sm flex items-center gap-2 group disabled:opacity-50"
                                >
                                    {loadingMore ? (
                                        <div className="w-4 h-4 border-2 border-sandbox-600 border-t-transparent rounded-full animate-spin"></div>
                                    ) : (
                                        <>
                                            Show More Opportunities
                                            <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform text-sandbox-500" />
                                        </>
                                    )}
                                </button>
                            </div>
                        )}
                    </div>
                ) : view === 'job_detail' && selectedJob ? (
                    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <button
                            onClick={() => setView('public')}
                            className="bg-white border border-gray-200 px-4 py-2 rounded-lg text-sm font-medium text-gray-600 hover:text-gray-900 flex items-center gap-2"
                        >
                            &larr; Back to Listings
                        </button>

                        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
                            <div className="p-8 border-b border-gray-100">
                                <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
                                    <div>
                                        <div className="flex items-center gap-3 mb-2">
                                            <span className="bg-sandbox-100 text-sandbox-700 text-[10px] font-bold px-2 py-0.5 rounded uppercase">{selectedJob.job_type}</span>
                                            <span className="bg-gray-100 text-gray-600 text-[10px] font-bold px-2 py-0.5 rounded uppercase">{selectedJob.experience_level}</span>
                                        </div>
                                        <h1 className="text-3xl font-bold text-gray-900">{selectedJob.title}</h1>
                                        <div className="flex items-center gap-4 mt-2 text-gray-600">
                                            <div className="flex items-center gap-1">
                                                <Briefcase size={16} className="text-sandbox-500" />
                                                <span className="font-semibold">{selectedJob.company}</span>
                                            </div>
                                            <div className="flex items-center gap-1">
                                                <MapPin size={16} className="text-gray-400" />
                                                <span>{selectedJob.location}</span>
                                            </div>
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => setView('apply_form')}
                                        className="w-full sm:w-auto bg-sandbox-600 text-white px-8 py-3 rounded-xl font-bold hover:bg-sandbox-700 transition-all shadow-lg shadow-sandbox-200 flex items-center justify-center gap-2"
                                    >
                                        Apply Now <ArrowRight size={18} />
                                    </button>
                                </div>
                            </div>

                            <div className="p-8 grid grid-cols-1 md:grid-cols-3 gap-12">
                                <div className="md:col-span-2 space-y-8">
                                    <section>
                                        <h2 className="text-xl font-bold text-gray-900 mb-4">Description</h2>
                                        <p className="text-gray-600 leading-relaxed whitespace-pre-wrap">
                                            {selectedJob.description || "No description provided."}
                                        </p>
                                    </section>

                                    {selectedJob.requirements && selectedJob.requirements.length > 0 && (
                                        <section>
                                            <h2 className="text-xl font-bold text-gray-900 mb-4">Requirements</h2>
                                            <ul className="space-y-3">
                                                {selectedJob.requirements.map((req, i) => (
                                                    <li key={i} className="flex gap-3 text-gray-600">
                                                        <div className="mt-1.5 w-1.5 h-1.5 rounded-full bg-sandbox-500 shrink-0"></div>
                                                        {req}
                                                    </li>
                                                ))}
                                            </ul>
                                        </section>
                                    )}

                                    {selectedJob.responsibilities && selectedJob.responsibilities.length > 0 && (
                                        <section>
                                            <h2 className="text-xl font-bold text-gray-900 mb-4">Responsibilities</h2>
                                            <ul className="space-y-3">
                                                {selectedJob.responsibilities.map((res, i) => (
                                                    <li key={i} className="flex gap-3 text-gray-600">
                                                        <div className="mt-1.5 w-1.5 h-1.5 rounded-full bg-sandbox-500 shrink-0"></div>
                                                        {res}
                                                    </li>
                                                ))}
                                            </ul>
                                        </section>
                                    )}
                                </div>

                                <div className="space-y-8">
                                    <div className="bg-gray-50 rounded-xl p-6 border border-gray-100">
                                        <h3 className="font-bold text-gray-900 mb-4">Job Details</h3>
                                        <dl className="space-y-4 text-sm">
                                            <div>
                                                <dt className="text-gray-500 mb-1">Status</dt>
                                                <dd className="font-medium text-green-600 flex items-center gap-1.5">
                                                    <div className="w-1.5 h-1.5 rounded-full bg-green-500"></div>
                                                    Accepting Applications
                                                </dd>
                                            </div>
                                            <div>
                                                <dt className="text-gray-500 mb-1">Salary Range</dt>
                                                <dd className="font-medium">{selectedJob.salary_range || "Competitive"}</dd>
                                            </div>
                                            <div>
                                                <dt className="text-gray-500 mb-1">Remote Available</dt>
                                                <dd className="font-medium">{selectedJob.is_remote ? "Yes" : "No"}</dd>
                                            </div>
                                            <div>
                                                <dt className="text-gray-500 mb-1">Posted Date</dt>
                                                <dd className="font-medium">{selectedJob.posted_date}</dd>
                                            </div>
                                        </dl>
                                    </div>

                                    <div>
                                        <h3 className="font-bold text-gray-900 mb-4">Required Skills</h3>
                                        <div className="flex flex-wrap gap-2">
                                            {selectedJob.skills_required.map(skill => (
                                                <span key={skill} className="bg-white border border-gray-200 text-gray-700 px-3 py-1 rounded-lg text-xs font-medium">
                                                    {skill}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                ) : view === 'apply_form' && selectedJob ? (
                    <div className="max-w-2xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden">
                            <div className="bg-sandbox-900 p-8 text-white relative">
                                <button
                                    onClick={() => setView('job_detail')}
                                    className="absolute left-4 top-4 text-white/50 hover:text-white transition-colors"
                                >
                                    &larr; Cancel
                                </button>
                                <div className="text-center">
                                    <p className="text-sandbox-300 text-xs font-bold uppercase tracking-widest mb-1">Application for</p>
                                    <h2 className="text-2xl font-bold">{selectedJob.title}</h2>
                                    <p className="text-white/70 text-sm mt-1">{selectedJob.company}</p>
                                </div>
                            </div>

                            <form
                                onSubmit={(e) => {
                                    e.preventDefault();
                                    const formData = new FormData(e.currentTarget);
                                    const data: any = {};
                                    formData.forEach((value, key) => data[key] = value);
                                    handleSubmitApplication(data as ApplicationForm);
                                }}
                                className="p-8 space-y-6"
                            >
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                                    <div className="space-y-1.5">
                                        <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Full Name</label>
                                        <input
                                            name="applicant_name"
                                            required
                                            className="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2.5 outline-none focus:ring-2 focus:ring-sandbox-500 focus:bg-white transition-all"
                                            placeholder="John Doe"
                                        />
                                    </div>
                                    <div className="space-y-1.5">
                                        <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Email Address</label>
                                        <input
                                            name="email"
                                            type="email"
                                            required
                                            className="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2.5 outline-none focus:ring-2 focus:ring-sandbox-500 focus:bg-white transition-all"
                                            placeholder="john@example.com"
                                        />
                                    </div>
                                </div>

                                <div className="space-y-1.5">
                                    <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Upload Resume (PDF/DOCX)</label>
                                    <div className="relative group">
                                        <input
                                            type="file"
                                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                                            onChange={(e) => setResumeFile(e.target.files?.[0]?.name || null)}
                                        />
                                        <div className={`w-full border-2 border-dashed rounded-xl p-6 text-center transition-all ${resumeFile ? 'border-green-300 bg-green-50' : 'border-gray-200 bg-gray-50 group-hover:border-sandbox-300'}`}>
                                            <Upload size={24} className={`mx-auto mb-2 ${resumeFile ? 'text-green-500' : 'text-gray-400 group-hover:text-sandbox-500'}`} />
                                            <p className={`text-sm font-medium ${resumeFile ? 'text-green-700' : 'text-gray-500'}`}>
                                                {resumeFile || 'Drag & drop or click to upload resume'}
                                            </p>
                                            <p className="text-[10px] text-gray-400 mt-1 uppercase tracking-tighter">Mock field: File stays on your device</p>
                                        </div>
                                    </div>
                                </div>

                                <div className="space-y-1.5">
                                    <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Brief Resume Text</label>
                                    <textarea
                                        name="resume_text"
                                        rows={4}
                                        required
                                        className="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 outline-none focus:ring-2 focus:ring-sandbox-500 focus:bg-white transition-all"
                                        placeholder="Paste your professional summary or key skills here..."
                                    ></textarea>
                                </div>

                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                                    <div className="space-y-1.5">
                                        <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Work Authorization</label>
                                        <select
                                            name="work_authorization"
                                            required
                                            className="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2.5 outline-none focus:ring-2 focus:ring-sandbox-500 focus:bg-white transition-all"
                                        >
                                            <option value="US Citizen/Permanent Resident">US Citizen / Green Card</option>
                                            <option value="Visa Required">Visa Required (F-1/H1-B)</option>
                                            <option value="Other">Other</option>
                                        </select>
                                    </div>
                                    <div className="space-y-1.5">
                                        <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Availability</label>
                                        <input
                                            name="availability"
                                            required
                                            placeholder="Immediately / 2 weeks notice"
                                            className="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2.5 outline-none focus:ring-2 focus:ring-sandbox-500 focus:bg-white transition-all"
                                        />
                                    </div>
                                </div>

                                <button
                                    type="submit"
                                    disabled={submitting}
                                    className="w-full bg-sandbox-600 text-white py-4 rounded-xl font-bold hover:bg-sandbox-700 transition-all shadow-lg shadow-sandbox-100 flex items-center justify-center gap-3 disabled:opacity-50"
                                >
                                    {submitting ? (
                                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                    ) : (
                                        <>Finalize & Submit Application <ArrowRight size={18} /></>
                                    )}
                                </button>

                                <p className="text-[10px] text-gray-400 text-center uppercase tracking-widest leading-relaxed">
                                    Submission will be transmitted to the Sandbox API on port 8001. <br /> Authentication verified via X-API-Key.
                                </p>
                            </form>
                        </div>
                    </div>
                ) : view === 'artifact_detail' && selectedApplication ? (
                    <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <button
                            onClick={() => setView('admin')}
                            className="bg-white border border-gray-200 px-4 py-2 rounded-lg text-sm font-medium text-gray-600 hover:text-gray-900 flex items-center gap-2"
                        >
                            &larr; Back to Feed
                        </button>

                        <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden">
                            <div className="bg-gray-900 p-8 text-white">
                                <span className="bg-green-500 text-black text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider mb-2 inline-block">
                                    {selectedApplication.status}
                                </span>
                                <h2 className="text-2xl font-bold font-mono">Artifact Block: {selectedApplication.id}</h2>
                                <p className="text-white/60 font-mono text-sm mt-1">
                                    Received: {new Date(selectedApplication.submitted_at).toLocaleString()}
                                </p>
                            </div>

                            <div className="p-8 space-y-8">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                    <div>
                                        <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-4">Applicant Data</h3>
                                        <dl className="space-y-3 text-sm">
                                            <div>
                                                <dt className="text-gray-500">Name</dt>
                                                <dd className="font-medium text-gray-900">{selectedApplication.applicant?.applicant_name}</dd>
                                            </div>
                                            <div>
                                                <dt className="text-gray-500">Email</dt>
                                                <dd className="font-medium text-gray-900">{selectedApplication.applicant?.email}</dd>
                                            </div>
                                            <div>
                                                <dt className="text-gray-500">Phone</dt>
                                                <dd className="font-medium text-gray-900">{selectedApplication.applicant?.phone}</dd>
                                            </div>
                                            <div>
                                                <dt className="text-gray-500">Work Auth</dt>
                                                <dd className="font-medium text-gray-900">{selectedApplication.applicant?.work_authorization}</dd>
                                            </div>
                                            <div>
                                                <dt className="text-gray-500">Availability</dt>
                                                <dd className="font-medium text-gray-900">{selectedApplication.applicant?.availability}</dd>
                                            </div>
                                        </dl>
                                    </div>
                                    <div>
                                        <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-4">Target Role</h3>
                                        <div className="bg-gray-50 p-4 rounded-xl border border-gray-100">
                                            <p className="font-bold text-gray-900 text-lg">{selectedApplication.job_title}</p>
                                            <div className="flex items-center gap-2 text-sandbox-600 font-medium text-sm mt-1">
                                                <Briefcase size={14} />
                                                {selectedApplication.company}
                                            </div>
                                            <p className="text-xs text-gray-400 font-mono mt-3">Job ID: {selectedApplication.job_id}</p>
                                        </div>
                                    </div>
                                </div>

                                <div className="border-t border-gray-100 pt-8">
                                    <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-4">Tailored Resume Artifact</h3>
                                    <div className="bg-gray-50 rounded-xl p-6 font-mono text-xs text-gray-600 whitespace-pre-wrap border border-gray-200 shadow-inner h-96 overflow-y-auto">
                                        {selectedApplication.applicant?.resume_text}
                                    </div>
                                </div>

                                {selectedApplication.applicant?.cover_letter && (
                                    <div className="border-t border-gray-100 pt-8">
                                        <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-4">Cover Letter Artifact</h3>
                                        <div className="bg-white rounded-xl p-8 border border-gray-200 shadow-sm text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                                            {selectedApplication.applicant?.cover_letter}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                ) : (
                    /* Admin View / Applications Log */
                    <div className="space-y-6">
                        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
                            <div className="bg-gray-50 px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                                <div>
                                    <h2 className="text-lg font-bold text-gray-900">Application Feed (Incoming)</h2>
                                    <p className="text-sm text-gray-500">Watch your autonomous agent submit applications to port 8001.</p>
                                </div>
                                <div className="flex items-center gap-2 text-sm font-medium text-green-600 bg-green-50 px-3 py-1.5 rounded-lg border border-green-100">
                                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                                    Live Updates Active
                                </div>
                            </div>

                            <div className="divide-y divide-gray-100">
                                {applications.length === 0 ? (
                                    <div className="p-12 text-center">
                                        <div className="bg-gray-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                                            <ShieldCheck size={32} className="text-gray-400" />
                                        </div>
                                        <h3 className="text-lg font-semibold text-gray-900">No applications received yet</h3>
                                        <p className="text-gray-500 max-w-sm mx-auto mt-2">
                                            Start your Agent in the main dashboard to see entries appear here in real-time.
                                        </p>
                                    </div>
                                ) : (
                                    [...applications].reverse().map(app => (
                                        <div key={app.id} className="p-6 hover:bg-gray-50 transition-colors border-l-4 border-green-500">
                                            <div className="flex justify-between items-center">
                                                <div className="flex-1">
                                                    <div className="flex items-center gap-2 mb-1">
                                                        <span className="text-xs font-mono text-gray-400">ID: {app.id.substring(0, 8)}</span>
                                                        <span className="text-xs text-gray-400">•</span>
                                                        <span className="text-xs text-gray-400">Received at {new Date(app.submitted_at).toLocaleTimeString()}</span>
                                                    </div>
                                                    <h4 className="text-lg font-bold text-gray-900">
                                                        {app.applicant?.applicant_name || 'Anonymous Submission'}
                                                    </h4>
                                                    <p className="text-sandbox-700 font-medium">
                                                        Applied for <span className="text-gray-900 font-semibold">{app.job_title}</span> at {app.company}
                                                    </p>
                                                </div>
                                                <div className="flex flex-col items-end gap-3">
                                                    <div className="flex items-center gap-1.5 bg-green-100 text-green-800 px-3 py-1 rounded-full text-xs font-bold uppercase">
                                                        <CheckCircle size={14} />
                                                        {app.status}
                                                    </div>
                                                    <div className="flex items-center gap-2">
                                                        <button
                                                            onClick={() => {
                                                                setSelectedApplication(app);
                                                                setView('artifact_detail');
                                                            }}
                                                            className="text-xs text-sandbox-600 hover:text-sandbox-800 font-semibold underline underline-offset-4"
                                                        >
                                                            View Full Artifact Block
                                                        </button>
                                                        <button
                                                            onClick={() => handleDeleteApplication(app.id)}
                                                            className="p-1.5 text-red-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                                            title="Delete application"
                                                        >
                                                            <Trash2 size={16} />
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="mt-4 bg-gray-900 rounded-lg p-3 overflow-hidden">
                                                <div className="text-[10px] text-sandbox-400 uppercase font-bold tracking-widest mb-2 opacity-50">Transmitted Skills</div>
                                                <div className="flex flex-wrap gap-1.5">
                                                    {(app.applicant?.resume_text?.substring(0, 100) || '').split(' ').slice(0, 8).map((word: string, i: number) => (
                                                        <span key={i} className="text-[10px] text-white/70 bg-white/10 px-1.5 py-0.5 rounded">
                                                            {word.replace(/[^a-zA-Z]/g, '')}
                                                        </span>
                                                    ))}
                                                    <span className="text-[10px] text-white/30 px-1.5 py-0.5">... [Grounding Verified Artifact]</span>
                                                </div>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </main>

            {/* Footer */}
            <footer className="bg-white border-t border-gray-200 py-8 text-center text-sm text-gray-400">
                <div className="mb-2 uppercase tracking-widest text-[10px] font-bold">Sandbox Environment</div>
                <p>&copy; 2026 SandboxPortal • Simulated Job Application Flow</p>
            </footer>
        </div>
    )
}

export default App
