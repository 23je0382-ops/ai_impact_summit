
# System Architecture

## Overview
The **AI Job Impact Agent** is an autonomous system designed to scale job applications while maintaining high personalization and safety standards. It employs a micro-service architecture (monorepo) with a React frontend and a FastAPI python backend.

## System Components

```mermaid
graph TD
    subgraph "Frontend Layer"
        UI[React Dashboard]
        Tracker[Application Tracker]
        Pack[Artifact Pack Manager]
    end

    subgraph "Backend API (FastAPI)"
        API[API Router]
        
        subgraph "Autonomous Engine"
            Ranker[Job Ranker]
            Batch[Batch Processor]
            Assembler[Application Assembler]
        end
        
        subgraph "Generation Services"
            Tailor[Resume Tailor]
            Cover[Cover Letter Gen]
            Answers[Answer Library]
        end
        
        subgraph "Safety & Control"
            Verifier[Grounding Verifier]
            Policy[Policy Engine]
            Audit[Audit Logger]
        end
    end

    subgraph "Data Persistence"
        Store[JSON Data Store]
        Logs[Audit Logs]
    end

    UI --> API
    API --> Ranker
    API --> Batch
    
    Batch --> Policy
    Batch --> Assembler
    Assembler --> Tailor
    Assembler --> Cover
    Assembler --> Answers
    
    Tailor --> Verifier
    Cover --> Verifier
    
    Verifier --> Audit
    Batch --> Audit
    
    Backend --> Store
    Backend --> Logs
```

## Data Flow Architecture

The data flows through a linear pipeline designed to ensure consistency and personalization.

```mermaid
sequenceDiagram
    participant User
    participant Profile as Student Profile
    participant Search as Job Search/Ranker
    participant Queue as Apply Queue
    participant Assembly as App Assembler
    participant Safety as Grounding/Policy
    participant External as Job Portal

    User->>Profile: Updates Resume & Artifacts
    Profile->>Search: Provides Skills/Experience
    Search->>Queue: Pushes Top Ranked Jobs
    
    loop Batch Processor
        Queue->>Assembly: Dequeue Job
        Assembly->>Safety: Check Policy (Limit/Blocklist)
        alt Policy Passed
            Assembly->>Assembly: Tailor Resume & Cover Letter
            Assembly->>Safety: Verify Grounding (Anti-Hallucination)
            alt Grounding Passed
                Assembly->>External: Submit Application
                External-->>Assembly: Receipt
            else Hallucination Detected
                Assembly->>User: Flag & Revert
            end
        else Policy Blocked
            Safety->>Queue: Skip & Log
        end
    end
```

## Core Subsystems

### 1. Autonomous Engine
- **Job Ranker**: Scores incoming job listings against the student profile using a weighted algorithm (Skills 40%, Experience 30%, Constraints 30%) and LLM-based reasoning.
- **Batch Processor**: A background worker that processes the job queue, respecting rate limits and pacing (slower/faster based on response types).

### 2. Generation & Tailoring
- **Resume Tailor**: Re-orders and rewords existing bullet points (using STAR method) to check keywords from the job description.
- **Answer Library**: Maintains a cache of reusable, modular behavioral answers ("Why this company?", "Strengths") that are dynamically injected.

### 3. Safety Layer
See [GROUNDING_SAFETY.md](./GROUNDING_SAFETY.md) for details on Hallucination prevention and Policy enforcement.

## Technology Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Backend** | Python (FastAPI) | High performance, native async support for IO-bound submission tasks, rich AI/LLM ecosystem. |
| **Frontend** | React + TypeScript | Type safety, component modularity, and rapid UI development with Tailwind CSS styling. |
| **LLM** | Groq (Llama-3) | Extremely low latency inference essential for "real-time" tailoring of 50+ applications. |
| **Persistence** | Local JSON | Portable, zero-setup data store ideal for single-user autonomous agents. Thread-locked for concurrency. |
| **State** | Zustand | Lightweight global state management for the frontend without the boilerplate of Redux. |
