import { Activity, AlertTriangle } from "lucide-react";
import { cn } from "../lib/utils";

export const SystemHealth = () => {
    // Mock data for now, eventually this could be real-time
    const latency = 45; // ms
    const errorRate = 0.02; // %

    return (
        <div className="bg-slate-900/50 rounded-lg p-3 border border-white/5 space-y-3">
            <div className="flex items-center justify-between text-xs text-slate-400 font-medium uppercase tracking-wider">
                <span>System Health</span>
                <span className="flex items-center gap-1.5 text-emerald-400">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)] animate-pulse"></span>
                    Operational
                </span>
            </div>

            <div className="grid grid-cols-2 gap-2">
                <div className="bg-slate-950/50 rounded p-2 border border-white/5">
                    <div className="text-[10px] text-slate-500 mb-1 flex items-center gap-1">
                        <Activity size={10} /> Latency
                    </div>
                    <div className={cn("text-lg font-mono leading-none", latency < 100 ? "text-emerald-400" : "text-amber-400")}>
                        {latency}<span className="text-xs text-slate-600 ml-0.5">ms</span>
                    </div>
                </div>
                <div className="bg-slate-950/50 rounded p-2 border border-white/5">
                    <div className="text-[10px] text-slate-500 mb-1 flex items-center gap-1">
                        <AlertTriangle size={10} /> Errors
                    </div>
                    <div className={cn("text-lg font-mono leading-none", errorRate < 0.1 ? "text-emerald-400" : "text-rose-400")}>
                        {errorRate}<span className="text-xs text-slate-600 ml-0.5">%</span>
                    </div>
                </div>
            </div>
        </div>
    );
};
