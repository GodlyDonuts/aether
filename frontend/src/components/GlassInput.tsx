import { useState, KeyboardEvent } from 'react';

interface GlassInputProps {
    onSend: (message: string) => void;
    disabled?: boolean;
}

export const GlassInput = ({ onSend, disabled }: GlassInputProps) => {
    const [input, setInput] = useState('');

    const handleSend = () => {
        if (input.trim() && !disabled) {
            onSend(input);
            setInput('');
        }
    };

    const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div
            style={{
                width: '100%',
                maxWidth: '768px',
                margin: '0 auto',
                padding: '0 20px 120px 20px',
                boxSizing: 'border-box',
                position: 'relative'
            }}
        >
            <div style={{
                position: 'relative',
                borderRadius: '30px',
                background: 'rgba(255, 255, 255, 0.5)',
                backdropFilter: 'blur(20px)',
                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
                border: '1px solid rgba(255, 255, 255, 0.4)',
                transition: 'all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1)',
                display: 'flex',
                alignItems: 'center',
                padding: '8px 8px 8px 24px',
            }}>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask anything"
                    disabled={disabled}
                    style={{
                        flex: 1,
                        background: 'transparent',
                        border: 'none',
                        outline: 'none',
                        fontSize: '16px',
                        color: '#1d1d1f',
                        paddingRight: '12px',
                        fontWeight: 400
                    }}
                />
                <button
                    onClick={handleSend}
                    disabled={!input.trim() || disabled}
                    style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '50%',
                        border: 'none',
                        background: input.trim() ? '#1d1d1f' : '#e5e5e5', // Black when active
                        color: 'white',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        cursor: input.trim() && !disabled ? 'pointer' : 'default',
                        transition: 'background 0.2s ease',
                        flexShrink: 0
                    }}
                >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <line x1="12" y1="19" x2="12" y2="5"></line>
                        <polyline points="5 12 12 5 19 12"></polyline>
                    </svg>
                </button>
            </div>
        </div>
    );
};
