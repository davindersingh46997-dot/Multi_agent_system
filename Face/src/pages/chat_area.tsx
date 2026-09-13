import { useState } from "react";
import SideBar from "./side_bar";

function ChatArea() {
    const [message, setMessage] = useState("");
    const [messages, setMessages] = useState<string[]>([]);

    const handleSendMessage = () => {
        // Don't send empty messages
        if (!message.trim()) return;

        console.log("Sending message:", message);

        // Add new message to the chat
        setMessages((prevMessages) => [
            ...prevMessages,
            message.trim(),
        ]);

        // Clear input
        setMessage("");
    };

    const handleKeyDown = (
        e: React.KeyboardEvent<HTMLTextAreaElement>
    ) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    return (
        <div className="min-h-screen flex flex-col bg-slate-500">

            <SideBar/>

            {/* ================= CHAT AREA ================= */}
            <div className="flex-1 overflow-y-auto px-6 py-6 pb-32">

                <div className="max-w-3xl mx-auto">

                    {messages.map((msg, index) => (
                        <div
                            key={index}
                            className="flex justify-end mb-4"
                        >
                            <div
                                className="
                                    max-w-[70%]
                                    bg-blue-500
                                    text-white
                                    px-4
                                    py-3
                                    rounded-2xl
                                    rounded-br-md
                                    break-words
                                    shadow-sm
                                "
                            >
                                {msg}
                            </div>
                        </div>
                    ))}

                </div>
            </div>


            {/* ================= INPUT AREA ================= */}
            <div className="
                fixed
                bottom-0
                left-0
                w-full
                bg-slate-500
                border-t
                border-gray-200
                p-4
            ">

                <div className="
                    flex
                    items-end
                    gap-2
                    w-full
                    max-w-3xl
                    mx-auto
                    p-3
                    bg-black-200
                    border
                    border-gray-200
                    rounded-2xl
                    shadow-sm
                ">

                    {/* Textarea */}
                    <textarea
                        placeholder="Type your message here..."
                        rows={1}
                        className="
                            flex-1
                            resize-none
                            bg-transparent
                            px-3
                            py-2
                            text-sm
                            text-gray-800
                            placeholder-gray-400
                            focus:outline-none
                            max-h-40
                            border-2
                            border-gray-300
                            rounded-xl
                            focus:border-blue-500
                            focus:ring
                            focus:ring-blue-200
                            transition-all
                            overflow-y-auto
                        "
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        onKeyDown={handleKeyDown}
                    />

                    {/* Send button */}
                    <button
                        onClick={handleSendMessage}
                        disabled={!message.trim()}
                        className="
                            shrink-0
                            px-4
                            py-2
                            rounded-xl
                            bg-gray-900
                            text-white
                            text-sm
                            font-medium
                            hover:bg-gray-700
                            active:scale-95
                            transition-all
                            disabled:opacity-40
                            disabled:cursor-not-allowed
                        "
                    >
                        Send
                    </button>

                </div>
            </div>

        </div>
    );
}

export default ChatArea;