import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import type { Message } from '../types';

interface MessageBubbleProps {
    message: Message;
}

export const MessageBubble = ({ message }: MessageBubbleProps) => {
    const isUser = message.role === 'user';

    return (
        <div
            style={{
                display: 'flex',
                justifyContent: isUser ? 'flex-end' : 'flex-start',
                marginBottom: '24px',
                animation: 'fadeIn 0.3s ease-out'
            }}
        >
            <div
                style={{
                    maxWidth: '70%',
                    padding: '10px 16px',
                    borderRadius: '24px',
                    background: isUser
                        ? '#f4f4f4' // Minimal grey for user
                        : 'transparent', // Transparent for AI
                    color: '#1d1d1f',
                    fontSize: '16px',
                    lineHeight: '1.6',
                    letterSpacing: '-0.01em',
                    textAlign: 'left',
                    overflowWrap: 'anywhere', // Force breaks for long URLs
                    wordBreak: 'break-word'   // Fallback
                }}
            >
                {isUser ? (
                    message.content
                ) : (
                    <ReactMarkdown
                        remarkPlugins={[remarkMath]}
                        rehypePlugins={[rehypeKatex]}
                        components={{
                            // Style markdown elements to match Apple aesthetic
                            p: ({ children }) => <p style={{ margin: '0 0 10px 0' }}>{children}</p>,
                            ul: ({ children }) => <ul style={{ paddingLeft: '20px', margin: '10px 0' }}>{children}</ul>,
                            ol: ({ children }) => <ol style={{ paddingLeft: '20px', margin: '10px 0' }}>{children}</ol>,
                            li: ({ children }) => <li style={{ marginBottom: '4px' }}>{children}</li>,
                            strong: ({ children }) => <strong style={{ fontWeight: 600 }}>{children}</strong>,
                            em: ({ children }) => <em style={{ fontStyle: 'italic' }}>{children}</em>,
                            a: ({ children, href }) => (
                                <a
                                    href={href}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    style={{ color: '#0066cc', textDecoration: 'none', cursor: 'pointer' }}
                                    onMouseOver={(e) => e.currentTarget.style.textDecoration = 'underline'}
                                    onMouseOut={(e) => e.currentTarget.style.textDecoration = 'none'}
                                >
                                    {children}
                                </a>
                            ),
                        }}
                    >
                        {message.content}
                    </ReactMarkdown>
                )}
            </div>
            <style>{`
                @keyframes fadeIn {
                  from { opacity: 0; transform: translateY(10px); }
                  to { opacity: 1; transform: translateY(0); }
                }
                /* Remove bottom margin from last paragraph in markdown */
                div > p:last-child {
                    margin-bottom: 0 !important;
                }
              `}</style>
        </div>
    );
};
