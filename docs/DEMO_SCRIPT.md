
# 5-Minute Demo Video Script

**Goal**: Showcase the full autonomous loop of the AI Job Agent.
**Persona**: "Arjun", a CS student applying for internships/new grad roles.

## [0:00 - 0:30] Introduction & Problem
**Visual**: Face camera or Title Slide "AI Agent: Autonomous Job Application System".
**Talking Points**:
- "Hi, I'm [Name]. We've built an autonomous agent that solves the biggest pain point for students today: The 'Black Hole' of job applications."
- "Students spend hundreds of hours manually tweaking resumes and filling forms, often with little success."
- "Our system automates this entire pipeline—from finding jobs to tailoring resumes and submitting applications—while ensuring safety and personalization at scale."

## [0:30 - 1:00] Step 1: Profile & Artifact Generation
**Visual**: `ArtifactPackPage` (/artifact-pack). Show "Arjun's" profile loaded.
**Action**: Scroll through the profile. Show the "Generate Artifact Pack" status (already done or click if fast).
**Talking Points**:
- "It starts with the Student Profile. Here we have Arjun's history: his internships at Swiggy, his projects, and skills."
- "The agent takes this raw data and generates a 'Proof Pack': Master resume bullets, verified evidence, and reusable behavioral answers."
- "This isn't just a template; it's a structured knowledge base about the candidate."

## [1:00 - 2:00] Step 2: Intelligent Search & Ranking
**Visual**: `JobSearchPage` (/job-search).
**Action**: Click "Refresh Jobs" (simulated). Scroll through the list. Point out the "Match Score".
**Talking Points**:
- "Next, the agent scans the job market. We've seeded 50+ real-world listings here."
- "Notice the 'Match Score'. The agent doesn't just look for keywords. It uses an LLM to read the job description and compare it against Arjun's specific experiences."
- "It prioritizes roles like 'Backend Engineer' at 'Swiggy' because of his internship match, while deprioritizing misalignment roles."

## [2:00 - 3:00] Step 3: Queue & Policy Controls
**Visual**: `ApplyQueuePage` (/apply/queue) and dashboard settings.
**Action**: Show the top 15 jobs in the queue. Open "Policy Settings" modal/view.
**Talking Points**:
- "The best jobs go into the Apply Queue."
- "Before we let the agent loose, we set the Rules of Engagement via the Policy Engine found in the Dashboard."
- "We can set a Daily Limit (e.g., 25 apps), block specific companies, or enforce 'Remote Only'."
- "This ensures the agent works *for* you, not randomly."

## [3:00 - 4:00] Step 4: Autonomous Execution (The "Magic")
**Visual**: `ApplyQueuePage`.
**Action**: Click "Start Batches". Watch the status bubbles change (Assembling -> Submitting).
**Talking Points**:
- "Now, I click Start. The agent takes over."
- "Watch closely. For each job, it is: 1) Loading the specific job requirements. 2) Tailoring Arjun's resume to highlight relevant skills. 3) Generating a custom cover letter."
- "It's doing this in real-time. If I click 'Stop', it halts immediately. But let's let it run for a few applications."
- (Let it process 3-4 jobs).

## [4:00 - 4:30] Step 5: Tracker Dashboard
**Visual**: `TrackerPage` (/tracker).
**Action**: Show the table filling up with "Submitted" status.
**Talking Points**:
- "Let's switch to the Application Tracker."
- "Here is the live feed. We can see 5 applications submitted in the last minute."
- "No manual data entry. It tracks the status, the role, and the date automatically."

## [4:30 - 5:00] Step 6: Audit & Verification
**Visual**: Click the "Audit" (magnifying glass) icon on a row in Tracker. Show the Modal timeline.
**Action**: Scroll down the timeline. Point to "Verification".
**Talking Points**:
- "But how do we trust it? That's where the Audit Trail comes in."
- "I can click any application to see EXACTLY what happened."
- "Here, you see the 'Snapshot' of data used. And here, in green, is the 'Grounding Verification'."
- "The system checked the generated text against Arjun's profile to prevent hallucinations. If it tried to lie, this check would fail."
- "This is Autonomous AI with built-in integrity."

## [End]
**Visual**: Face camera.
**Talking Points**:
- "That is the AI Job Impact Agent. Scaling your career search without losing your personal touch. Thank you."
