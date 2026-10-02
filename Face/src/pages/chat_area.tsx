import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { FiPaperclip, FiSend, FiX } from "react-icons/fi";
import SideBar from "./side_bar";

interface Project {
    id: number;
    name: string;
    relative_path: string;
}

interface TaskChange {
    id: number;
    relative_path: string;
    diff: string;
    status: string;
    approval_hash: string;
}

interface DeveloperTask {
    id: number;
    project_id: number;
    prompt: string;
    status: string;
    result: string | null;
    error: string | null;
    created_at: string;
    changes: TaskChange[];
}

const activeStatuses = new Set(["queued", "indexing", "analyzing"]);

function ChatArea() {
    const navigate = useNavigate();
    const [projects, setProjects] = useState<Project[]>([]);
    const [selectedProject, setSelectedProject] = useState("");
    const [showProjectForm, setShowProjectForm] = useState(false);
    const [projectName, setProjectName] = useState("");
    const [projectPath, setProjectPath] = useState(".");
    const [tasks, setTasks] = useState<DeveloperTask[]>([]);
    const [message, setMessage] = useState("");
    const [image, setImage] = useState<File | null>(null);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState("");
    const token = localStorage.getItem("access_token") ?? "";
    const hasActiveTasks = tasks.some((task) => activeStatuses.has(task.status));

    useEffect(() => {
        if (!token) {
            navigate("/login");
            return;
        }

        let cancelled = false;
        const load = async () => {
            try {
                const [projectResponse, taskResponse] = await Promise.all([
                    fetch("/api/projects", {
                        headers: { Authorization: `Bearer ${token}` },
                    }),
                    fetch("/api/tasks", {
                        headers: { Authorization: `Bearer ${token}` },
                    }),
                ]);
                if (projectResponse.status === 401 || taskResponse.status === 401) {
                    localStorage.removeItem("access_token");
                    navigate("/login");
                    return;
                }
                if (!projectResponse.ok || !taskResponse.ok) {
                    throw new Error("Unable to load your workspace.");
                }
                const projectData: Project[] = await projectResponse.json();
                const taskData: DeveloperTask[] = await taskResponse.json();
                if (!cancelled) {
                    setProjects(projectData);
                    setTasks(taskData);
                    setSelectedProject((current) => current || String(projectData[0]?.id ?? ""));
                }
            } catch (loadError) {
                if (!cancelled) {
                    setError(loadError instanceof Error ? loadError.message : "Unable to load your workspace.");
                }
            } finally {
                if (!cancelled) setLoading(false);
            }
        };

        void load();
        return () => {
            cancelled = true;
        };
    }, [navigate, token]);

    useEffect(() => {
        if (!hasActiveTasks || !token) return;
        const interval = window.setInterval(async () => {
            try {
                const response = await fetch("/api/tasks", {
                    headers: { Authorization: `Bearer ${token}` },
                });
                if (response.ok) setTasks(await response.json());
            } catch {
                setError("Task status refresh failed. The task may still be running.");
            }
        }, 2500);
        return () => window.clearInterval(interval);
    }, [hasActiveTasks, token]);

    const createProject = async (event: React.FormEvent) => {
        event.preventDefault();
        setError("");
        try {
            const response = await fetch("/api/projects", {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ name: projectName, relative_path: projectPath }),
                    {projects.length > 0 && (
                        <button
                            type="button"
                            className="rounded-md border border-slate-300 px-3 py-2 text-sm hover:bg-slate-50"
                            onClick={() => setShowProjectForm((open) => !open)}
                        >
                            {showProjectForm ? "Close project form" : "Add project"}
                        </button>
                    )}
            setShowProjectForm(false);
        } catch (createError) {
            setError(createError instanceof Error ? createError.message : "Unable to register project.");
        }
    };

    const sendTask = async () => {
        if (!message.trim() || !selectedProject || submitting) return;
        setSubmitting(true);
        setError("");
        const formData = new FormData();
        formData.append("project_id", selectedProject);
        formData.append("prompt", message.trim());
        if (image) formData.append("image", image);

        try {
            const response = await fetch("/api/tasks", {
                method: "POST",
                headers: { Authorization: `Bearer ${token}` },
                body: formData,
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || "Unable to submit task.");
            setTasks((current) => [data, ...current.filter((task) => task.id !== data.id)]);
            setMessage("");
            setImage(null);
        } catch (sendError) {
            setError(sendError instanceof Error ? sendError.message : "Unable to submit task.");
        } finally {
            setSubmitting(false);
        }
    };

    const decideChange = async (task: DeveloperTask, change: TaskChange, approved: boolean) => {
        setError("");
        try {
            const response = await fetch(
                `/api/tasks/${task.id}/changes/${change.id}/approval`,
                {
                    method: "POST",
                    headers: {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ approved, approval_hash: change.approval_hash }),
                },
            );
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || "Unable to record this decision.");
            setTasks((current) => current.map((item) => item.id === data.id ? data : item));
        } catch (approvalError) {
            setError(approvalError instanceof Error ? approvalError.message : "Unable to record this decision.");
        }
    };

    const visibleTasks = selectedProject
        ? tasks.filter((task) => task.project_id === Number(selectedProject))
        : tasks;

    return (
        <div className="flex min-h-screen bg-slate-100 text-slate-900">
            <SideBar />
            <main className="flex min-w-0 flex-1 flex-col">
                <header className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 bg-white px-6 py-4">
                    <div>
                        <h1 className="text-lg font-semibold">Software workspace</h1>
                        <p className="text-sm text-slate-500">Project-grounded coding tasks</p>
                    </div>
                    <label className="flex items-center gap-2 text-sm">
                        <span className="text-slate-500">Project</span>
                        <select
                            className="max-w-64 rounded-md border border-slate-300 bg-white px-3 py-2"
                            value={selectedProject}
                            onChange={(event) => setSelectedProject(event.target.value)}
                            disabled={!projects.length}
                        >
                            {projects.length === 0 && <option value="">No project registered</option>}
                            {projects.map((project) => (
                                <option key={project.id} value={project.id}>
                                    {project.name} · {project.relative_path}
                                </option>
                            ))}
                        </select>
                    </label>
                    <button
                        className="rounded-md border border-slate-300 px-3 py-2 text-sm hover:bg-slate-50"
                        onClick={() => setShowProjectForm((open) => !open)}
                    >
                        {showProjectForm ? "Close project form" : "Add project"}
                    </button>
                </header>

                <section className="mx-auto flex w-full max-w-5xl flex-1 flex-col px-5 pb-8 pt-6">
                    {(showProjectForm || (projects.length === 0 && !loading)) && (
                        <form onSubmit={createProject} className="mb-6 border-b border-slate-200 pb-6">
                            <h2 className="mb-3 text-base font-semibold">Register a project</h2>
                            <p className="mb-4 text-sm text-slate-600">
                                The path is relative to the backend PROJECTS_ROOT setting.
                            </p>
                            <div className="flex flex-wrap gap-2">
                                <input
                                    className="min-w-40 flex-1 rounded-md border border-slate-300 bg-white px-3 py-2 text-sm"
                                    placeholder="Project name"
                                    value={projectName}
                                    onChange={(event) => setProjectName(event.target.value)}
                                    required
                                />
                                <input
                                    className="min-w-40 flex-1 rounded-md border border-slate-300 bg-white px-3 py-2 text-sm"
                                    placeholder="Relative path, e.g. ."
                                    value={projectPath}
                                    onChange={(event) => setProjectPath(event.target.value)}
                                    required
                                />
                                <button className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white" type="submit">
                                    Add project
                                </button>
                            </div>
                        </form>
                    )}

                    {error && <p role="alert" className="mb-4 border-l-2 border-rose-600 bg-rose-50 px-3 py-2 text-sm text-rose-800">{error}</p>}
                    {loading && <p className="text-sm text-slate-500">Loading workspace…</p>}
                    {!loading && visibleTasks.length === 0 && projects.length > 0 && (
                        <div className="my-auto py-12 text-center">
                            <h2 className="text-xl font-semibold">What are we working on?</h2>
                            <p className="mt-2 text-sm text-slate-500">Ask about the selected project or attach an image containing code.</p>
                        </div>
                    )}

                    <div className="space-y-8">
                        {visibleTasks.map((task) => (
                            <article key={task.id} className="border-b border-slate-200 pb-7">
                                <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
                                    <p className="whitespace-pre-wrap font-medium">{task.prompt}</p>
                                    <span className="rounded-sm bg-slate-200 px-2 py-1 text-xs uppercase text-slate-700">{task.status.replaceAll("_", " ")}</span>
                                </div>
                                {task.error && <p className="mb-3 text-sm text-amber-800">{task.error}</p>}
                                {task.result && <p className="whitespace-pre-wrap text-sm leading-6 text-slate-700">{task.result}</p>}
                                {task.changes.map((change) => (
                                    <section key={change.id} className="mt-4 border border-slate-300 bg-white">
                                        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200 px-3 py-2">
                                            <span className="font-mono text-sm">{change.relative_path}</span>
                                            <span className="text-xs uppercase text-slate-500">{change.status}</span>
                                        </div>
                                        <pre className="max-h-80 overflow-auto p-3 text-xs leading-5 text-slate-800">{change.diff || "New file proposal"}</pre>
                                        {change.status === "pending" && (
                                            <div className="flex justify-end gap-2 border-t border-slate-200 p-3">
                                                <button
                                                    className="rounded-md border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50"
                                                    onClick={() => void decideChange(task, change, false)}
                                                >Reject</button>
                                                <button
                                                    className="rounded-md bg-emerald-700 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-800"
                                                    onClick={() => void decideChange(task, change, true)}
                                                >Approve and apply</button>
                                            </div>
                                        )}
                                    </section>
                                ))}
                            </article>
                        ))}
                    </div>
                </section>

                <footer className="sticky bottom-0 border-t border-slate-200 bg-white/95 px-4 py-3 backdrop-blur">
                    <div className="mx-auto flex w-full max-w-5xl items-end gap-2 rounded-md border border-slate-300 bg-white p-2 focus-within:border-blue-600">
                        <textarea
                            className="max-h-40 min-h-11 min-w-0 flex-1 resize-y bg-transparent px-2 py-2 text-sm outline-none"
                            placeholder="Describe the coding task..."
                            rows={1}
                            value={message}
                            onChange={(event) => setMessage(event.target.value)}
                            onKeyDown={(event) => {
                                if (event.key === "Enter" && !event.shiftKey) {
                                    event.preventDefault();
                                    void sendTask();
                                }
                            }}
                        />
                        <label className="cursor-pointer rounded-md p-2 text-slate-600 hover:bg-slate-100" title="Attach a code screenshot">
                            <FiPaperclip aria-hidden="true" />
                            <input
                                className="sr-only"
                                type="file"
                                accept="image/png,image/jpeg,image/webp"
                                onChange={(event) => setImage(event.target.files?.[0] ?? null)}
                            />
                        </label>
                        <button
                            className="rounded-md bg-blue-700 p-2.5 text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-40"
                            onClick={() => void sendTask()}
                            disabled={!message.trim() || !selectedProject || submitting}
                            aria-label={submitting ? "Submitting task" : "Send task"}
                            title="Send task"
                        >
                            <FiSend aria-hidden="true" />
                        </button>
                    </div>
                    {image && (
                        <div className="mx-auto mt-2 flex w-full max-w-5xl items-center justify-between text-xs text-slate-600">
                            <span>{image.name}</span>
                            <button type="button" onClick={() => setImage(null)} aria-label="Remove image attachment" title="Remove image">
                                <FiX />
                            </button>
                        </div>
                    )}
                </footer>
            </main>
        </div>
    );
}

export default ChatArea;