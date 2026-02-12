'use client';

import mapB1 from '../../../assets/images/map_b1.jpg';
import mapB2 from '../../../assets/images/map_b2.jpg';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Header from '@/components/shared/Header';
import BottomNav from '@/components/shared/BottomNav';
import CategoryButton from '@/components/shared/CategoryButton';
import {
    LayoutGrid, Sparkles, Utensils, Bath, Pencil,
    Box, Cookie, Lamp, Dog
} from 'lucide-react';
import MapNavigation, { Point } from '@/components/MapNavigation';
import { Floor } from '@/types/MapData';


const categories = [
    { icon: <LayoutGrid className="w-5 h-5" />, label: '전체', id: 'all' },
    { icon: <Sparkles className="w-5 h-5" />, label: '뷰티', id: 'beauty' },
    { icon: <Utensils className="w-5 h-5" />, label: '주방', id: 'kitchen' },
    { icon: <Bath className="w-5 h-5" />, label: '욕실', id: 'bath' },
    { icon: <Pencil className="w-5 h-5" />, label: '문구', id: 'stationery' },
    { icon: <Box className="w-5 h-5" />, label: '수납정리', id: 'storage' },
    { icon: <Cookie className="w-5 h-5" />, label: '식품', id: 'food' },
    { icon: <Lamp className="w-5 h-5" />, label: '인테리어', id: 'interior' },
    { icon: <Dog className="w-5 h-5" />, label: '애견', id: 'pet' },
];

// B1 Floor zones
// import { MapZone, DEFAULT_B1_ZONES, DEFAULT_B2_ZONES } from '@/utils/mapZones';
// import { useAllMapZones } from '@/hooks/useMapZones';


export default function CategoryMapPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const initialCategory = searchParams.get('category') || 'all';
    const [activeCategory, setActiveCategory] = useState<string>('all');

    // Navigation State
    const [navPath, setNavPath] = useState<Point[]>([]);
    const [navFloor, setNavFloor] = useState<Floor | null>(null);
    const [isNavigating, setIsNavigating] = useState(false);

    useEffect(() => {
        const cat = searchParams.get('category');
        if (cat) setActiveCategory(cat);

        const targetId = searchParams.get('productId');
        if (targetId) {
            fetchRoute(targetId);
        }
    }, [searchParams]);

    const fetchRoute = async (productId: string) => {
        try {
            // Mock start location
            const startX = 100;
            const startY = 100;

            const res = await fetch('http://localhost:8000/api/navigation/route', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    start_x: startX,
                    start_y: startY,
                    floor: 'B1',
                    target_product_id: parseInt(productId)
                })
            });

            if (res.ok) {
                const data = await res.json();
                setNavPath(data.path);
                setNavFloor(data.floor as Floor);
                setIsNavigating(true);
            } else {
                console.error("Failed to fetch route");
            }
        } catch (e) {
            console.error("Error fetching route:", e);
        }
    };
    // const { b1Zones, b2Zones } = useAllMapZones();

    // Use defaults if no API data
    // const displayB1 = b1Zones;
    // const displayB2 = b2Zones;

    useEffect(() => {
        const cat = searchParams.get('category');
        if (cat) {
            setActiveCategory(cat);
        }
    }, [searchParams]);

    // Map Sidebar ID to Zone Names
    /*
    const getTargetZones = (catId: string) => {
        switch (catId) {
            case 'beauty': return ['화장품', '뷰티'];
            case 'kitchen': return ['주방'];
            case 'bath': return ['욕실'];
            case 'stationery': return ['문구'];
            case 'storage': return ['수납'];
            case 'food': return ['식품', '간식'];
            case 'interior': return ['인테리어소품', '홈패브릭', '내추럴코너'];
            case 'pet': return ['반려동물'];
            case 'all': return [];
            default: return [catId]; // Assume raw zone name if not matched
        }
    };

    const targetZones = getTargetZones(activeCategory);

    const renderZones = (zones: MapZone[]) => {
        return zones.map((zone, idx) => {
            const isHighlighted = targetZones.includes(zone.name) || activeCategory === 'all';
            return (
                <div
                    key={idx}
                    style={{
                        position: 'absolute',
                        left: zone.rect.left,
                        top: zone.rect.top,
                        width: zone.rect.width,
                        height: zone.rect.height,
                        backgroundColor: isHighlighted ? zone.color : 'rgba(200,200,200,0.2)',
                        opacity: isHighlighted ? 0.9 : 0.5,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        border: isHighlighted ? '2px solid rgba(0,0,0,0.1)' : '1px solid #ddd',
                        borderRadius: '8px',
                        fontSize: zone.fontSize || 12,
                        fontWeight: 'bold',
                        color: '#333',
                        transition: 'all 0.3s ease',
                        zIndex: isHighlighted ? 10 : 1,
                        boxShadow: isHighlighted ? '0 4px 6px rgba(0,0,0,0.1)' : 'none',
                    }}
                >
                    {zone.name}
                </div>
            );
        });
    };
    */

    return (
        <div className="kiosk-container flex flex-col bg-gray-50">
            <Header />

            <main className="flex-1 flex p-5 gap-5 overflow-hidden">
                {/* Map Container */}
                <div className="flex-1 flex gap-4">
                    {/* B1 Floor Card */}
                    <div className="flex-1 bg-white rounded-2xl shadow-soft p-5 flex flex-col">
                        <h3 className="font-suite font-semibold text-lg text-gray-700 mb-3 text-center">
                            B1 Floor
                        </h3>
                        <div className="flex-1 relative bg-gray-50 rounded-xl border border-gray-200 overflow-hidden">
                            <MapNavigation
                                floor="B1"
                                path={navFloor === 'B1' ? navPath : []}
                                className={navFloor === 'B1' ? '' : 'opacity-50'}
                            />
                        </div>
                    </div>

                    {/* B2 Floor Card */}
                    <div className="flex-1 bg-white rounded-2xl shadow-soft p-5 flex flex-col">
                        <h3 className="font-suite font-semibold text-lg text-gray-700 mb-3 text-center">
                            B2 Floor
                        </h3>
                        <div className="flex-1 relative bg-gray-50 rounded-xl border border-gray-200 overflow-hidden">
                            <MapNavigation
                                floor="B2"
                                path={navFloor === 'B2' ? navPath : []}
                                className={navFloor === 'B2' ? '' : 'opacity-50'}
                            />
                        </div>
                    </div>
                </div>

                {/* Category Sidebar */}
                <div className="w-36 flex flex-col gap-2">
                    {categories.map((cat) => (
                        <CategoryButton
                            key={cat.id}
                            icon={cat.icon}
                            label={cat.label}
                            isActive={activeCategory === cat.id}
                            onClick={() => setActiveCategory(cat.id)}
                        />
                    ))}
                </div>
            </main>

            {/* Bottom Navigation */}
            <nav className="h-nav bg-white shadow-[0_-2px_8px_rgba(0,0,0,0.06)] flex items-center justify-around">
                <button className="flex items-center gap-2 text-daiso-red">
                    <LayoutGrid className="w-6 h-6" />
                    <span className="font-suite font-bold text-sm">카테고리 지도</span>
                </button>
                <button
                    onClick={() => router.push('/kioskmode')}
                    className="flex items-center gap-2 text-gray-500 hover:text-gray-700"
                >
                    <Sparkles className="w-6 h-6" />
                    <span className="font-suite text-sm">상품 검색</span>
                </button>
                <button className="flex items-center gap-2 text-gray-500 hover:text-gray-700">
                    <Box className="w-6 h-6" />
                    <span className="font-suite text-sm">장바구니</span>
                </button>
            </nav>
        </div>
    );
}
