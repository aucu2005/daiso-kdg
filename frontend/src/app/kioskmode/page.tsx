'use client';

import { Mic, Search, Home, Map as MapIcon, Headphones } from 'lucide-react';
import Header from '@/components/shared/Header';
import BottomNav from '@/components/shared/BottomNav';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';


const categories = [
    { icon: <Home className="w-12 h-12" />, label: '홈', active: true },
    { icon: <MapIcon className="w-12 h-12" />, label: '카테고리/매장지도', href: '/kioskmode/map' },
    { icon: <Headphones className="w-12 h-12" />, label: '고객센터' },
];

export default function KioskVoiceHome() {
    const router = useRouter();
    const [searchQuery, setSearchQuery] = useState('');

    const handleVoiceClick = () => {
        router.push('/kioskmode/voice');
    };

    const handleSearch = () => {
        if (searchQuery.trim()) {
            router.push(`/kioskmode/results?q=${encodeURIComponent(searchQuery)}`);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    };

    return (
        <div className="kiosk-container flex flex-col bg-white">
            <Header />

            {/* Voice Search Section */}
            <section className="h-40 flex items-center justify-center gap-6 bg-white px-8">
                {/* Mic Button */}
                <button
                    onClick={handleVoiceClick}
                    className="w-20 h-20 bg-daiso-red rounded-full flex items-center justify-center shadow-red hover:scale-105 transition-transform"
                >
                    <Mic className="w-10 h-10 text-white" />
                </button>

                {/* Search Input */}
                <div className="w-[700px] h-16 bg-gray-100 rounded-full flex items-center px-8 gap-4 shadow-soft">
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="찾으시는 상품을 말씀해주세요"
                        className="flex-1 bg-transparent text-xl text-gray-700 placeholder-gray-400 outline-none font-pretendard"
                    />
                    <button onClick={handleSearch}>
                        <Search className="w-7 h-7 text-daiso-red" />
                    </button>
                </div>
            </section>

            {/* Carousel Section */}
            <section className="h-[340px] flex items-center justify-center bg-white px-8">
                <div className="w-[1100px] h-[300px] bg-gradient-to-r from-red-500 via-pink-500 to-orange-400 rounded-3xl shadow-medium flex items-center justify-center overflow-hidden">
                    <div className="text-center text-white">
                        <p className="text-2xl font-suite mb-2">🎊 신상품 입고!</p>
                        <h2 className="text-4xl font-suite font-bold mb-4">봄맞이 인테리어 소품</h2>
                        <p className="text-lg opacity-90">지금 B1층에서 만나보세요</p>
                    </div>
                </div>
            </section>

            {/* Category Shortcuts */}
            <section className="flex-1 bg-gray-50 flex items-center justify-center px-8 pt-10">
                <div className="flex gap-16">
                    {categories.map((cat, idx) => (
                        <Link
                            key={idx}
                            href={cat.href || '#'}
                            className="flex flex-col items-center gap-4 group"
                        >
                            <div className={`w-24 h-24 rounded-3xl flex items-center justify-center shadow-soft transition-all group-hover:scale-105 ${cat.active ? 'bg-white text-daiso-red' : 'bg-white text-gray-700'
                                }`}>
                                {cat.icon}
                            </div>
                            <span className="font-suite text-xl font-semibold text-gray-700">
                                {cat.label}
                            </span>
                        </Link>
                    ))}
                </div>
            </section>

        </div>
    );
}
