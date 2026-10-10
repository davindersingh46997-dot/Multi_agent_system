import { useMemo, useState } from "react";
import {
    FiActivity,
    FiAlertCircle,
    FiArrowDown,
    FiArrowRight,
    FiBell,
    FiCheck,
    FiCheckCircle,
    FiChevronDown,
    FiChevronRight,
    FiClock,
    FiCode,
    FiCpu,
    FiFile,
    FiFileText,
    FiGitBranch,
    FiGitPullRequest,
    FiLayers,
    FiMessageSquare,
    FiMoreHorizontal,
    FiPause,
    FiPlay,
    FiPlus,
    FiSearch,
    FiShield,
    FiTerminal,
    FiUploadCloud,
    FiUsers,
    FiX,
    FiZap,
} from "react-icons/fi";
import "./agentic_workspace.css";

type Section = "workspace" | "tasks" | "agents" | "activity";
type TaskStatus = "In progress" | "Awaiting approval" | "Completed" | "Queued";
type AgentStatus = "working" | "done" | "waiting";

interface DemoTask {
    id: string;
    title: string;
    status: TaskStatus;
    time: string;
    description: string;
}

interface Agent {
    name: string;
    role: string;
    initials: string;
    color: string;
    status: AgentStatus;
    detail: string;
}

const initialTasks: DemoTask[] = [
    {
        id: "run-248",
        title: "Add OAuth refresh token rotation",
        status: "Awaiting approval",
        time: "4 min ago",
        description: "Implement secure refresh token rotation and revoke reused tokens.",
    },
    {
        id: "run-247",
        title: "Fix dashboard loading state",
        status: "Completed",
        time: "Yesterday",
        description: "Resolve the skeleton flash when dashboard data is already cached.",
    },
    {
        id: "run-246",
        title: "Add pagination to activity feed",
        status: "Completed",
        time: "Yesterday",
        description: "Add cursor-based pagination for the activity feed endpoint.",
    },
];

const initialAgents: Agent[] = [
    {
        name: "Repository analyst",
        role: "Finding context",
        initials: "RA",
        color: "mint",
        status: "done",
        detail: "Indexed 42 files · 6 relevant matches",
    },
    {
        name: "Planner",
        role: "Plan ready",
        initials: "PL",
        color: "blue",
        status: "done",
        detail: "4 implementation steps · 2 dependencies",
    },
    {
        name: "Coding agent",
        role: "Implementing changes",
        initials: "CA",
        color: "violet",
        status: "working",
        detail: "Editing auth/refresh.ts",
    },
    {
        name: "Testing agent",
        role: "Waiting for changes",
        initials: "TA",
        color: "amber",
        status: "waiting",
        detail: "Unit and integration checks",
    },
    {
        name: "Debugging agent",
        role: "Available for failures",
        initials: "DB",
        color: "blue",
        status: "waiting",
        detail: "Diagnose failures and suggest minimal repairs",
    },
    {
        name: "Reviewer",
        role: "Waiting for changes",
        initials: "RV",
        color: "pink",
        status: "waiting",
        detail: "Diff, regression, and security review",
    },
];

const activityItems = [
    { time: "10:42:18", title: "Coding agent updated auth/refresh.ts", kind: "code" },
    { time: "10:41:52", title: "Planner created a 4-step implementation plan", kind: "plan" },
    { time: "10:41:09", title: "Repository analyst found 6 relevant files", kind: "search" },
    { time: "10:40:31", title: "Task started from your request", kind: "start" },
];

const diffRows = [
    { type: "context", number: "18", text: "export async function rotateRefreshToken(token: string) {" },
    { type: "remove", number: "19", text: "  const session = await sessions.findByToken(token);" },
    { type: "add", number: "19", text: "  const session = await sessions.consumeRefreshToken(token);" },
    { type: "add", number: "20", text: "  if (!session) throw new InvalidRefreshTokenError();" },
    { type: "context", number: "21", text: "  return issueTokenPair(session.userId);" },
    { type: "context", number: "22", text: "}" },
];

const sectionTitles: Record<Section, { eyebrow: string; title: string; description: string }> = {
    workspace: {
        eyebrow: "DEVELOPMENT WORKSPACE",
        title: "What are we building today?",
        description: "Describe the outcome. Your agent team will inspect, plan, implement, and validate it.",
    },
    tasks: {
        eyebrow: "TASK HISTORY",
        title: "Runs & task history",
        description: "Pick up where you left off and review the state of every coding run.",
    },
    agents: {
        eyebrow: "YOUR AGENT TEAM",
        title: "Specialists, working together",
        description: "Each agent has a focused role, bounded tools, and a shared task context.",
    },
    activity: {
        eyebrow: "WORKSPACE ACTIVITY",
        title: "A clear trail of every action",
        description: "Follow task events, agent hand-offs, approvals, and validation outcomes.",
    },
};

function statusClass(status: TaskStatus) {
    if (status === "Completed") return "status-completed";
    if (status === "Awaiting approval") return "status-approval";
    if (status === "Queued") return "status-queued";
    return "status-progress";
}

function AgentAvatar({ agent, small = false }: { agent: Agent; small?: boolean }) {
    return (
        <span className={`agent-avatar avatar-${agent.color}${small ? " avatar-small" : ""}`}>
            {agent.initials}
        </span>
    );
}

function AgentStatusIcon({ status }: { status: AgentStatus }) {
    if (status === "done") return <FiCheck size={13} />;
    if (status === "working") return <span className="status-spinner" />;
    return <FiClock size={12} />;
}

function AgenticWorkspace() {
    const [section, setSection] = useState<Section>("workspace");
    const [project, setProject] = useState("acme-platform");
    const [prompt, setPrompt] = useState("");
    const [tasks, setTasks] = useState(initialTasks);
    const [selectedTaskId, setSelectedTaskId] = useState("run-248");
    const [activeTab, setActiveTab] = useState<"overview" | "changes" | "checks">("overview");
    const [approved, setApproved] = useState(false);
    const [paused, setPaused] = useState(false);
    const [toast, setToast] = useState("");
    const [showProjectMenu, setShowProjectMenu] = useState(false);
    const [searchTerm, setSearchTerm] = useState("");

    const selectedTask = tasks.find((task) => task.id === selectedTaskId) ?? tasks[0];
    const filteredTasks = useMemo(
        () => tasks.filter((task) => task.title.toLowerCase().includes(searchTerm.toLowerCase())),
        [searchTerm, tasks],
    );
    const header = sectionTitles[section];
    const isQueued = selectedTask.status === "Queued";
    const isCompleted = selectedTask.status === "Completed";

    const notify = (message: string) => {
        setToast(message);
        window.setTimeout(() => setToast(""), 3600);
    };

    const startTask = () => {
        const title = prompt.trim();
        if (!title) {
            notify("Describe the change you want to make first.");
            return;
        }
        const task: DemoTask = {
            id: `local-${Date.now()}`,
            title,
            status: "Queued",
            time: "Just now",
            description: title,
        };
        setTasks((current) => [task, ...current]);
        setSelectedTaskId(task.id);
        setSection("workspace");
        setPrompt("");
        setActiveTab("overview");
        setApproved(false);
        setPaused(false);
        notify("Added to this UI preview. No backend task was created.");
    };

    const decideApproval = () => {
        setApproved((current) => !current);
        if (!approved) {
            setTasks((current) => current.map((task) => (
                task.id === selectedTaskId ? { ...task, status: "Completed" } : task
            )));
            notify("Approval recorded in this preview only. No files were changed.");
        } else {
            setTasks((current) => current.map((task) => (
                task.id === selectedTaskId ? { ...task, status: "Awaiting approval" } : task
            )));
            notify("Approval reset in this preview.");
        }
    };

    const createNewTask = () => {
        setSection("workspace");
        setSelectedTaskId(tasks[0]?.id ?? "");
        setPrompt("");
        setActiveTab("overview");
    };

    const renderAgentStrip = () => (
        <div className="agent-strip">
            <div className="agent-strip-heading">
                <div>
                    <span className="section-kicker">AGENT TEAM</span>
                    <span className="agent-count">06 specialists</span>
                </div>
                <button className="quiet-button" onClick={() => setSection("agents")}>
                    Team details <FiArrowRight size={13} />
                </button>
            </div>
            <div className="agent-list">
                {initialAgents.map((agent) => (
                    <div className="agent-row" key={agent.initials}>
                        <AgentAvatar agent={agent} />
                        <div className="agent-copy">
                            <strong>{agent.name}</strong>
                            <span>{agent.detail}</span>
                        </div>
                        <span className={`agent-state state-${agent.status}`}>
                            <AgentStatusIcon status={agent.status} />
                            <span>{agent.status === "done" ? "Ready" : agent.status === "working" ? "Working" : "Queued"}</span>
                        </span>
                    </div>
                ))}
            </div>
            <div className="agent-strip-footer">
                <FiShield size={14} />
                <span>Agents are scoped to this task and project.</span>
                <button aria-label="Learn about agent permissions" onClick={() => notify("Tool permissions and access are shown here in the connected product.")}>
                    Learn more
                </button>
            </div>
        </div>
    );

    const renderTaskCard = (task: DemoTask, compact = false) => (
        <button
            className={`task-card${compact ? " task-card-compact" : ""}${task.id === selectedTaskId ? " task-card-selected" : ""}`}
            key={task.id}
            onClick={() => {
                setSelectedTaskId(task.id);
                setApproved(task.status === "Completed" && task.id === selectedTaskId);
                setActiveTab("overview");
                setSection("workspace");
            }}
        >
            <div className="task-card-top">
                <span className={`task-status ${statusClass(task.status)}`}>
                    <span className="status-dot" />
                    {task.status}
                </span>
                <span className="task-time">{task.time}</span>
            </div>
            <strong>{task.title}</strong>
            {!compact && <p>{task.description}</p>}
            <span className="task-card-bottom">
                <span className="task-id">{task.id.toUpperCase()}</span>
                <span className="mini-avatars">
                    {initialAgents.slice(0, 3).map((agent) => (
                        <AgentAvatar key={agent.initials} agent={agent} small />
                    ))}
                    <span className="mini-avatar-more">+3</span>
                </span>
            </span>
        </button>
    );

    const renderWorkspace = () => (
        <>
            <section className="welcome-section">
                <div className="welcome-copy">
                    <div className="eyebrow"><span className="eyebrow-line" />{header.eyebrow}</div>
                    <h1>{header.title}</h1>
                    <p>{header.description}</p>
                </div>
                <div className="workspace-summary">
                    <div className="summary-orbit"><FiZap size={18} /></div>
                    <div><strong>6 agents</strong><span>Ready to collaborate</span></div>
                </div>
            </section>

            <section className="composer-panel" aria-label="Create a coding task">
                <div className="composer-topline">
                    <span className="composer-icon"><FiMessageSquare size={16} /></span>
                    <span>NEW DEVELOPMENT TASK</span>
                    <span className="local-preview-pill">LOCAL UI PREVIEW</span>
                </div>
                <label className="visually-hidden" htmlFor="task-prompt">Describe a coding task</label>
                <textarea
                    id="task-prompt"
                    value={prompt}
                    onChange={(event) => setPrompt(event.target.value)}
                    onKeyDown={(event) => {
                        if ((event.ctrlKey || event.metaKey) && event.key === "Enter") startTask();
                    }}
                    placeholder="Describe a feature, bug fix, or refactor…"
                    rows={3}
                />
                <div className="composer-toolbar">
                    <div className="composer-tools">
                        <button className="tool-button" onClick={() => notify("File attachments are part of the connected product flow.")}>
                            <FiUploadCloud size={15} /> <span>Attach context</span>
                        </button>
                        <span className="toolbar-divider" />
                        <button className="tool-button" onClick={() => notify("Repository context will be selected from the project workspace.")}>
                            <FiLayers size={15} /> <span>Repository context</span>
                        </button>
                    </div>
                    <div className="composer-submit-row">
                        <span className="shortcut-hint">⌘ + Enter</span>
                        <button className="launch-button" onClick={startTask}>
                            <FiZap size={15} /> Start agent run <FiArrowRight size={14} />
                        </button>
                    </div>
                </div>
            </section>

            <div className="workspace-columns">
                <div className="workspace-primary">
                    <section className="active-run-section">
                        <div className="section-heading">
                            <div>
                                <span className="section-kicker">IN FOCUS</span>
                                <h2>Active workspace run</h2>
                            </div>
                            <button className="quiet-button" onClick={() => setSection("tasks")}>
                                All tasks <FiArrowRight size={13} />
                            </button>
                        </div>
                        <article className="run-panel">
                            <div className="run-panel-header">
                                <div className="run-title-wrap">
                                    <span className="run-icon"><FiGitBranch size={15} /></span>
                                    <div>
                                        <span className="run-label">{selectedTask.id.toUpperCase()} <span className="tiny-separator">·</span> {project}</span>
                                        <h3>{selectedTask.title}</h3>
                                    </div>
                                </div>
                                <span className={`task-status ${statusClass(selectedTask.status)}`}>
                                    <span className="status-dot" />{selectedTask.status}
                                </span>
                            </div>

                            <div className="run-progress">
                                <div className="progress-track"><span style={{ width: isQueued ? "0%" : isCompleted || approved ? "100%" : "68%" }} /></div>
                                <div className="progress-meta">
                                    <span><FiActivity size={13} /> {isQueued ? "Queued locally — waiting to start" : isCompleted ? "Task complete in preview" : approved ? "Review approved in preview" : paused ? "Run paused" : "Coding agent is implementing"}</span>
                                    <span>{isQueued ? "0 / 5" : isCompleted || approved ? "5 / 5" : paused ? "Paused" : "3 / 5"} stages</span>
                                </div>
                            </div>

                            <div className="workflow-steps">
                                {[
                                    { label: "Analyze", icon: <FiSearch size={14} />, state: isQueued ? "step-waiting" : "step-done" },
                                    { label: "Plan", icon: <FiLayers size={14} />, state: isQueued ? "step-waiting" : "step-done" },
                                    { label: "Implement", icon: <FiCode size={14} />, state: isQueued ? "step-waiting" : isCompleted || approved ? "step-done" : paused ? "step-paused" : "step-current" },
                                    { label: "Validate", icon: <FiCheckCircle size={14} />, state: isQueued || !isCompleted && !approved ? "step-waiting" : "step-done" },
                                    { label: "Review", icon: <FiShield size={14} />, state: isQueued || !isCompleted && !approved ? "step-waiting" : "step-done" },
                                ].map((step, index) => (
                                    <div className={`workflow-step ${step.state}`} key={step.label}>
                                        <span className="step-marker">{step.icon}</span>
                                        <span>{step.label}</span>
                                        {index < 4 && <span className="step-connector" />}
                                    </div>
                                ))}
                            </div>

                            <div className="run-tabs" role="tablist" aria-label="Task details">
                                {(["overview", "changes", "checks"] as const).map((tab) => (
                                    <button
                                        className={activeTab === tab ? "run-tab active" : "run-tab"}
                                        key={tab}
                                        onClick={() => setActiveTab(tab)}
                                        role="tab"
                                        aria-selected={activeTab === tab}
                                    >
                                        {tab === "overview" ? "Overview" : tab === "changes" ? "Changes" : "Checks"}
                                        {tab === "changes" && <span className="tab-count">2</span>}
                                    </button>
                                ))}
                                <button className="icon-button run-more" aria-label="More run actions" onClick={() => notify("Run actions are available in the connected application.")}>
                                    <FiMoreHorizontal size={17} />
                                </button>
                            </div>

                            {activeTab === "overview" && (
                                <div className="overview-content">
                                    <div className="plan-card">
                                        <div className="plan-card-heading">
                                            <span className="plan-icon"><FiFileText size={14} /></span>
                                            <div><strong>Implementation plan</strong><span>Prepared by Planner · just now</span></div>
                                            <button className="text-link" onClick={() => notify("This preview is showing a sample plan.")}>View plan <FiArrowRight size={12} /></button>
                                        </div>
                                        <ol className="plan-list">
                                            <li><span>1</span><div><strong>Review the current token lifecycle</strong><small>auth/session.ts · auth/refresh.ts</small></div><FiCheck size={14} className="plan-done" /></li>
                                            <li><span>2</span><div><strong>Add single-use refresh token rotation</strong><small>Consume old token before issuing a replacement</small></div><span className="plan-current-dot" /></li>
                                            <li><span>3</span><div><strong>Cover reuse detection with tests</strong><small>Unit test · integration test</small></div><FiClock size={13} className="plan-pending" /></li>
                                        </ol>
                                    </div>
                                    <div className="latest-activity">
                                        <div className="latest-activity-head"><strong>Latest agent activity</strong><button className="text-link" onClick={() => setSection("activity")}>View log <FiArrowRight size={12} /></button></div>
                                        <div className="activity-inline">
                                            <AgentAvatar agent={initialAgents[2]} small />
                                            <div><strong>Coding agent <span>·</span> 12 sec ago</strong><p>Updating token consumption to be atomic and single-use.</p></div>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {activeTab === "changes" && (
                                <div className="changes-content">
                                    <div className="change-file-row">
                                        <div><FiFile size={14} /><strong>auth/refresh.ts</strong><span>+2 −1</span></div>
                                        <span className="change-review-state"><span className="status-dot" /> Review requested</span>
                                    </div>
                                    <div className="diff-block" aria-label="Sample code diff">
                                        {diffRows.map((row, index) => (
                                            <div className={`diff-row diff-${row.type}`} key={`${row.number}-${index}`}>
                                                <span className="diff-sign">{row.type === "add" ? "+" : row.type === "remove" ? "−" : " "}</span>
                                                <span className="diff-number">{row.number}</span>
                                                <code>{row.text}</code>
                                            </div>
                                        ))}
                                    </div>
                                    <div className="diff-disclaimer"><FiAlertCircle size={13} /> Sample diff for UI preview. No repository files have been read or changed.</div>
                                    <div className="approval-bar">
                                        <div><FiShield size={15} /><span>Review each change before applying</span></div>
                                        <button className={approved ? "approve-button approved" : "approve-button"} onClick={decideApproval}>
                                            {approved ? <><FiCheck size={14} /> Approved in preview</> : <><FiCheckCircle size={14} /> Approve changes</>}
                                        </button>
                                    </div>
                                </div>
                            )}

                            {activeTab === "checks" && (
                                <div className="checks-content">
                                    <div className="checks-summary">
                                        <span className="check-summary-icon"><FiClock size={15} /></span>
                                        <div><strong>Validation has not run yet</strong><span>Checks run in an isolated environment after implementation.</span></div>
                                        <span className="check-pending-pill">PENDING</span>
                                    </div>
                                    {[
                                        { name: "Unit tests", command: "pytest tests/auth", state: "Waiting" },
                                        { name: "Type check", command: "mypy brain/auth", state: "Waiting" },
                                        { name: "Security review", command: "Diff and dependency scan", state: "Waiting" },
                                    ].map((check) => (
                                        <div className="check-row" key={check.name}>
                                            <span className="check-row-icon"><FiTerminal size={14} /></span>
                                            <div><strong>{check.name}</strong><code>{check.command}</code></div>
                                            <span>{check.state}</span>
                                        </div>
                                    ))}
                                    <p className="checks-note">This preview never runs commands or reports sample checks as passing.</p>
                                </div>
                            )}

                            <div className="run-footer">
                                <div className="run-footer-meta"><FiClock size={13} /> Started 4 minutes ago <span>·</span> <FiGitBranch size={13} /> feature/refresh-rotation</div>
                                <div className="run-controls">
                                    <button className="outline-button" onClick={() => { setPaused((current) => !current); notify(paused ? "Run resumed in preview." : "Run paused in preview."); }}>
                                        {paused ? <FiPlay size={13} /> : <FiPause size={13} />}{paused ? "Resume" : "Pause"}
                                    </button>
                                    <button className="outline-button" onClick={() => notify("Cancellation is preview-only; no task is running.")}><FiX size={14} /> Cancel</button>
                                </div>
                            </div>
                        </article>
                    </section>

                    {renderAgentStrip()}
                </div>

                <aside className="workspace-aside">
                    <section className="aside-section repo-card">
                        <div className="aside-heading"><span className="section-kicker">PROJECT CONTEXT</span><button className="icon-button" aria-label="More project options" onClick={() => notify("Project settings will be available when connected.")}><FiMoreHorizontal size={16} /></button></div>
                        <div className="repo-title"><span className="repo-icon"><FiCode size={16} /></span><div><strong>{project}</strong><span>Private repository</span></div></div>
                        <div className="repo-meta-row"><span><FiGitBranch size={13} /> main</span><span className="repo-sync"><span className="status-dot" /> Synced</span></div>
                        <div className="repo-stats">
                            <div><strong>42</strong><span>Files indexed</span></div><div><strong>3m</strong><span>Last indexed</span></div>
                        </div>
                        <button className="repo-link" onClick={() => notify("Repository browsing is not connected in this UI-only implementation.")}>Browse repository <FiArrowRight size={13} /></button>
                    </section>

                    <section className="aside-section recent-section">
                        <div className="aside-heading"><span className="section-kicker">RECENT TASKS</span><button className="text-link" onClick={() => setSection("tasks")}>See all</button></div>
                        <div className="recent-task-list">
                            {tasks.slice(0, 3).map((task) => (
                                <button className="recent-task" key={task.id} onClick={() => { setSelectedTaskId(task.id); setSection("workspace"); }}>
                                    <span className={`recent-task-icon ${statusClass(task.status)}`}>{task.status === "Completed" ? <FiCheck size={13} /> : task.status === "Awaiting approval" ? <FiShield size={13} /> : <FiActivity size={13} />}</span>
                                    <span className="recent-task-copy"><strong>{task.title}</strong><small>{task.time}</small></span>
                                    <FiChevronRight className="recent-chevron" size={14} />
                                </button>
                            ))}
                        </div>
                    </section>

                    <section className="aside-section safety-card">
                        <div className="safety-icon"><FiShield size={15} /></div>
                        <div><strong>Human approval required</strong><p>Agents propose changes. You stay in control of what gets applied.</p></div>
                        <FiArrowDown className="safety-arrow" size={14} />
                    </section>

                    <section className="aside-section delivery-card">
                        <div className="aside-heading"><span className="section-kicker">GIT & DELIVERY</span><FiGitPullRequest size={14} /></div>
                        <div className="delivery-branch"><FiGitBranch size={13} /><span>feature/refresh-rotation</span></div>
                        <div className="delivery-status"><span className="delivery-status-icon"><FiCheck size={12} /></span><span><strong>Changes staged for review</strong><small>2 files · 48 additions · 12 deletions</small></span></div>
                        <button className="delivery-button" onClick={() => notify("Pull request preview only. No branch, commit, or PR was created.")}>Preview pull request <FiArrowRight size={13} /></button>
                    </section>

                    <section className="aside-section usage-card">
                        <div className="aside-heading"><span className="section-kicker">THIS MONTH</span><span className="usage-label">DEMO DATA</span></div>
                        <div className="usage-value">18 <span>agent runs</span></div>
                        <div className="usage-track"><span /></div>
                        <div className="usage-foot"><span>18 of 50 runs</span><button onClick={() => notify("Usage limits are informational preview data.")}>View usage</button></div>
                    </section>
                </aside>
            </div>
        </>
    );

    const renderTasks = () => (
        <>
            <section className="welcome-section section-welcome">
                <div className="welcome-copy"><div className="eyebrow"><span className="eyebrow-line" />{header.eyebrow}</div><h1>{header.title}</h1><p>{header.description}</p></div>
                <button className="launch-button" onClick={createNewTask}><FiPlus size={15} /> New task</button>
            </section>
            <div className="list-toolbar">
                <label className="search-input"><FiSearch size={15} /><input value={searchTerm} onChange={(event) => setSearchTerm(event.target.value)} placeholder="Search tasks…" /></label>
                <button className="filter-button" onClick={() => notify("Task filters are part of the connected task API.")}>All statuses <FiChevronDown size={13} /></button>
            </div>
            <div className="task-history-list">
                {filteredTasks.length ? filteredTasks.map((task) => renderTaskCard(task)) : <div className="empty-state">No tasks match that search.</div>}
            </div>
        </>
    );

    const renderAgents = () => (
        <>
            <section className="welcome-section section-welcome">
                <div className="welcome-copy"><div className="eyebrow"><span className="eyebrow-line" />{header.eyebrow}</div><h1>{header.title}</h1><p>{header.description}</p></div>
                <span className="agents-ready-pill"><span className="status-dot" /> All systems ready</span>
            </section>
            <div className="agent-directory">
                {initialAgents.map((agent, index) => (
                    <article className="agent-directory-card" key={agent.initials}>
                        <div className="directory-card-top"><AgentAvatar agent={agent} /><span className={`agent-state state-${agent.status}`}><AgentStatusIcon status={agent.status} />{agent.status === "done" ? "Ready" : agent.status === "working" ? "Working" : "Queued"}</span></div>
                        <h2>{agent.name}</h2><p>{agent.detail}</p>
                        <div className="agent-role-line"><FiCpu size={13} /> {agent.role}</div>
                        <div className="agent-capabilities"><span>{index < 2 ? "Read-only" : index === 2 ? "Propose changes" : "Validation"}</span><span>Task-scoped</span></div>
                    </article>
                ))}
            </div>
            <div className="notice-banner"><FiShield size={16} /><div><strong>Least-privilege by design</strong><span>Agent capabilities are scoped to the selected project and task. Write access, commands, and external actions require separate controls.</span></div></div>
        </>
    );

    const renderActivity = () => (
        <>
            <section className="welcome-section section-welcome">
                <div className="welcome-copy"><div className="eyebrow"><span className="eyebrow-line" />{header.eyebrow}</div><h1>{header.title}</h1><p>{header.description}</p></div>
                <button className="filter-button" onClick={() => notify("Activity filters are preview-only.")}>All events <FiChevronDown size={13} /></button>
            </section>
            <div className="activity-log-card">
                <div className="activity-log-header"><div><strong>OAuth refresh token rotation</strong><span>RUN-248 · Today, 10:40 AM</span></div><span className="task-status status-approval"><span className="status-dot" /> Awaiting approval</span></div>
                <div className="activity-log">
                    {activityItems.map((item, index) => (
                        <div className="activity-log-row" key={item.time}>
                            <span className={`activity-log-icon activity-${item.kind}`}>{item.kind === "code" ? <FiCode size={14} /> : item.kind === "plan" ? <FiFileText size={14} /> : item.kind === "search" ? <FiSearch size={14} /> : <FiPlay size={13} />}</span>
                            <span className="activity-log-line" />
                            <div className="activity-log-copy"><strong>{item.title}</strong><span>{index === 0 ? "Change proposal created · auth/refresh.ts" : index === 1 ? "Plan is ready for implementation" : index === 2 ? "Evidence scoped to acme-platform" : "Request accepted by workspace"}</span></div>
                            <time>{item.time}</time>
                        </div>
                    ))}
                </div>
                <button className="load-events-button" onClick={() => notify("All available preview events are shown.")}>You're all caught up</button>
            </div>
        </>
    );

    return (
        <div className="agentic-app">
            <aside className="app-sidebar">
                <div className="brand-lockup">
                    <span className="brand-mark"><FiZap size={18} /></span>
                    <span className="brand-copy"><strong>ORBIT</strong><small>AGENTIC STUDIO</small></span>
                    <button className="sidebar-collapse" aria-label="Collapse navigation" onClick={() => notify("Navigation is already in compact mode on smaller screens.")}><FiChevronDown size={14} /></button>
                </div>

                <div className="sidebar-workspace">
                    <span className="sidebar-label">WORKSPACE</span>
                    <button className="project-select" onClick={() => setShowProjectMenu((current) => !current)} aria-expanded={showProjectMenu}>
                        <span className="project-monogram">A</span><span className="project-select-copy"><strong>{project}</strong><small>Personal workspace</small></span><FiChevronDown size={14} />
                    </button>
                    {showProjectMenu && (
                        <div className="project-menu">
                            {["acme-platform", "storefront-api", "design-system"].map((name) => (
                                <button key={name} onClick={() => { setProject(name); setShowProjectMenu(false); notify(`Switched preview context to ${name}.`); }}>
                                    <span className="project-monogram">{name.charAt(0).toUpperCase()}</span>{name}{project === name && <FiCheck size={13} />}
                                </button>
                            ))}
                        </div>
                    )}
                </div>

                <button className="sidebar-new-task" onClick={createNewTask}><FiPlus size={15} /><span>New task</span><kbd>⌘ K</kbd></button>

                <nav className="primary-nav" aria-label="Workspace navigation">
                    <span className="sidebar-label">BUILD</span>
                    {([
                        { id: "workspace", label: "Workspace", icon: <FiLayers size={16} /> },
                        { id: "tasks", label: "Runs & tasks", icon: <FiGitPullRequest size={16} />, badge: String(tasks.length) },
                        { id: "agents", label: "Agent team", icon: <FiUsers size={16} /> },
                    ] as const).map((item) => (
                        <button className={section === item.id ? "nav-item nav-item-active" : "nav-item"} key={item.id} onClick={() => setSection(item.id)}>
                            {item.icon}<span>{item.label}</span>{"badge" in item && <span className="nav-badge">{item.badge}</span>}
                        </button>
                    ))}
                    <span className="sidebar-label nav-label-spaced">MONITOR</span>
                    <button className={section === "activity" ? "nav-item nav-item-active" : "nav-item"} onClick={() => setSection("activity")}>
                        <FiActivity size={16} /><span>Activity log</span><span className="unread-indicator" />
                    </button>
                </nav>

                <div className="sidebar-bottom">
                    <div className="sidebar-connection"><span className="connection-indicator" /><span><strong>Workspace connected</strong><small>Local UI preview</small></span></div>
                    <button className="user-profile" onClick={() => notify("Profile settings are not connected in this UI preview.")}>
                        <span className="user-avatar">RS</span><span><strong>Rohit Sharma</strong><small>Personal plan</small></span><FiMoreHorizontal size={16} />
                    </button>
                </div>
            </aside>

            <main className="app-main">
                <header className="topbar">
                    <div className="breadcrumb"><span>Workspace</span><FiChevronRight size={13} /><strong>{section === "workspace" ? "Overview" : sectionTitles[section].title}</strong></div>
                    <div className="topbar-actions">
                        <span className="branch-chip"><FiGitBranch size={13} /> main <FiChevronDown size={12} /></span>
                        <span className="topbar-divider" />
                        <button className="icon-button notification-button" aria-label="Notifications" onClick={() => notify("You're all caught up.")}><FiBell size={16} /><i /></button>
                        <span className="topbar-user">RS</span>
                    </div>
                </header>

                <div className="workspace-scroll">
                    <div className="workspace-content">
                        <div className="prototype-banner"><FiAlertCircle size={14} /><span><strong>Frontend preview</strong> — actions are local only. No backend, repository, agents, or commands are connected.</span><button aria-label="Dismiss preview notice" onClick={(event) => event.currentTarget.parentElement?.remove()}><FiX size={14} /></button></div>
                        {section === "workspace" && renderWorkspace()}
                        {section === "tasks" && renderTasks()}
                        {section === "agents" && renderAgents()}
                        {section === "activity" && renderActivity()}
                        <footer className="workspace-footer">
                            <span>ORBIT <span className="footer-dot">·</span> AGENTIC DEVELOPMENT WORKSPACE</span>
                            <span>Project-aware development workspace</span>
                        </footer>
                    </div>
                </div>
            </main>

            {toast && <div className="toast-message" role="status"><FiCheckCircle size={16} />{toast}</div>}
        </div>
    );
}

export default AgenticWorkspace;
