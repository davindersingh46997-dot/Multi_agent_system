import {FiPlus,FiMessageSquare,FiUser,FiSettings} from "react-icons/fi";

function SideBar() {
    return (
       <aside className="
       w-64
       h-screen
       flex
       flex-col
       bg-white
       border-r
       border-slate-200
       ">
        <div className="px-5 py-5 border-b border-slate-200">
            <h1 className="text-lg font-semibold text-slate-900">
                Agentic AI system
            </h1>

            <p className="text-xs text-slate-500 mt-1">
                Intelligent AI
            </p>
        </div>

        <div className="p-4">
            <button className="
            w-full
            flex
            items-center
            justify-center
            gap-2
            px-4
            py-2.5
            rounded-xl
            bg-indigo-600
            hover:bg-indigo-700
            text-white
            text-sm
            font-medium
            transition
            ">
                <FiPlus size={20} />
                New Chat
            </button>   
        </div>

        <div className="flex-1 overflow-y-auto px-3">
           <p className="
           px-3
           mb-2
           text-xs
           font-semibold
           text-slate-400
           uppercase
           tracking-wide
           ">
            Recent chats
           </p>

           <button className="
           w-full
           flex
           items-center
           gap-3
           px-3
           py-2.5
           rounded-xl
           text-left
           text-sm
           text-slate-700
           hover: bg-slate-100
           transition
           ">
            <FiMessageSquare size={20}
            className="text-slate-400 shrink-0" />

            <span className="trunate">
            Research on RAG
           </span>

           </button>

           <button className="
           w-full
           flex
           items-center
           gap-3
           px-3
           py-2.5
           rounded-lg
           text-left
           text-sm
           text-slate-700
           hover:bg-slate-100
           transition
           ">
            <FiMessageSquare size={20}
             className="text-slate-400 shrink-0"/>
            <span className="truncate">
                AI Agents
            </span>
            </button>          
        </div>

        <div className="p-3 border-t border-slate-200">

                <button className="
                    w-full
                    flex
                    items-center
                    gap-3
                    px-3
                    py-2.5
                    rounded-lg
                    text-sm
                    text-slate-700
                    hover:bg-slate-100
                    transition
                ">
                    <FiSettings size={18} />
                    Settings
                </button>

                <button className="
                    w-full
                    flex
                    items-center
                    gap-3
                    px-3
                    py-2.5
                    rounded-lg
                    text-sm
                    text-slate-700
                    hover:bg-slate-100
                    transition
                ">
                    <FiUser size={18} />
                    Profile
                </button>

            </div>
    </aside>
    );
}

export default SideBar;