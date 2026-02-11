'use client';

import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import Header from '@/components/shared/Header';

export default function VoiceInputPage() {
    const router = useRouter();
    const [transcript, setTranscript] = useState('"세탁 세제 어디 있어요?"');
    const [isListening, setIsListening] = useState(true);

    // Simulated waveform bars
    const bars = Array.from({ length: 13 }, (_, i) => ({
        id: i,
        delay: i * 0.1,
    }));

    const handleCancel = () => {
        router.back();
    };

    const handleConfirm = () => {
        // Extract search query from transcript
        const query = transcript.replace(/[""]/g, '').replace('어디 있어요?', '').trim();
        router.push(`/kioskmode/results?q=${encodeURIComponent(query || '세탁 세제')}`);
    };

    return (
        <div className="kiosk-container flex flex-col bg-white">
            <Header />

            <main className="flex-1 bg-gray-50 flex flex-col items-center justify-center gap-12">
                {/* Listening Text */}
                <h1 className="font-suite text-5xl font-bold text-gray-700">
                    듣고 있습니다...
                </h1>

                {/* Waveform Animation */}
                <div className="flex items-center justify-center gap-1 h-20">
                    {bars.map((bar) => (
                        <div
                            key={bar.id}
                            className="w-1.5 bg-daiso-red rounded-full animate-wave-bar"
                            style={{
                                height: `${20 + Math.random() * 60}px`,
                                animationDelay: `${bar.delay}s`,
                            }}
                        />
                    ))}
                </div>

                {/* User Input Display */}
                <p className="font-suite text-3xl font-semibold text-gray-600">
                    {transcript}
                </p>

                {/* Action Buttons */}
                <div className="flex gap-6">
                    <button
                        onClick={handleCancel}
                        className="w-40 h-14 bg-gray-100 rounded-full font-suite text-xl font-semibold text-gray-600 shadow-soft hover:bg-gray-200 transition-colors"
                    >
                        취소
                    </button>
                    <button
                        onClick={handleConfirm}
                        className="w-40 h-14 bg-daiso-red rounded-full font-suite text-xl font-bold text-white shadow-red hover:bg-daiso-red-dark transition-colors"
                    >
                        확인
                    </button>
                </div>
            </main>
        </div>
    );
}
