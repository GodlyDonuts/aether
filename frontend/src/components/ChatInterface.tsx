import { useState, useRef, useEffect } from 'react';
import type { Message, ChatResponse } from '../types';
import { MessageBubble } from './MessageBubble';
import { GlassInput } from './GlassInput';

export const ChatInterface = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (text: string) => {
        const userMsg: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: text,
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
                body: JSON.stringify({ message: text }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data: ChatResponse = await response.json();

            const aiMsg: Message = {
                id: Date.now().toString() + '_ai',
                role: 'assistant',
                content: data.response,
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
            {/* Header / Logo - Only visible when minimal */}
            {messages.length > 0 && (
                <div style={{
                    position: 'absolute',
                    top: '20px',
                    left: '20px',
                    fontSize: '14px',
                    fontWeight: 600,
                    color: '#86868b',
                    zIndex: 10
                }}>
                    AXON
                </div>
            )}


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
