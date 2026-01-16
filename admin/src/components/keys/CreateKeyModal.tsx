import { useState } from 'react';
import { X, Calendar, Shield, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface CreateKeyModalProps {
    isOpen: boolean;
    onClose: () => void;
    onCreate: (data: { name: string; rateLimit: number; expiration: string }) => void;
}

export const CreateKeyModal = ({ isOpen, onClose, onCreate }: CreateKeyModalProps) => {
    const [name, setName] = useState('');
    const [rateLimit, setRateLimit] = useState(1000);
    const [expiration, setExpiration] = useState('never');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onCreate({ name, rateLimit, expiration });
        onClose();
        setName('');
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
                        onClick={onClose}
                    />
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-[#0F172A] border border-white/10 rounded-xl shadow-2xl z-50 overflow-hidden"
                    >
                        <div className="p-6 border-b border-white/5 flex justify-between items-center bg-white/5">
                            <h2 className="text-lg font-semibold text-white">Create API Key</h2>
                            <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
                                <X size={20} />
                            </button>
                        </div>

                        <form onSubmit={handleSubmit} className="p-6 space-y-6">
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-300">Key Name</label>
                                <input
                                    type="text"
                                    placeholder="e.g. Production Service A"
                                    className="w-full bg-slate-950 border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
                                    autoFocus
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    required
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
                                        <Zap size={14} className="text-amber-400" /> Rate Limit
                                    </label>
                                    <select
                                        className="w-full bg-slate-950 border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
                                        value={rateLimit}
                                        onChange={(e) => setRateLimit(Number(e.target.value))}
                                    >
                                        <option value={100}>100 req/s</option>
                                        <option value={1000}>1k req/s</option>
                                        <option value={5000}>5k req/s</option>
                                        <option value={0}>Unlimited</option>
                                    </select>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
                                        <Calendar size={14} className="text-blue-400" /> Expiration
                                    </label>
                                    <select
                                        className="w-full bg-slate-950 border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
                                        value={expiration}
                                        onChange={(e) => setExpiration(e.target.value)}
                                    >
                                        <option value="never">Never</option>
                                        <option value="30d">30 Days</option>
                                        <option value="90d">90 Days</option>
                                        <option value="1y">1 Year</option>
                                    </select>
                                </div>
                            </div>

                            <div className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/20 text-xs text-blue-200 flex items-start gap-2">
                                <Shield size={14} className="mt-0.5 shrink-0" />
                                <p>This key will be generated with full access permissions. You can edit scopes later.</p>
                            </div>

                            <div className="flex justify-end gap-3 pt-2">
                                <button type="button" onClick={onClose} className="px-4 py-2 text-sm font-medium text-slate-400 hover:text-white transition-colors">
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors shadow-lg shadow-blue-500/20"
                                >
                                    Create Key
                                </button>
                            </div>
                        </form>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
};
