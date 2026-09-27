import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { FiEye, FiEyeOff } from "react-icons/fi";
import { FcGoogle } from "react-icons/fc";
import { FaFacebook } from "react-icons/fa";

function SignUp() {
    const navigate = useNavigate();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        setError("");

        if (!email || !password) {
            setError("Please enter your email and password.");
            return;
        }

        if (password.length < 8) {
            setError("Password must contain at least 8 characters.");
            return;
        }

        try {
            setLoading(true);

            const response = await fetch("/api/auth/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    email,
                    password,
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail || "Unable to create account."
                );
            }

            navigate("/verify-2fa", {
                state: {
                    email,
                },
            });

        } catch (err) {
            if (err instanceof Error) {
                setError(err.message);
            } else {
                setError("Something went wrong.");
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="relative min-h-screen overflow-hidden bg-black flex items-center justify-center px-4">

            {/* =========================================
                SPACE BACKGROUND
            ========================================= */}

            <div
                className="
                    absolute inset-0
                    bg-black
                    bg-[radial-gradient(ellipse_at_center,_rgba(30,45,110,0.20)_0%,_rgba(0,0,0,1)_60%)]
                "
            />

            {/* Blue / Purple Glow */}

            <div
                className="
                    absolute
                    left-1/2
                    top-1/2
                    -translate-x-1/2
                    -translate-y-1/2
                    h-[650px]
                    w-[650px]
                    rounded-full
                    bg-[radial-gradient(circle,_rgba(85,45,180,0.28)_0%,_rgba(30,55,150,0.15)_35%,_transparent_70%)]
                    blur-2xl
                "
            />

            {/* Stars */}

            <div
                className="
                    absolute inset-0
                    opacity-70
                    bg-[radial-gradient(circle_at_10%_20%,white_0,white_1px,transparent_1px),
                        radial-gradient(circle_at_20%_80%,white_0,white_1px,transparent_1px),
                        radial-gradient(circle_at_35%_35%,white_0,white_1px,transparent_1px),
                        radial-gradient(circle_at_50%_15%,white_0,white_1px,transparent_1px),
                        radial-gradient(circle_at_65%_70%,white_0,white_1px,transparent_1px),
                        radial-gradient(circle_at_80%_25%,white_0,white_1px,transparent_1px),
                        radial-gradient(circle_at_90%_80%,white_0,white_1px,transparent_1px)]
                "
            />

            {/* Second layer of stars */}

            <div
                className="
                    absolute inset-0
                    scale-125
                    opacity-40
                    bg-[radial-gradient(circle_at_15%_45%,white_0,white_1px,transparent_1px),
                        radial-gradient(circle_at_30%_15%,white_0,white_1px,transparent_1px),
                        radial-gradient(circle_at_48%_85%,white_0,white_1px,transparent_1px),
                        radial-gradient(circle_at_72%_45%,white_0,white_1px,transparent_1px),
                        radial-gradient(circle_at_88%_15%,white_0,white_1px,transparent_1px)]
                "
            />


            {/* =========================================
                SIGN UP CARD
            ========================================= */}

            <div
                className="
                    relative
                    z-10
                    w-full
                    max-w-[368px]
                    rounded-[15px]
                    border
                    border-slate-600/40
                    bg-gradient-to-br
                    from-[#1c1d2b]/95
                    to-[#12131e]/95
                    px-12
                    py-7
                    shadow-[0_25px_70px_rgba(0,0,0,0.65)]
                    backdrop-blur-xl
                "
            >

                {/* =====================================
                    TITLE
                ===================================== */}

                <h1
                    className="
                        mb-5
                        text-center
                        text-xl
                        font-bold
                        tracking-tight
                        text-gray-100
                    "
                >
                    Create an account
                </h1>


                {/* =====================================
                    SOCIAL BUTTONS
                ===================================== */}

                <div className="flex gap-2.5">

                    {/* Google */}

                    <button
                        type="button"
                        className="
                            flex
                            h-[34px]
                            flex-1
                            items-center
                            justify-center
                            gap-2
                            rounded
                            bg-[#2a2b31]
                            text-[11px]
                            font-medium
                            text-gray-400
                            transition
                            hover:bg-[#34353c]
                        "
                    >
                        <FcGoogle size={17} />

                        <span>
                            Google
                        </span>
                    </button>


                    {/* Facebook */}

                    <button
                        type="button"
                        className="
                            flex
                            h-[34px]
                            flex-1
                            items-center
                            justify-center
                            gap-2
                            rounded
                            bg-[#2a2b31]
                            text-[11px]
                            font-medium
                            text-gray-400
                            transition
                            hover:bg-[#34353c]
                        "
                    >
                        <FaFacebook
                            size={16}
                            className="text-[#1877F2]"
                        />

                        <span>
                            Facebook
                        </span>
                    </button>

                </div>


                {/* =====================================
                    OR
                ===================================== */}

                <div
                    className="
                        my-3
                        flex
                        items-center
                        gap-2.5
                        text-xs
                        text-gray-500
                    "
                >

                    <div className="h-px flex-1 bg-white/5" />

                    <span>
                        Or
                    </span>

                    <div className="h-px flex-1 bg-white/5" />

                </div>


                {/* =====================================
                    FORM
                ===================================== */}

                <form
                    onSubmit={handleSubmit}
                    className="flex flex-col gap-3.5"
                >

                    {/* EMAIL */}

                    <div className="flex flex-col gap-1.5">

                        <label
                            htmlFor="email"
                            className="
                                text-xs
                                font-normal
                                text-gray-400
                            "
                        >
                            Email
                        </label>

                        <input
                            id="email"
                            type="email"
                            value={email}
                            onChange={(e) =>
                                setEmail(e.target.value)
                            }
                            placeholder="balmida@gmail.com"
                            className="
                                h-[35px]
                                w-full
                                rounded-md
                                border
                                border-[#353640]
                                bg-[#171822]
                                px-3
                                text-[11px]
                                text-gray-200
                                outline-none
                                placeholder:text-[#686974]
                                transition
                                focus:border-blue-500
                                focus:ring-1
                                focus:ring-blue-500/30
                            "
                        />

                    </div>


                    {/* PASSWORD */}

                    <div className="flex flex-col gap-1.5">

                        {/* Password label */}

                        <div className="flex items-center justify-between">

                            <label
                                htmlFor="password"
                                className="
                                    text-xs
                                    font-normal
                                    text-gray-400
                                "
                            >
                                Password
                            </label>

                            <Link
                                to="/forgot-password"
                                className="
                                    text-[11px]
                                    text-gray-500
                                    transition
                                    hover:text-gray-300
                                "
                            >
                                Forgot ?
                            </Link>

                        </div>


                        {/* Password input */}

                        <div className="relative">

                            <input
                                id="password"
                                type={
                                    showPassword
                                        ? "text"
                                        : "password"
                                }
                                value={password}
                                onChange={(e) =>
                                    setPassword(e.target.value)
                                }
                                placeholder="Enter your password"
                                className="
                                    h-[35px]
                                    w-full
                                    rounded-md
                                    border
                                    border-[#353640]
                                    bg-[#171822]
                                    px-3
                                    pr-10
                                    text-[11px]
                                    text-gray-200
                                    outline-none
                                    placeholder:text-[#686974]
                                    transition
                                    focus:border-blue-500
                                    focus:ring-1
                                    focus:ring-blue-500/30
                                "
                            />

                            <button
                                type="button"
                                onClick={() =>
                                    setShowPassword(
                                        !showPassword
                                    )
                                }
                                className="
                                    absolute
                                    right-2.5
                                    top-1/2
                                    -translate-y-1/2
                                    text-gray-500
                                    transition
                                    hover:text-gray-300
                                "
                            >
                                {showPassword ? (
                                    <FiEyeOff size={17} />
                                ) : (
                                    <FiEye size={17} />
                                )}
                            </button>

                        </div>

                    </div>


                    {/* ERROR */}

                    {error && (
                        <p
                            className="
                                -mt-1
                                text-[11px]
                                text-red-400
                            "
                        >
                            {error}
                        </p>
                    )}


                    {/* =================================
                        CREATE ACCOUNT
                    ================================= */}

                    <button
                        type="submit"
                        disabled={loading}
                        className="
                            mt-0.5
                            h-[34px]
                            w-full
                            rounded-md
                            bg-[#1976ed]
                            text-[11px]
                            font-semibold
                            text-white
                            transition
                            hover:bg-[#2682f5]
                            hover:shadow-[0_5px_18px_rgba(25,118,237,0.25)]
                            active:scale-[0.99]
                            disabled:cursor-not-allowed
                            disabled:opacity-60
                        "
                    >
                        {loading
                            ? "Creating account..."
                            : "Create account"}
                    </button>

                </form>


                {/* =====================================
                    LOGIN
                ===================================== */}

                <div
                    className="
                        mt-5
                        flex
                        items-center
                        justify-center
                        gap-1
                        text-[11px]
                        text-gray-600
                    "
                >

                    <span>
                        Already Have An Account?
                    </span>

                    <Link
                        to="/signin"
                        className="
                            font-medium
                            text-gray-500
                            transition
                            hover:text-gray-300
                        "
                    >
                        Log in
                    </Link>

                </div>

            </div>

        </div>
    );
}

export default SignUp;