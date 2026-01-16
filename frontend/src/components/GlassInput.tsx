import { useState, useRef, type KeyboardEvent, type ChangeEvent } from 'react';
import { Paperclip, X } from 'lucide-react';

interface GlassInputProps {
    onSend: (message: string, image?: string) => void;
    disabled?: boolean;
}

export const GlassInput = ({ onSend, disabled }: GlassInputProps) => {
    const [input, setInput] = useState('');
    const [selectedImage, setSelectedImage] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleSend = () => {
        if ((input.trim() || selectedImage) && !disabled) {
            onSend(input, selectedImage || undefined);
            setInput('');
            setSelectedImage(null);
        }
    };

    const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                const result = reader.result as string;
                setSelectedImage(result);
            };
            reader.readAsDataURL(file);
        }
    };

    const triggerFileSelect = () => {
        fileInputRef.current?.click();
    };

    const clearImage = () => {
        setSelectedImage(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
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
            {/* Image Preview */}
            {selectedImage && (
                <div style={{
                    position: 'absolute',
                    top: '-100px',
                    left: '40px',
                    width: '80px',
                    height: '80px',
                    borderRadius: '12px',
                    overflow: 'hidden',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                    border: '2px solid white',
                    animation: 'fadeIn 0.2s ease-out'
                }}>
                    <img
                        src={selectedImage}
                        alt="Upload preview"
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    />
                    <button
                        onClick={clearImage}
                        style={{
                            position: 'absolute',
                            top: '4px',
                            right: '4px',
                            width: '20px',
                            height: '20px',
                            borderRadius: '50%',
                            background: 'rgba(0,0,0,0.5)',
                            color: 'white',
                            border: 'none',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            cursor: 'pointer'
                        }}
                    >
                        <X size={12} />
                    </button>
                </div>
            )}

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
                padding: '8px 8px 8px 16px',
            }}>
                <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileSelect}
                    accept="image/*"
                    style={{ display: 'none' }}
                />

                <button
                    onClick={triggerFileSelect}
                    disabled={disabled}
                    style={{
                        background: 'transparent',
                        border: 'none',
                        color: '#86868b',
                        cursor: disabled ? 'default' : 'pointer',
                        padding: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        marginRight: '4px'
                    }}
                >
                    <Paperclip size={20} />
                </button>

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
                    disabled={(!input.trim() && !selectedImage) || disabled}
                    style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '50%',
                        border: 'none',
                        background: (input.trim() || selectedImage) ? '#1d1d1f' : '#e5e5e5', // Black when active
                        color: 'white',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        cursor: (input.trim() || selectedImage) && !disabled ? 'pointer' : 'default',
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
