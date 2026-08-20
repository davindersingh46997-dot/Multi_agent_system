import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FiEye, FiEyeOff } from "react-icons/fi";
import FaceUnlock from "./Face_unlock";

function SignIn() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [showFaceUnlock, setShowFaceUnlock] = useState(false);

    const navigate = useNavigate();

    const handleSignIn = () => {
        if(username == "davinder" && password == "dav"){
            navigate("/chat");
        }

        else{
            alert("username or password is incorrect ")
        }

        setUsername("");
        setPassword("");
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
            <div className="w-full max-w-md p-8 bg-white rounded-lg shadow-md">

                <h2 className="text-2xl font-semibold text-center mb-6">
                    Sign In
                </h2>

                {/* Username */}
                <input
                    type="text"
                    placeholder="Enter your username"
                    className="w-full px-4 py-2 mb-4 border border-gray-300 rounded-lg focus:outline-none focus:ring focus:ring-blue-200"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                />

                {/* Password */}
                <div className="relative mb-4">
                    <input
                        type={showPassword ? "text" : "password"}
                        placeholder="Enter your password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full px-4 py-2 pr-12 border border-gray-300 rounded-lg focus:outline-none focus:ring focus:ring-blue-200"
                    />

                    <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                        aria-label={showPassword ? "Hide password" : "Show password"}
                    >
                        {showPassword ? <FiEyeOff size={20} /> : <FiEye size={20} />}
                    </button>
                </div>

                {/* Sign In */}
                <button
                    type="button"
                    className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring focus:ring-blue-200"
                    onClick={handleSignIn}
                >
                    Sign In
                </button>

                <button 
                type="button"
                onClick={() => setShowFaceUnlock(true)}
                className="mt-4 text-sm text-blue-600 underline hover:text-blue-800"
                >
                    Face Authentication
                </button>

                {showFaceUnlock && (
                <FaceUnlock
                    onClose={() => setShowFaceUnlock(false)}
                />
            )}

            </div>
        </div>
    );
}

export default SignIn;