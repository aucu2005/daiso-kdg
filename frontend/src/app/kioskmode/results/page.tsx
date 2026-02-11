'use client';

import mapB1 from '../../../assets/images/map_b1.jpg';
import mapB2 from '../../../assets/images/map_b2.jpg';

import { useSearchParams, useRouter } from 'next/navigation';
import { Suspense, useEffect } from 'react';
import Header from '@/components/shared/Header';
import BottomNav from '@/components/shared/BottomNav';
import { QrCode, ChevronRight, Loader2, MessageSquareWarning } from 'lucide-react';
import { useSearchStore } from '@/store/searchStore';
import { Product } from '@/lib/api';

import { getZoneFromCategory } from '@/utils/categoryMap';
import { DEFAULT_B1_ZONES, DEFAULT_B2_ZONES, MapZone } from '@/utils/mapZones';
import Link from 'next/link';
import { useAllMapZones } from '@/hooks/useMapZones';

function SearchResultsContent() {
    const searchParams = useSearchParams();
    const router = useRouter();
    const query = searchParams.get('q') || '';

    const {
        response,
        selectedProduct,
        isLoading,
        error,
        performSearch,
        selectProduct
    } = useSearchStore();

    useEffect(() => {
        if (query) {
            performSearch(query);
        }
    }, [query]);

    // Handle clarification or unsupported intents
    const needsClarification = response?.needs_clarification;
    const generatedQuestion = response?.generated_question;
    const isUnsupported = response?.intent === 'UNSUPPORTED';

    if (isLoading) {
        return (
            <div className="kiosk-container flex flex-col bg-white">
                <Header showBack title="검색 중..." onBack={() => router.back()} />
                <div className="flex-1 flex flex-col items-center justify-center gap-4">
                    <Loader2 className="w-16 h-16 text-daiso-red animate-spin" />
                    <p className="font-suite text-2xl text-gray-600">"{query}" 상품을 찾고 있습니다...</p>
                </div>
                <BottomNav />
            </div>
        );
    }

    if (error) {
        return (
            <div className="kiosk-container flex flex-col bg-white">
                <Header showBack title="오류 발생" onBack={() => router.back()} />
                <div className="flex-1 flex flex-col items-center justify-center gap-4">
                    <MessageSquareWarning className="w-16 h-16 text-gray-400" />
                    <p className="font-suite text-2xl text-gray-600">{error}</p>
                    <button onClick={() => window.location.reload()} className="px-6 py-3 bg-gray-200 rounded-full font-bold">다시 시도</button>
                </div>
                <BottomNav />
            </div>
        );
    }

    if (!isLoading && !response && query) {
        return null; // Initial state before fetch
    }

    // Clarification / Unsupported UI
    if (needsClarification || isUnsupported) {
        return (
            <div className="kiosk-container flex flex-col bg-white">
                <Header showBack title="안내" onBack={() => router.back()} />
                <div className="flex-1 flex flex-col items-center justify-center gap-8 p-12 text-center">
                    <div className="w-24 h-24 bg-red-50 rounded-full flex items-center justify-center">
                        <MessageSquareWarning className="w-12 h-12 text-daiso-red" />
                    </div>
                    <h2 className="font-suite text-3xl font-bold text-gray-800">
                        {generatedQuestion || "죄송합니다. 찾으시는 상품을 이해하지 못했습니다."}
                    </h2>
                    <p className="text-xl text-gray-500">
                        다른 단어로 다시 검색해보시겠어요?
                    </p>
                    <button
                        onClick={() => router.push('/kioskmode')}
                        className="px-8 py-4 bg-daiso-red text-white rounded-full text-xl font-bold shadow-soft hover:bg-daiso-red-dark"
                    >
                        다시 검색하기
                    </button>
                </div>
                <BottomNav />
            </div>
        );
    }

    // Product List
    const products = response?.products || [];

    return (
        <div className="kiosk-container flex flex-col bg-gray-50">
            <Header showBack title="검색 결과" onBack={() => {
                router.push('/kioskmode');
            }} />

            <main className="flex-1 flex overflow-hidden">
                {/* Left Panel - Product List */}
                <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
                    {/* Search Query Display */}
                    <div className="p-4 border-b border-gray-100">
                        <p className="text-sm text-gray-500">검색어</p>
                        <p className="font-suite font-bold text-lg text-gray-800">"{query}"</p>
                    </div>

                    {/* Product Cards */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-3">
                        {products.length === 0 ? (
                            <div className="text-center py-10 text-gray-400">
                                검색 결과가 없습니다.
                            </div>
                        ) : (
                            products.map((product) => {
                                const zoneInfo = getZoneFromCategory(product.category_major, product.category_middle);
                                const floor = zoneInfo?.floor || product.floor || 'B1';
                                const zoneName = zoneInfo?.zone || '기타';
                                const location = product.location || '';
                                return (
                                    <button
                                        key={product.id}
                                        onClick={() => selectProduct(product)}
                                        className={`w-full p-4 rounded-xl text-left transition-all ${selectedProduct?.id === product.id
                                            ? 'bg-red-50 border-2 border-daiso-red'
                                            : 'bg-gray-50 border border-gray-200 hover:bg-gray-100'
                                            }`}
                                    >
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="font-suite font-bold text-gray-800 line-clamp-2">
                                                {product.name}
                                            </span>
                                            <ChevronRight className={`w-5 h-5 ${selectedProduct?.id === product.id ? 'text-daiso-red' : 'text-gray-400'}`} />
                                        </div>
                                        <div className="flex items-center gap-3 text-sm">
                                            <span className="px-2 py-1 bg-gray-800 text-white rounded text-xs font-bold">
                                                {floor}
                                            </span>
                                            <span className="text-gray-600 font-bold">{zoneName} {location && `(${location})`}</span>
                                            <span className="text-daiso-red font-bold ml-auto">{product.price.toLocaleString()}원</span>
                                        </div>
                                    </button>
                                );
                            })
                        )}
                    </div>

                    {/* QR Code Section */}
                    <div className="p-4 border-t border-gray-200 bg-gray-50">
                        <div className="flex items-center gap-3 mb-3">
                            <QrCode className="w-5 h-5 text-daiso-red" />
                            <span className="font-suite font-semibold text-gray-700">
                                모바일로 길안내
                            </span>
                        </div>
                        <div className="w-32 h-32 bg-white border border-gray-300 rounded-lg mx-auto flex items-center justify-center">
                            <span className="text-gray-400 text-xs">QR Code</span>
                        </div>
                    </div>
                </div>

                {/* Right Panel - Maps */}
                <div className="flex-1 p-6 flex gap-4">
                    {/* Map Logic: Highlight zone based on selected product */}
                    {(() => {
                        const { b1Zones, b2Zones } = useAllMapZones();
                        const displayB1 = b1Zones;
                        const displayB2 = b2Zones;

                        const zoneInfo = getZoneFromCategory(selectedProduct?.category_major, selectedProduct?.category_middle);
                        const targetFloor = zoneInfo?.floor || selectedProduct?.floor || 'B1';
                        const targetZoneName = zoneInfo?.zone;

                        const renderSingleZone = (zones: MapZone[]) => {
                            const zone = zones.find(z => z.name === targetZoneName);
                            if (!zone) return null;
                            return (
                                <div
                                    style={{
                                        position: 'absolute',
                                        left: zone.rect.left,
                                        top: zone.rect.top,
                                        width: zone.rect.width,
                                        height: zone.rect.height,
                                        backgroundColor: zone.color,
                                        border: '3px solid #ff0033',
                                        borderRadius: '8px',
                                        boxShadow: '0 0 15px rgba(255,0,50,0.5)',
                                        zIndex: 10,
                                        animation: 'pulse 2s infinite'
                                    }}
                                >
                                    <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-daiso-red text-white text-xs font-bold px-2 py-1 rounded whitespace-nowrap">
                                        {zone.name}
                                    </div>
                                </div>
                            );
                        };

                        return (
                            <>
                                {/* B1 Map */}
                                <div className={`flex-1 bg-white rounded-2xl shadow-soft p-5 transition-all flex flex-col ${targetFloor === 'B1' ? 'ring-4 ring-daiso-red ring-opacity-20' : 'opacity-60 grayscale'}`}>
                                    <h3 className="font-suite font-semibold text-lg text-gray-700 mb-4 text-center">
                                        B1 Floor {targetFloor === 'B1' && <span className="text-daiso-red font-bold">(위치)</span>}
                                    </h3>
                                    <div className="relative w-full h-auto bg-gray-50 rounded-xl border border-gray-200 overflow-hidden">
                                        <img
                                            src={mapB1.src}
                                            alt="B1 Map"
                                            className="w-full h-auto object-contain"
                                        />
                                        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 px-3 py-1 bg-gray-800 text-white text-xs font-bold rounded z-10">
                                            현위치(입구)
                                        </div>
                                        {renderSingleZone(displayB1)}
                                    </div>
                                    {targetFloor === 'B1' && (
                                        <Link
                                            href={`/kioskmode/map?category=${targetZoneName || 'all'}`}
                                            className="mt-4 w-full py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold rounded-xl text-center"
                                        >
                                            지도 자세히 보기
                                        </Link>
                                    )}
                                </div>

                                {/* B2 Map */}
                                <div className={`flex-1 bg-white rounded-2xl shadow-soft p-5 transition-all flex flex-col ${targetFloor === 'B2' ? 'ring-4 ring-daiso-red ring-opacity-20' : 'opacity-60 grayscale'}`}>
                                    <h3 className="font-suite font-semibold text-lg text-gray-700 mb-4 text-center">
                                        B2 Floor {targetFloor === 'B2' && <span className="text-daiso-red font-bold">(위치)</span>}
                                    </h3>
                                    <div className="relative w-full h-auto bg-gray-50 rounded-xl border border-gray-200 overflow-hidden">
                                        <img
                                            src={mapB2.src}
                                            alt="B2 Map"
                                            className="w-full h-auto object-contain"
                                        />
                                        {renderSingleZone(displayB2)}
                                    </div>
                                    {targetFloor === 'B2' && (
                                        <Link
                                            href={`/kioskmode/map?category=${targetZoneName || 'all'}`}
                                            className="mt-4 w-full py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold rounded-xl text-center"
                                        >
                                            지도 자세히 보기
                                        </Link>
                                    )}
                                </div>
                            </>
                        );
                    })()}
                </div>
            </main>

            <BottomNav />
        </div>
    );
}

export default function SearchResultsPage() {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <SearchResultsContent />
        </Suspense>
    );
}
