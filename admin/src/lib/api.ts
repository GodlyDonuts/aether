import axios from 'axios';

const API_URL = 'http://localhost:8000/admin';

export const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export interface User {
    id: string;
    email: string;
    name: string;
    role: 'admin' | 'developer' | 'viewer';
    avatar_url?: string;
    created_at: string;
    plan: 'free' | 'pro' | 'enterprise';
}

export interface ApiKey {
    id: string;
    name: string;
    key: string; // The partial or full key depending on context (usually hidden)
    created_at: string;
    last_used_at?: string;
    status: 'active' | 'revoked';
    scopes: string[];
    rate_limit: number;
    usage_month: number;
    usage_limit: number;
}

export interface Transaction {
    id: string;
    user_id: string;
    amount: number;
    currency: string;
    status: 'succeeded' | 'pending' | 'failed';
    created_at: string;
}

export interface UsageMetrics {
    period_start: string;
    period_end: string;
    total_requests: number;
    failed_requests: number;
    latency_p95: number;
}

export interface AuditLog {
    id: string;
    action: string;
    actor_id: string;
    target_id?: string;
    timestamp: string;
    metadata?: Record<string, any>;
}

export interface Stats {
    total_requests: number;
    active_users: number;
    revenue: number;
    mrr: number;
    churn_rate: number;
    system_latency: number;
    error_rate: number;
    history: Array<{
        timestamp: string;
        requests: number;
        revenue: number;
    }>;
}

// API Methods
export const getApiKeys = async (): Promise<ApiKey[]> => {
    const { data } = await api.get<ApiKey[]>('/keys');
    return data;
};

export const createApiKey = async (name: string, options?: { expiration?: string; rate_limit?: number }): Promise<ApiKey> => {
    const { data } = await api.post<ApiKey>('/keys', { name, ...options });
    return data;
};

export const revokeApiKey = async (id: string): Promise<void> => {
    await api.delete(`/keys/${id}`);
};

export const getStats = async (): Promise<Stats> => {
    const { data } = await api.get<Stats>('/stats');
    return data;
};

export const getUsers = async (): Promise<User[]> => {
    const { data } = await api.get<User[]>('/users');
    return data;
};
