import { AreaChart, Area, XAxis, Tooltip, ResponsiveContainer } from 'recharts';

interface SyncChartsProps {
    data: any[];
}

export const SyncCharts = ({ data }: SyncChartsProps) => {
    return (
        <div className="grid grid-rows-2 gap-4 h-[400px]">
            {/* Request Volume */}
            <div className="glass-card rounded-xl p-6 border border-white/5">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Request Volume</h3>
                    <span className="text-xs text-blue-400 font-mono">sync-id: metrics</span>
                </div>
                <div className="h-[140px]">
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={data} syncId="metrics">
                            <defs>
                                <linearGradient id="colorRequests" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <Tooltip
                                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', color: '#e2e8f0' }}
                                itemStyle={{ color: '#94a3b8' }}
                            />
                            <Area type="monotone" dataKey="requests" stroke="#3b82f6" strokeWidth={2} fill="url(#colorRequests)" />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Revenue */}
            <div className="glass-card rounded-xl p-6 border border-white/5">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Revenue Stream</h3>
                </div>
                <div className="h-[140px]">
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={data} syncId="metrics">
                            <defs>
                                <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <XAxis dataKey="timestamp" hide />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', color: '#e2e8f0' }}
                                itemStyle={{ color: '#94a3b8' }}
                            />
                            <Area type="monotone" dataKey="revenue" stroke="#10b981" strokeWidth={2} fill="url(#colorRevenue)" />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};
