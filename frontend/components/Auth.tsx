"use client";

import { useState } from "react";

interface AuthProps {
  onAuthSuccess: (token: string) => void;
}

export default function Auth({ onAuthSuccess }: AuthProps) {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const baseUrl = "http://127.0.0.1:8000";
    const endpoint = isLogin ? `${baseUrl}/auth/login` : `${baseUrl}/auth/signup`;
    const payload = isLogin
      ? { email, password }
      : { username, email, password };

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        let errMsg = `Request failed with status ${response.status}`;
        if (typeof errorData.detail === "string") {
          errMsg = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          errMsg = errorData.detail
            .map((err: any) => {
              const fieldName = err.loc[err.loc.length - 1];
              return `${fieldName}: ${err.msg}`;
            })
            .join(", ");
        }
        throw new Error(errMsg);
      }

      if (isLogin) {
        const data = await response.json();
        localStorage.setItem("authToken", data.access_token);
        onAuthSuccess(data.access_token);
      } else {
        // Automatically switch to login screen after successful signup
        setIsLogin(true);
        setError("Account created successfully! Please log in.");
        setPassword("");
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 px-4 text-white">
      <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900/60 p-8 shadow-xl backdrop-blur-md">
        
        {/* Header */}
        <div className="text-center">
          <p className="text-sm font-semibold uppercase tracking-widest text-slate-400">
            Educational AI Agent Platform
          </p>
          <h2 className="mt-2 text-3xl font-bold tracking-tight text-white">
            {isLogin ? "Sign In" : "Create Account"}
          </h2>
          <p className="mt-2 text-sm text-slate-400">
            {isLogin
              ? "Access your dashboard, chat history, and metrics"
              : "Sign up to track your learning progress"}
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="mt-8 space-y-5">
          {error && (
            <div className={`rounded-lg p-4 text-sm ${error.includes("successfully") ? "bg-emerald-950/60 text-emerald-400 border border-emerald-800" : "bg-rose-950/60 text-rose-400 border border-rose-800"}`}>
              {error}
            </div>
          )}

          {!isLogin && (
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400">
                Username
              </label>
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="johndoe"
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-white outline-none focus:border-slate-500"
              />
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400">
              Email Address
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-white outline-none focus:border-slate-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400">
              Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-white outline-none focus:border-slate-500"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-white py-3 text-sm font-semibold text-slate-950 transition hover:bg-slate-200 disabled:opacity-40"
          >
            {loading ? "Processing..." : isLogin ? "Sign In" : "Sign Up"}
          </button>
        </form>

        {/* Footer Toggle */}
        <div className="mt-6 text-center text-sm text-slate-400">
          {isLogin ? (
            <p>
              Don't have an account?{" "}
              <button
                type="button"
                onClick={() => {
                  setIsLogin(false);
                  setError("");
                }}
                className="font-medium text-white underline hover:text-slate-200"
              >
                Sign Up
              </button>
            </p>
          ) : (
            <p>
              Already have an account?{" "}
              <button
                type="button"
                onClick={() => {
                  setIsLogin(true);
                  setError("");
                }}
                className="font-medium text-white underline hover:text-slate-200"
              >
                Sign In
              </button>
            </p>
          )}
        </div>

      </div>
    </div>
  );
}
