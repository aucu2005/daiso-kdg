'use client';

import { ArrowLeft, Map, Camera } from 'lucide-react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Suspense } from 'react';

function MobileContent() {
    const searchParams = useSearchParams();
    const router = useRouter();

    const productName = searchParams.get('name') || '규조토 욕실 매트';
    const shelf = searchParams.get('shelf') || 'B1-B01';

    return (
        <div className="mobile-container flex flex-col bg-gray-50 mx-auto">
            {/* Header */}
            <header className="h-14 bg-white px-4 flex items-center justify-between">
                <button
                    onClick={() => router.back()}
                    className="p-2 -ml-2"
                >
                    <ArrowLeft className="w-6 h-6 text-gray-700" />
                </button>
                <div className="flex items-center">
                    <span className="font-suite text-xl font-extrabold text-gray-700">어디</span>
                    <span className="font-suite text-xl font-extrabold text-daiso-red">다이소</span>
                </div>
                <div className="w-10" /> {/* Spacer for centering */}
            </header>

            {/* Map Area */}
            <div className="flex-1 bg-white relative">
                {/* Placeholder Map */}
                <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                        <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                            <Map className="w-10 h-10 text-gray-400" />
                        </div>
                        <p className="text-gray-400">지도 영역</p>
                        <p className="text-sm text-gray-300 mt-1">터치하여 확대</p>
                    </div>
                </div>

                {/* Floor indicator */}
                <div className="absolute top-4 left-4 flex gap-2">
                    <button className="px-4 py-2 bg-daiso-red text-white rounded-full text-sm font-bold">
                        B1
                    </button>
                    <button className="px-4 py-2 bg-gray-200 text-gray-600 rounded-full text-sm">
                        B2
                    </button>
                </div>

                {/* Zoom controls */}
                <div className="absolute right-4 top-1/2 -translate-y-1/2 flex flex-col gap-2">
                    <button className="w-10 h-10 bg-white shadow-soft rounded-full flex items-center justify-center text-gray-600 text-xl">
                        +
                    </button>
                    <button className="w-10 h-10 bg-white shadow-soft rounded-full flex items-center justify-center text-gray-600 text-xl">
                        −
                    </button>
                </div>
            </div>

            {/* Bottom Sheet */}
            <div className="h-52 bg-white rounded-t-3xl shadow-[0_-4px_16px_rgba(0,0,0,0.08)] p-5 flex flex-col gap-4">
                {/* Product Card */}
                <div className="flex items-center gap-4">
                    <div className="w-[70px] h-[70px] bg-gray-100 rounded-xl flex items-center justify-center">
                        <span className="text-3xl">🧴</span>
                    </div>
                    <div className="flex-1">
                        <h3 className="font-suite text-lg font-bold text-gray-800">
                            {productName}
                        </h3>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="font-suite font-semibold text-gray-700">
                                {shelf}
                            </span>
                            <span className="text-gray-500 text-sm">
                                약 30초 소요
                            </span>
                        </div>
                    </div>
                </div>

                {/* Button Row */}
                <div className="flex gap-3">
                    <button className="flex-1 h-12 bg-daiso-red text-white rounded-xl flex items-center justify-center gap-2 font-suite font-bold">
                        <Map className="w-5 h-5" />
                        지도 보기
                    </button>
                    <button className="flex-1 h-12 bg-white text-daiso-red border-2 border-daiso-red rounded-xl flex items-center justify-center gap-2 font-suite font-bold">
                        <Camera className="w-5 h-5" />
                        AR 네비
                    </button>
                </div>
            </div>
        </div>
    );
}

export default function MobilePage() {
    return (
        <Suspense fallback={<div className="mobile-container flex items-center justify-center">Loading...</div>}>
            <MobileContent />
        </Suspense>
    );
}
