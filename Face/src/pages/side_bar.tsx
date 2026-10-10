import { FiMessageSquare, FiPlus, FiSettings, FiUser, FiZap } from "react-icons/fi";
import { Link } from "react-router-dom";

function SideBar() {
    return (
        <aside className="relative z-20 flex h-screen w-[68px] shrink-0 flex-col border-r border-white/[0.07] bg-[#0a0d15] transition-[width] duration-200 lg:w-64">
            <div className="flex items-center gap-3 border-b border-white/[0.07] px-3 py-5 lg:px-5">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-violet-300/20 bg-gradient-to-br from-violet-500/20 to-cyan-400/10 text-violet-200 shadow-[0_0_24px_rgba(139,92,246,0.12)]">
                    <FiZap className="text-lg" />
                </div>
                <div className="hidden min-w-0 lg:block">
                    <h1 className="truncate text-sm font-semibold tracking-wide text-slate-100">Agentic Studio</h1>
                    <p className="mt-0.5 text-[11px] text-slate-500">Multi-agent workspace</p>
                </div>
            </div>

            <div className="p-3 lg:p-4">
                <button
                    className="flex w-full items-center justify-center gap-2 rounded-xl border border-violet-300/20 bg-violet-500/10 px-3 py-2.5 text-sm font-medium text-violet-100 transition hover:border-violet-300/35 hover:bg-violet-500/20 lg:justify-start lg:px-4"
                    title="Start a new chat"
                >
                    <FiPlus size={18} className="shrink-0" />
                    <span className="hidden lg:inline">New chat</span>
                </button>
                <Link
                    to="/workspace"
                    className="mt-2 flex w-full items-center justify-center gap-2 rounded-xl border border-white/[0.07] px-3 py-2.5 text-sm text-slate-400 transition hover:border-emerald-300/20 hover:bg-emerald-300/[0.05] hover:text-emerald-100 lg:justify-start lg:px-4"
                    title="Open the coding workspace"
                >
                    <FiMessageSquare size={17} className="shrink-0" />
                    <span className="hidden lg:inline">Coding workspace</span>
                </Link>
            </div>

            <div className="flex-1 overflow-y-auto px-2 lg:px-3">
                <p className="mb-2 hidden px-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-600 lg:block">
                    Recent chats
                </p>
                <button className="flex w-full items-center justify-center gap-3 rounded-xl border border-violet-300/[0.08] bg-violet-300/[0.045] px-3 py-2.5 text-left text-sm text-slate-300 transition hover:bg-white/[0.06] lg:justify-start">
                    <FiMessageSquare size={17} className="shrink-0 text-violet-300" />
                    <span className="hidden truncate lg:inline">Research on RAG</span>
                </button>
                <button className="mt-1 flex w-full items-center justify-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm text-slate-500 transition hover:bg-white/[0.045] hover:text-slate-300 lg:justify-start">
                    <FiMessageSquare size={17} className="shrink-0 text-slate-600" />
                    <span className="hidden truncate lg:inline">AI Agents</span>
                </button>
            </div>

            <div className="border-t border-white/[0.07] p-2 lg:p-3">
                <button className="flex w-full items-center justify-center gap-3 rounded-lg px-3 py-2.5 text-sm text-slate-500 transition hover:bg-white/[0.05] hover:text-slate-200 lg:justify-start">
                    <FiSettings size={17} className="shrink-0" />
                    <span className="hidden lg:inline">Settings</span>
                </button>
                <button className="mt-1 flex w-full items-center justify-center gap-3 rounded-lg px-3 py-2.5 text-sm text-slate-500 transition hover:bg-white/[0.05] hover:text-slate-200 lg:justify-start">
                    <FiUser size={17} className="shrink-0" />
                    <span className="hidden lg:inline">Profile</span>
                </button>
            </div>
        </aside>
    );
}

export default SideBar;