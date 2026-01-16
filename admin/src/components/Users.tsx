import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getUsers, type User } from '../lib/api';
import { Ban, Search } from 'lucide-react';
import { cn } from '../lib/utils';
import { motion } from 'framer-motion';

export const Users = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const { data: users = [] } = useQuery({
        queryKey: ['users'],
        queryFn: getUsers,
        // Mock data since endpoint might not exist
        initialData: [
            { id: 'usr_1', name: 'Alex Rivera', email: 'alex@example.com', role: 'admin', plan: 'enterprise', created_at: '2025-12-01' },
            { id: 'usr_2', name: 'Sarah Chen', email: 'sarah@techcorp.com', role: 'developer', plan: 'pro', created_at: '2026-01-10' },
            { id: 'usr_3', name: 'Mike Ross', email: 'mike@startup.io', role: 'viewer', plan: 'free', created_at: '2026-01-15' }
        ] as User[]
    });

    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-5 duration-500">
            <div className="flex justify-between items-center">
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
                    <input
                        type="text"
                        placeholder="Search users..."
                        className="pl-10 pr-4 py-2 bg-[#0F172A] border border-white/10 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 w-64 transition-all"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                </div>
            </div>

            <div className="bg-[#0F172A]/80 backdrop-blur-xl rounded-xl border border-white/10 overflow-hidden shadow-xl">
                <table className="w-full text-left">
                    <thead className="bg-white/5 border-b border-white/5">
                        <tr>
                            <th className="px-6 py-4 font-semibold text-slate-400 text-xs uppercase tracking-wider">User</th>
                            <th className="px-6 py-4 font-semibold text-slate-400 text-xs uppercase tracking-wider">Role</th>
                            <th className="px-6 py-4 font-semibold text-slate-400 text-xs uppercase tracking-wider">Plan</th>
                            <th className="px-6 py-4 font-semibold text-slate-400 text-xs uppercase tracking-wider">Joined</th>
                            <th className="px-6 py-4 font-semibold text-slate-400 text-xs uppercase tracking-wider text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {users.map((user) => (
                            <motion.tr
                                key={user.id}
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="group hover:bg-white/[0.02] transition-colors"
                            >
                                <td className="px-6 py-4">
                                    <div className="flex items-center gap-3">
                                        <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-xs font-bold text-slate-400 border border-white/10">
                                            {user.name.charAt(0)}
                                        </div>
                                        <div>
                                            <div className="font-medium text-slate-200">{user.name}</div>
                                            <div className="text-xs text-slate-500">{user.email}</div>
                                        </div>
                                    </div>
                                </td>
                                <td className="px-6 py-4">
                                    <span className={cn(
                                        "inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border",
                                        user.role === 'admin' ? "bg-purple-500/10 text-purple-400 border-purple-500/20" : "bg-slate-800 text-slate-400 border-slate-700"
                                    )}>
                                        {user.role}
                                    </span>
                                </td>
                                <td className="px-6 py-4">
                                    <span className={cn(
                                        "inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border uppercase tracking-wider",
                                        user.plan === 'enterprise' ? "bg-blue-500/10 text-blue-400 border-blue-500/20" :
                                            user.plan === 'pro' ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" :
                                                "bg-slate-800 text-slate-400 border-slate-700"
                                    )}>
                                        {user.plan}
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-slate-500 text-sm">
                                    {user.created_at}
                                </td>
                                <td className="px-6 py-4 text-right">
                                    <button className="p-2 hover:bg-white/5 rounded-lg text-slate-400 hover:text-rose-400 transition-colors" title="Disable User">
                                        <Ban size={16} />
                                    </button>
                                </td>
                            </motion.tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}
