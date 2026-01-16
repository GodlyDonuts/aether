import { useState, useRef, useEffect } from 'react';
import type { Message, ChatResponse } from '../types';
import { MessageBubble } from './MessageBubble';
import { GlassInput } from './GlassInput';

import { useNavigate } from 'react-router-dom';

export const ChatInterface = () => {
    const navigate = useNavigate();
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const [demoMode, setDemoMode] = useState(false);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (text: string, image?: string) => {
        // ... (rest of function unchanged)
        const userMsg: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: text,
            image: image,
            timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, userMsg]);
        setIsLoading(true);

        try {
            const response = await fetch('http://localhost:8000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: text,
                    image: image,
                    demo_mode: demoMode
                }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data: ChatResponse = await response.json();

            const aiMsg: Message = {
                id: Date.now().toString() + '_ai',
                role: 'assistant',
                content: data.response,
                nudge: data.nudge_details,
                timestamp: new Date().toISOString()
            };

            setMessages(prev => [...prev, aiMsg]);

        } catch (error) {
            console.error('Error sending message:', error);
            const errorMsg: Message = {
                id: Date.now().toString() + '_error',
                role: 'assistant',
                content: "Something went wrong. Please check the connection.",
                timestamp: new Date().toISOString()
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div style={{
            width: '100vw',
            height: '100vh',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: messages.length === 0 ? 'center' : 'space-between',
            alignItems: 'center',
            position: 'relative'
        }}>
            {/* Header / Logo - Always visible now for stats access */}
            <div style={{
                position: 'absolute',
                top: '20px',
                left: '40px',
                right: '40px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                zIndex: 10
            }}>
                <div style={{
                    fontSize: '14px',
                    fontWeight: 600,
                    color: '#86868b',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px'
                }}>
                    AXON
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                className="sr-only peer"
                                checked={demoMode}
                                onChange={(e) => setDemoMode(e.target.checked)}
                            />
                            <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
                            <span className="ml-2 text-xs font-medium text-gray-500">Demo Mode</span>
                        </label>
                    </div>
                </div>
                <button
                    onClick={() => navigate('/analytics')}
                    style={{
                        padding: '8px 16px',
                        background: 'rgba(0,0,0,0.05)',
                        border: 'none',
                        borderRadius: '20px',
                        fontSize: '13px',
                        fontWeight: 500,
                        color: '#1d1d1f',
                        cursor: 'pointer',
                        transition: 'background 0.2s'
                    }}
                >
                    Stats
                </button>
            </div>


            {/* Content Area */}
            <div style={{
                flex: 1,
                width: '100%',
                maxWidth: '768px',
                padding: '80px 20px 20px 20px',
                boxSizing: 'border-box',
                overflowY: 'auto',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: messages.length === 0 ? 'center' : 'flex-start',
            }}>
                {messages.length === 0 ? (
                    <div style={{
                        textAlign: 'center',
                        marginBottom: '40px',
                        animation: 'fadeIn 0.5s ease-out'
                    }}>
                        <h1 style={{
                            fontSize: '32px',
                            fontWeight: 600,
                            letterSpacing: '-0.02em',
                            margin: '0 0 10px 0',
                            color: '#1d1d1f'
                        }}>
                            What can I help with?
                        </h1>
                    </div>
                ) : (
                    <>
                        {messages.map((msg) => (
                            <MessageBubble key={msg.id} message={msg} />
                        ))}
                        {isLoading && (
                            <div style={{
                                alignSelf: 'flex-start',
                                color: '#86868b',
                                fontSize: '14px',
                                paddingLeft: '16px',
                                animation: 'fadeIn 0.3s'
                            }}>
                                Thinking...
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </>
                )}
            </div>

            {/* Input Area */}
            <GlassInput onSend={handleSend} disabled={isLoading} />
        </div>
    );
};
