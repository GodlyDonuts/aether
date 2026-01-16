import { useEffect, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Globe, Wifi } from 'lucide-react';

interface Log {
    id: string;
    path: string;
    method: string;
    status: number;
    timestamp: string;
    ip: string;
}

export const ActiveConnections = () => {
    const [logs, setLogs] = useState<Log[]>([]);
    const ws = useRef<WebSocket | null>(null);

    useEffect(() => {
        // Connect to WebSocket
        const connect = () => {
            // In production replace localhost with window.location.host
            const socket = new WebSocket('ws://localhost:8000/ws');

            socket.onopen = () => {
                console.log('Connected to traffic stream');
            };

            socket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'traffic') {
                    const newLog: Log = {
                        id: Math.random().toString(36).substr(2, 9),
                        path: data.path,
                        method: data.method,
                        status: data.status,
                        timestamp: new Date().toLocaleTimeString(),
                        ip: data.ip
                    };
                    setLogs(prev => [newLog, ...prev].slice(0, 7));
                }
            };

            socket.onclose = () => {
                // console.log('Disconnected from stream, reconnecting...');
                setTimeout(connect, 3000);
            };

            ws.current = socket;
        };

        connect();

        return () => {
            if (ws.current) ws.current.close();
        };
    }, []);

    return (
        <div className="glass-card rounded-xl p-5 h-full flex flex-col relative overflow-hidden">
            <div className="flex justify-between items-center mb-4 relative z-10">
                <div className="flex items-center gap-2">
                    <div className="relative">
                        <Globe size={18} className="text-blue-400" />
                        <span className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
                    </div>
                    <h3 className="text-slate-200 font-medium text-sm">Live Traffic</h3>
                </div>
                <div className="text-xs text-slate-500 font-mono flex items-center gap-1.5">
                    <Wifi size={12} className="text-emerald-500" />
                    STREAMING
                </div>
            </div>

            <div className="space-y-3 flex-1 overflow-hidden relative z-10">
                <AnimatePresence initial={false}>
                    {logs.map((log) => (
                        <motion.div
                            key={log.id}
                            initial={{ opacity: 0, x: -20, height: 0 }}
                            animate={{ opacity: 1, x: 0, height: 'auto' }}
                            exit={{ opacity: 0, x: 20, height: 0 }}
                            className="flex items-center justify-between text-xs p-2 rounded-lg bg-white/5 border border-white/5"
                        >
                            <div className="flex items-center gap-3">
                                <span className={`w-1.5 h-1.5 rounded-full ${log.status >= 500 ? 'bg-rose-500 shadow-[0_0_5px_rgba(244,63,94,0.5)]' :
                                        log.status >= 400 ? 'bg-amber-500 shadow-[0_0_5px_rgba(245,158,11,0.5)]' :
                                            'bg-emerald-500 shadow-[0_0_5px_rgba(16,185,129,0.5)]'
                                    }`} />
                                <span className="font-mono text-slate-400 w-12">{log.method}</span>
                                <span className="text-slate-300 font-mono truncate max-w-[120px]" title={log.path}>{log.path}</span>
                            </div>
                            <div className="flex items-center gap-3">
                                <span className={`font-mono ${log.status >= 400 ? 'text-rose-400' : 'text-emerald-400'
                                    }`}>{log.status}</span>
                                <span className="text-slate-600 font-mono">{log.timestamp}</span>
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>

                {logs.length === 0 && (
                    <div className="absolute inset-0 flex items-center justify-center text-slate-600 text-xs animate-pulse">
                        Waiting for traffic...
                    </div>
                )}
            </div>

            {/* Matrix rain effect background (subtle) */}
            <div className="absolute inset-x-0 bottom-0 h-20 bg-gradient-to-t from-[#0F172A] to-transparent z-20 pointer-events-none" />
        </div>
    );
};
