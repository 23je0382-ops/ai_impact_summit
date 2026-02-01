
import React, { Component, ErrorInfo, ReactNode } from 'react'

interface Props {
    children: ReactNode
}

interface State {
    hasError: boolean
    error: Error | null
    errorInfo: ErrorInfo | null
}

export class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: null,
        errorInfo: null
    }

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error, errorInfo: null }
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('Uncaught error:', error, errorInfo)
        this.setState({ error, errorInfo })
    }

    public render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
                    <div className="max-w-md w-full space-y-8 text-center">
                        <div className="rounded-md bg-red-50 p-4 border border-red-200">
                            <h2 className="text-xl font-bold text-red-800 mb-2">Something went wrong</h2>
                            <p className="text-sm text-red-700 mb-4">
                                {this.state.error?.message || 'An unexpected error occurred.'}
                            </p>
                            <button
                                onClick={() => window.location.reload()}
                                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                            >
                                Reload Page
                            </button>
                            {/* <details className="mt-4 text-left text-xs text-gray-500 overflow-auto max-h-40">
                                {this.state.errorInfo?.componentStack}
                            </details> */}
                        </div>
                    </div>
                </div>
            )
        }

        return this.props.children
    }
}
