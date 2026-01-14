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
                    letterSpacing: '-0.01em'
                }}
            >
                {message.content}
            </div>
        </div>
    );
};
