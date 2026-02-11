'use client';

import { Wifi } from 'lucide-react';
import { useEffect, useState } from 'react';

interface HeaderProps {
    showBack?: boolean;
    title?: string;
    onBack?: () => void;
}

export default function Header({ showBack = false, title, onBack }: HeaderProps) {
    const [currentTime, setCurrentTime] = useState('');

    useEffect(() => {
        const updateTime = () => {
            const now = new Date();
            const hours = now.getHours();
            const minutes = now.getMinutes().toString().padStart(2, '0');
            const period = hours >= 12 ? 'PM' : 'AM';
            const displayHours = hours % 12 || 12;
            setCurrentTime(`${displayHours}:${minutes} ${period}`);
        };

        updateTime();
        const interval = setInterval(updateTime, 1000);
        return () => clearInterval(interval);
    }, []);

    return (
        <header className="w-full h-header bg-white shadow-soft px-8 flex items-center justify-between">
            {/* Left: Logo or Back */}
            <div className="flex items-center gap-3">
                {showBack ? (
                    <button
                        onClick={onBack}
                        className="flex items-center gap-2 text-gray-700 hover:text-daiso-red transition-colors"
                    >
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M15 18l-6-6 6-6" />
                        </svg>
                        <span className="font-suite font-semibold text-lg">뒤로</span>
                    </button>
                ) : (
                    <>
                        <div className="w-10 h-10 bg-daiso-red rounded-lg flex items-center justify-center">
                            <span className="text-white font-bold font-suite">D</span>
                        </div>
                        <span className="font-suite text-2xl font-extrabold text-daiso-red">
                            어디다있소
                        </span>
                    </>
                )}
            </div>

            {/* Center: Title (optional) */}
            {title && (
                <h1 className="font-suite text-xl font-bold text-gray-700 absolute left-1/2 transform -translate-x-1/2">
                    {title}
                </h1>
            )}

            {/* Right: Time & Status */}
            <div className="flex items-center gap-6">
                <span className="font-suite font-semibold text-gray-700">
                    {currentTime}
                </span>
                <Wifi className="w-5 h-5 text-gray-700" />
            </div>
        </header>
    );
}
