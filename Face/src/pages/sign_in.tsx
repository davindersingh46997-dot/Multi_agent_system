import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
    FiEye,
    FiEyeOff,
    FiUser,
    FiLock,
    FiLogIn,
    FiShield,
    FiAlertCircle,
} from "react-icons/fi";
import { RiScanLine, RiSparklingFill } from "react-icons/ri";
import FaceUnlock from "./Face_unlock";

function SignIn() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [showFaceUnlock, setShowFaceUnlock] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const navigate = useNavigate();

    const handleSignIn = async (e?: React.FormEvent) => {
        if (e) e.preventDefault();
        setError("");

        if (!username || !password) {
            const msg = "Please enter the username and password ";
            setError(msg);
            alert(msg);
            return;
        }

        try {
            setLoading(true);

            const response = await fetch("/api/auth/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    username,
                    password,
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                const errMsg = data.detail || "Invalid Username or password ";
                setError(errMsg);
                alert(errMsg);
                return;
            }

            localStorage.setItem("access_token", data.access_token);

            localStorage.setItem(
                "user",
                JSON.stringify(data.user)
            );

            navigate("chat");

        } catch (err) {
            console.error("Login error", err);
            const failMsg = "unable to connect to the server ";
            setError(failMsg);
            alert(failMsg);
        } finally {
            setLoading(false);
        }

        setUsername("");
        setPassword("");
    };

    return (
        <div className="relative min-h-screen w-full overflow-hidden bg-[#07080e] flex items-center justify-center px-4 py-10 selection:bg-blue-500/30 selection:text-blue-200">

            {/* =========================================
                DYNAMIC AMBIENT BACKGROUND & LIGHTING
            ========================================= */}

            {/* Deep radial gradient backdrop */}
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.18),rgba(255,255,255,0))]" />
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_rgba(30,58,138,0.22)_0%,_rgba(7,8,14,1)_75%)]" />

            {/* Cybernetic grid matrix with subtle motion */}
            <div className="pointer-events-none absolute inset-0 opacity-[0.03] bg-[linear-gradient(to_right,#808080_1px,transparent_1px),linear-gradient(to_bottom,#808080_1px,transparent_1px)] bg-[size:40px_40px] animate-grid-drift [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_70%,transparent_100%)]" />

            {/* Animated floating colored glow orbs */}
            <div className="pointer-events-none absolute -top-40 left-1/2 -translate-x-1/2 w-[720px] h-[460px] bg-gradient-to-tr from-blue-600/25 via-indigo-500/20 to-cyan-400/15 blur-[130px] rounded-full animate-orb-1" />
            <div className="pointer-events-none absolute -bottom-32 right-10 w-[520px] h-[420px] bg-gradient-to-br from-indigo-600/20 via-purple-600/15 to-pink-500/10 blur-[120px] rounded-full animate-orb-2" />
            <div className="pointer-events-none absolute -bottom-32 left-10 w-[460px] h-[360px] bg-gradient-to-tr from-blue-500/20 via-teal-500/15 to-cyan-400/15 blur-[110px] rounded-full animate-orb-3" />

            {/* Shooting stars / dynamic light streaks */}
            <div className="pointer-events-none absolute top-16 right-[20%] w-32 h-[1.5px] bg-gradient-to-r from-transparent via-cyan-400 to-white animate-shooting-star-1 opacity-0 rounded-full shadow-[0_0_10px_rgba(34,211,238,0.9)]" />
            <div className="pointer-events-none absolute top-36 left-[18%] w-28 h-[1.5px] bg-gradient-to-r from-transparent via-blue-400 to-indigo-200 animate-shooting-star-2 opacity-0 rounded-full shadow-[0_0_10px_rgba(96,165,250,0.9)]" />

            {/* Starfield Layer 1 - Twinkling fast */}
            <div
                className="
                    pointer-events-none absolute inset-0 opacity-70 animate-twinkle-fast
                    bg-[radial-gradient(circle_at_12%_18%,rgba(255,255,255,0.7)_0,transparent_1px),
                        radial-gradient(circle_at_42%_32%,rgba(255,255,255,0.6)_0,transparent_1px),
                        radial-gradient(circle_at_68%_14%,rgba(255,255,255,0.85)_0,transparent_1px),
                        radial-gradient(circle_at_91%_28%,rgba(255,255,255,0.7)_0,transparent_1px)]
                "
            />

            {/* Starfield Layer 2 - Twinkling slow */}
            <div
                className="
                    pointer-events-none absolute inset-0 opacity-50 animate-twinkle-slow
                    bg-[radial-gradient(circle_at_24%_78%,rgba(255,255,255,0.65)_0,transparent_1px),
                        radial-gradient(circle_at_82%_64%,rgba(255,255,255,0.6)_0,transparent_1px),
                        radial-gradient(circle_at_55%_88%,rgba(255,255,255,0.7)_0,transparent_1px),
                        radial-gradient(circle_at_35%_60%,rgba(255,255,255,0.5)_0,transparent_1px)]
                "
            />

            {/* =========================================
                SIGN IN CARD
            ========================================= */}

            <div className="relative z-10 w-full max-w-[420px] transition-all duration-300">
                {/* Glow ring around card */}
                <div className="absolute -inset-0.5 rounded-3xl bg-gradient-to-b from-blue-500/35 via-indigo-500/15 to-transparent opacity-75 blur-sm animate-card-aura" />

                <div
                    className="
                        relative
                        w-full
                        rounded-3xl
                        border
                        border-slate-700/60
                        bg-gradient-to-b
                        from-[#151726]/95
                        via-[#0e101b]/95
                        to-[#090a12]/95
                        p-8
                        sm:p-9
                        shadow-[0_25px_70px_rgba(0,0,0,0.85)]
                        backdrop-blur-2xl
                    "
                >
                    {/* Header badge & title */}
                    <div className="flex flex-col items-center text-center mb-7">
                        {/* Futuristic Shield Icon */}
                        <div className="relative mb-3 flex items-center justify-center">
                            <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-500 to-indigo-600 blur-md opacity-50" />
                            <div className="relative flex h-14 w-14 items-center justify-center rounded-2xl border border-blue-400/30 bg-[#121422] shadow-inner shadow-blue-500/20">
                                <FiShield className="text-2xl text-blue-400" />
                                <RiSparklingFill className="absolute top-2 right-2 text-xs text-cyan-300 animate-pulse" />
                            </div>
                        </div>

                        {/* Title */}
                        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
                            Welcome Back
                        </h1>

                        <p className="mt-1.5 text-xs text-slate-400">
                            Sign in to access your Multi-Agent Workspace
                        </p>

                        {/* Status Pill */}
                        <div className="mt-2.5 inline-flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-0.5 text-[10px] font-medium text-emerald-400">
                            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-ping" />
                            <span>System Secure • AI Ready</span>
                        </div>
                    </div>

                    {/* Inline Error Notice */}
                    {error && (
                        <div className="mb-5 flex items-center gap-2.5 rounded-xl border border-red-500/30 bg-red-500/10 px-3.5 py-2.5 text-xs text-red-300">
                            <FiAlertCircle className="text-base shrink-0 text-red-400" />
                            <span className="flex-1">{error}</span>
                        </div>
                    )}

                    {/* Form */}
                    <form onSubmit={handleSignIn} className="space-y-4">
                        {/* Username Input */}
                        <div>
                            <label
                                htmlFor="username"
                                className="block text-xs font-medium text-slate-300 mb-1.5"
                            >
                                Username
                            </label>
                            <div className="group relative rounded-xl border border-slate-700/80 bg-[#131522] focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500/20 transition-all duration-200">
                                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-400 group-focus-within:text-blue-400 transition-colors">
                                    <FiUser className="text-base" />
                                </div>
                                <input
                                    id="username"
                                    type="text"
                                    placeholder="Enter your username"
                                    className="w-full bg-transparent py-2.5 pl-10 pr-4 text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    autoComplete="username"
                                />
                            </div>
                        </div>

                        {/* Password Input */}
                        <div>
                            <div className="flex items-center justify-between mb-1.5">
                                <label
                                    htmlFor="password"
                                    className="block text-xs font-medium text-slate-300"
                                >
                                    Password
                                </label>
                            </div>
                            <div className="group relative rounded-xl border border-slate-700/80 bg-[#131522] focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500/20 transition-all duration-200">
                                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-400 group-focus-within:text-blue-400 transition-colors">
                                    <FiLock className="text-base" />
                                </div>
                                <input
                                    id="password"
                                    type={showPassword ? "text" : "password"}
                                    placeholder="Enter your password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full bg-transparent py-2.5 pl-10 pr-11 text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none"
                                    autoComplete="current-password"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute inset-y-0 right-0 flex items-center pr-3.5 text-slate-400 hover:text-slate-200 transition-colors focus:outline-none"
                                    aria-label={showPassword ? "Hide password" : "Show password"}
                                >
                                    {showPassword ? (
                                        <FiEyeOff className="text-base" />
                                    ) : (
                                        <FiEye className="text-base" />
                                    )}
                                </button>
                            </div>
                        </div>

                        {/* Sign In Button */}
                        <button
                            type="submit"
                            disabled={loading}
                            className="
                                relative
                                w-full
                                overflow-hidden
                                rounded-xl
                                bg-gradient-to-r
                                from-blue-600
                                via-indigo-600
                                to-blue-500
                                py-2.5
                                px-4
                                text-xs
                                sm:text-sm
                                font-semibold
                                text-white
                                shadow-[0_0_20px_rgba(37,99,235,0.35)]
                                transition-all
                                duration-200
                                hover:from-blue-500
                                hover:via-indigo-500
                                hover:to-blue-400
                                hover:shadow-[0_0_25px_rgba(37,99,235,0.5)]
                                active:scale-[0.98]
                                disabled:opacity-60
                                disabled:cursor-not-allowed
                                disabled:active:scale-100
                                flex
                                items-center
                                justify-center
                                gap-2
                                mt-2
                            "
                        >
                            {loading ? (
                                <>
                                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                                    <span>Authenticating...</span>
                                </>
                            ) : (
                                <>
                                    <FiLogIn className="text-base" />
                                    <span>Sign In</span>
                                </>
                            )}
                        </button>
                    </form>

                    {/* Divider */}
                    <div className="my-5 flex items-center gap-3 text-xs text-slate-500">
                        <div className="h-px flex-1 bg-slate-700/50" />
                        <span className="text-[11px] uppercase tracking-wider text-slate-400">
                            Or Biometric
                        </span>
                        <div className="h-px flex-1 bg-slate-700/50" />
                    </div>

                    {/* Face Authentication Biometric Button */}
                    <button
                        type="button"
                        onClick={() => setShowFaceUnlock(true)}
                        className="
                            group
                            relative
                            w-full
                            flex
                            items-center
                            justify-between
                            rounded-xl
                            border
                            border-cyan-500/30
                            bg-cyan-950/20
                            hover:bg-cyan-900/30
                            p-3
                            transition-all
                            duration-200
                            hover:border-cyan-400/60
                            hover:shadow-[0_0_20px_rgba(6,182,212,0.2)]
                            active:scale-[0.99]
                        "
                    >
                        <div className="flex items-center gap-3">
                            <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-cyan-400/30 bg-cyan-500/10 text-cyan-400 group-hover:scale-105 transition-transform">
                                <RiScanLine className="text-xl animate-pulse" />
                            </div>
                            <div className="text-left">
                                <div className="text-xs font-semibold text-cyan-200 group-hover:text-white transition-colors">
                                    Face Authentication
                                </div>
                                <div className="text-[10px] text-cyan-400/70">
                                    Instant biometric recognition
                                </div>
                            </div>
                        </div>

                        <span className="rounded-md border border-cyan-500/30 bg-cyan-500/10 px-2 py-0.5 text-[10px] font-medium text-cyan-300">
                            Scan ID
                        </span>
                    </button>

                    {/* Sign Up Link */}
                    <div className="mt-6 text-center text-xs text-slate-400">
                        <span>Don&apos;t have an account? </span>
                        <Link
                            to="/SignUp"
                            className="font-medium text-blue-400 hover:text-blue-300 underline underline-offset-4 transition-colors"
                        >
                            Sign Up
                        </Link>
                    </div>
                </div>

                {/* Footer Security Note */}
                <div className="mt-4 flex items-center justify-center gap-2 text-center text-[11px] text-slate-500">
                    <FiShield className="text-xs text-slate-500" />
                    <span>256-bit Encrypted Session • AI Multi-Agent Gateway</span>
                </div>
            </div>

            {/* Face Unlock Modal */}
            {showFaceUnlock && (
                <FaceUnlock onClose={() => setShowFaceUnlock(false)} />
            )}
        </div>
    );
}

export default SignIn;