import {useState} from "react";

function ChatArea() {
    const [message, setMessage] = useState("");

    const handleSendMessage = () => {
        // Implementation for sending the message
          console.log("Sending message:", message);

          setMessage(""); // Clear the input after sending
    }

    return (
        <div className="fixed bottom-0 left-0 w-full flex justify-center p-4 bg-white border-t border-gray-200">
            <div className="flex items-end gap-2 w-full max-w-2xl mx-auto p-3 bg-white border border-gray-200 rounded-2xl shadow-sm">
                <textarea
                    placeholder="Type your message here..."
                    rows={1}
                    className="flex-1 resize-none bg-transparent px-3 py-2 text-sm text-gray-800 placeholder-gray-400 focus:outline-none max-h-40 border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:ring focus:ring-blue-200 transition-all overflow-y-auto"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                ></textarea>
                <button className="shrink-0 px-4 py-2 rounded-xl bg-gray-900 text-white text-sm font-medium hover:bg-gray-700 active:scale-95 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
                value={message}
                onClick={handleSendMessage}
                >
                    Send
                </button>
            </div>
        </div>
    )
};

export default ChatArea;