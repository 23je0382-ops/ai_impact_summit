
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
    ArrowRight
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
    posted_date: string
    skills_required: string[]
    is_remote: boolean
}

interface Application {
    id: string
    job_id: string
    job_title: string
    company: string
    submitted_at: string
    status: string
    applicant: any
}

function App() {
    const [jobs, setJobs] = useState<Job[]>([])
    const [applications, setApplications] = useState<Application[]>([])
    const [loading, setLoading] = useState(true)
    const [searchTerm, setSearchTerm] = useState('')
    const [view, setView] = useState<'public' | 'admin'>('public')

    const fetchJobs = async () => {
        try {
            const res = await axios.get(`${SANDBOX_API}/sandbox/jobs`)
            setJobs(res.data.jobs)
        } catch (err) {
            console.error('Failed to fetch jobs', err)
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

    useEffect(() => {
        const init = async () => {
            setLoading(true)
            await fetchJobs()
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
                                className={`text-sm font-medium ${view === 'public' ? 'text-sandbox-600' : 'text-gray-500 hover:text-gray-900'}`}
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
                                        <button className="bg-sandbox-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-sandbox-700 transition-colors flex items-center gap-2">
                                            Apply Now <ArrowRight size={14} />
                                        </button>
                                    </div>
                                </div>
                            ))}
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
                                                    <button className="text-xs text-sandbox-600 hover:text-sandbox-800 font-semibold underline underline-offset-4">
                                                        View Full Artifact Block
                                                    </button>
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
