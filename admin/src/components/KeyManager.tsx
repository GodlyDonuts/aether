import { useState } from 'react';
import { Plus, Trash2, Key, Copy, Check, Search, Filter, Eye, EyeOff } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { createApiKey, getApiKeys, revokeApiKey } from '../lib/api';
import { CreateKeyModal } from './keys/CreateKeyModal';
import { cn } from '../lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

export const KeyManager = () => {
    const queryClient = useQueryClient();
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [copiedId, setCopiedId] = useState<string | null>(null);
    const [visibleKeys, setVisibleKeys] = useState<Set<string>>(new Set());

    const { data: keys = [], isLoading } = useQuery({
        queryKey: ['keys'],
        queryFn: getApiKeys
    });

    const createMutation = useMutation({
        mutationFn: ({ name }: { name: string; rateLimit: number; expiration: string }) => createApiKey(name),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['keys'] });
        }
    });

    const revokeMutation = useMutation({
        mutationFn: revokeApiKey,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['keys'] });
        }
    });

    const handleCreate = (data: { name: string; rateLimit: number; expiration: string }) => {
        createMutation.mutate(data);
    };

    const toggleVisibility = (id: string) => {
        const newVisible = new Set(visibleKeys);
        if (newVisible.has(id)) {
            newVisible.delete(id);
        } else {
            newVisible.add(id);
        }
        setVisibleKeys(newVisible);
    };

    const copyToClipboard = (text: string, id: string) => {
        navigator.clipboard.writeText(text);
        setCopiedId(id);
        setTimeout(() => setCopiedId(null), 2000);
    };

    const filteredKeys = keys.filter(k =>
        k.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        k.id.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-5 duration-500">
            <div className="flex justify-between items-center">
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
                    <input
                        type="text"
                        placeholder="Search keys..."
                        className="pl-10 pr-4 py-2 bg-[#0F172A] border border-white/10 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 w-64 transition-all"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                </div>
                <div className="flex gap-2">
                    <button className="px-3 py-2 bg-[#0F172A] border border-white/10 rounded-lg text-slate-400 hover:text-white transition-colors">
                        <Filter size={18} />
                    </button>
                    <button
                        onClick={() => setIsCreateModalOpen(true)}
                        className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 shadow-lg shadow-blue-900/20 transition-all hover:scale-105"
                    >
                        <Plus size={16} />
                        Create New Key
                    </button>
                </div>
            </div>

            <div className="bg-[#0F172A]/80 backdrop-blur-xl rounded-xl border border-white/10 overflow-hidden shadow-xl">
                <table className="w-full text-left">
                    <thead className="bg-white/5 border-b border-white/5">
                        <tr>
                            <th className="px-6 py-4 font-semibold text-slate-400 text-xs uppercase tracking-wider">Key Details</th>
                            <th className="px-6 py-4 font-semibold text-slate-400 text-xs uppercase tracking-wider">Usage Limit</th>
                            <th className="px-6 py-4 font-semibold text-slate-400 text-xs uppercase tracking-wider">Status</th>
                            <th className="px-6 py-4 font-semibold text-slate-400 text-xs uppercase tracking-wider text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {isLoading ? (
                            <tr><td colSpan={4} className="p-8 text-center text-slate-500 animate-pulse">Loading secure keys...</td></tr>
                        ) : filteredKeys.length === 0 ? (
                            <tr><td colSpan={4} className="p-12 text-center text-slate-500">No keys found matching your search.</td></tr>
                        ) : (
                            <AnimatePresence>
                                {filteredKeys.map((key) => (
                                    <motion.tr
                                        key={key.id}
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        exit={{ opacity: 0 }}
                                        className="group hover:bg-white/[0.02] transition-colors"
                                    >
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-3">
                                                <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center border border-blue-500/20">
                                                    <Key size={14} className="text-blue-400" />
                                                </div>
                                                <div>
                                                    <div className="font-medium text-slate-200">{key.name}</div>
                                                    <div className="flex items-center gap-2 mt-1">
                                                        <code className="text-xs font-mono text-slate-500 bg-white/5 px-1.5 py-0.5 rounded">
                                                            {visibleKeys.has(key.id) ? key.key : `${key.key.substring(0, 8)}...`}
                                                        </code>
                                                        <button
                                                            onClick={() => toggleVisibility(key.id)}
                                                            className="text-slate-600 hover:text-slate-400"
                                                        >
                                                            {visibleKeys.has(key.id) ? <EyeOff size={12} /> : <Eye size={12} />}
                                                        </button>
                                                        <button
                                                            onClick={() => copyToClipboard(key.key, key.id)}
                                                            className="text-slate-600 hover:text-blue-400"
                                                        >
                                                            {copiedId === key.id ? <Check size={12} className="text-emerald-500" /> : <Copy size={12} />}
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="w-48">
                                                <div className="flex justify-between text-xs mb-1.5">
                                                    <span className="text-slate-400">Monthly Usage</span>
                                                    <span className="text-slate-300 font-mono">{(key.usage_month || 0) / 1000}k / {(key.usage_limit || 100) / 1000}k</span>
                                                </div>
                                                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                                                    <motion.div
                                                        initial={{ width: 0 }}
                                                        animate={{ width: `${Math.min(((key.usage_month || 0) / (key.usage_limit || 100)) * 100, 100)}%` }}
                                                        className={cn(
                                                            "h-full rounded-full",
                                                            (key.usage_month || 0) > (key.usage_limit || 100) * 0.9 ? "bg-rose-500" : "bg-blue-500"
                                                        )}
                                                    />
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className={cn(
                                                "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border",
                                                key.status === 'active'
                                                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                                                    : "bg-rose-500/10 text-rose-400 border-rose-500/20"
                                            )}>
                                                <div className={cn(
                                                    "w-1.5 h-1.5 rounded-full mr-1.5",
                                                    key.status === 'active' ? "bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.5)]" : "bg-rose-400"
                                                )} />
                                                {key.status.toUpperCase()}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <div className="relative inline-block text-left">
                                                <button
                                                    className="p-2 hover:bg-white/5 rounded-lg text-slate-400 hover:text-white transition-colors"
                                                    onClick={() => {
                                                        if (confirm('Revoke key?')) revokeMutation.mutate(key.id);
                                                    }}
                                                >
                                                    <Trash2 size={16} className="text-rose-500/70 hover:text-rose-400" />
                                                </button>
                                            </div>
                                        </td>
                                    </motion.tr>
                                ))}
                            </AnimatePresence>
                        )}
                    </tbody>
                </table>
            </div>

            <CreateKeyModal
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
                onCreate={handleCreate}
            />
        </div>
    );
};
