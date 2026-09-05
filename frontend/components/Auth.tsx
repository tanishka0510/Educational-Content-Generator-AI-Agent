"use client";

import { useState } from "react";

interface AuthProps {
  onAuthSuccess: (token: string) => void;
  customNotice?: string;
  onCancel?: () => void;
}

export default function Auth({ onAuthSuccess, customNotice, onCancel }: AuthProps) {
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
            .map((err: { loc?: (string | number)[]; msg?: string }) => {
              const fieldName = err.loc && err.loc.length > 0 ? err.loc[err.loc.length - 1] : "field";
              return `${fieldName}: ${err.msg || "invalid"}`;
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
    <div className="flex min-h-screen items-center justify-center bg-[#F8FAFC] px-4 text-slate-900 font-sans">
      <div className="w-full max-w-md rounded-2xl border border-slate-200/80 bg-white p-8 shadow-xl">
        
        {/* Back / Cancel button if provided */}
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="mb-4 text-xs font-medium text-slate-500 hover:text-slate-900 transition flex items-center gap-1.5"
          >
            ← Home
          </button>
        )}

        {/* Custom Notice Banner for Gating/Trial Limits */}
        {customNotice && (
          <div className="mb-6 rounded-xl border border-[#C59B27]/30 bg-amber-50/80 p-3.5 text-center text-xs leading-5 text-[#9A7318] shadow-2xs">
            <span className="font-bold text-[#C59B27] mr-1.5">Free Trial Notice:</span>
            {customNotice}
          </div>
        )}

        {/* Header */}
        <div className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full border-2 border-[#C59B27] bg-amber-50 text-sm font-serif font-bold text-[#C59B27] shadow-sm">
            SL
          </div>
          <span className="inline-block rounded-full border border-[#C59B27]/40 bg-amber-50 px-3 py-1 text-xs font-semibold uppercase tracking-widest text-[#C59B27]">
            SMARTLEARN ACADEMIC PLATFORM
          </span>
          <h2 className="mt-3 font-serif text-3xl font-medium tracking-tight text-slate-900">
            {isLogin ? "Sign In" : "Create Account"}
          </h2>
          <p className="mt-2 text-sm text-slate-600">
            {isLogin
              ? "Access your academic analytics, document library, and chat records"
              : "Sign up to track your learning progress and unlock unlimited access"}
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="mt-8 space-y-5">
          {error && (
            <div className={`rounded-lg p-4 text-sm ${error.includes("successfully") ? "bg-emerald-50 text-emerald-700 border border-emerald-200" : "bg-rose-50 text-rose-700 border border-rose-200"}`}>
              {error}
            </div>
          )}

          {!isLogin && (
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500">
                Username
              </label>
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="johndoe"
                className="mt-2 w-full rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none focus:border-[#C59B27] focus:bg-white focus:ring-1 focus:ring-[#C59B27]/30 transition"
              />
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500">
              Email Address
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="mt-2 w-full rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none focus:border-[#C59B27] focus:bg-white focus:ring-1 focus:ring-[#C59B27]/30 transition"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500">
              Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="mt-2 w-full rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none focus:border-[#C59B27] focus:bg-white focus:ring-1 focus:ring-[#C59B27]/30 transition"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-[#C59B27] py-3 text-sm font-bold text-white transition hover:bg-[#B38A1F] disabled:opacity-40 shadow-md"
          >
            {loading ? "Processing..." : isLogin ? "Sign In" : "Sign Up"}
          </button>
        </form>

        {/* Footer Toggle */}
        <div className="mt-6 text-center text-sm text-slate-500">
          {isLogin ? (
            <p>
              Don&apos;t have an account?{" "}
              <button
                type="button"
                onClick={() => {
                  setIsLogin(false);
                  setError("");
                }}
                className="font-semibold text-[#C59B27] underline hover:text-[#B38A1F] transition"
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
                className="font-semibold text-[#C59B27] underline hover:text-[#B38A1F] transition"
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
