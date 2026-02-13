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
import { MapZone } from '@/utils/mapZones';
import { useAllMapZones } from '@/hooks/useMapZones';


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

export default function CategoryMapPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [activeCategory, setActiveCategory] = useState<string>('all');

    // Navigation State
    const [navPath, setNavPath] = useState<Point[]>([]);
    const [navFloor, setNavFloor] = useState<Floor | null>(null);
    const [isNavigating, setIsNavigating] = useState(false);

    // Fetch dynamic zones from API
    const { b1Zones, b2Zones } = useAllMapZones();

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
            // Mock start location or use Kiosk ID
            const kioskId = "kiosk_1"; // TODO: Load from config/storage

            const res = await fetch('http://localhost:8000/api/navigation/route', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    start_x: 50, // Default center if retrieval fails
                    start_y: 90, // Default bottom
                    floor: 'B1',
                    target_product_id: parseInt(productId),
                    kiosk_id: kioskId
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

    // Category to Zone Mapping
    const getTargetZones = (catId: string): { names: string[], floor: Floor | 'ALL' } => {
        switch (catId) {
            case 'beauty': return { names: ['화장품'], floor: 'B1' };
            case 'kitchen': return { names: ['주방'], floor: 'B2' };
            case 'bath': return { names: ['욕실'], floor: 'B2' };
            case 'stationery': return { names: ['문구'], floor: 'B2' }; // Note: '문구' is on B1 and B2 in zones? Checked utility: B1 has '문구', B2 has '문구'.
            case 'storage': return { names: ['수납'], floor: 'B2' };
            case 'food': return { names: ['식품'], floor: 'B1' };
            case 'interior': return { names: ['인테리어소품', '홈패브릭'], floor: 'ALL' }; // B1 & B2
            case 'pet': return { names: ['반려동물'], floor: 'B2' };
            case 'all': return { names: [], floor: 'ALL' };
            default: return { names: [], floor: 'ALL' };
        }
    };

    const targetInfo = getTargetZones(activeCategory);

    const renderZones = (floor: Floor, zones: MapZone[]) => {
        const isAll = activeCategory === 'all';

        return zones.map((zone, idx) => {
            // Check if this zone should be highlighted
            const isTarget = targetInfo.names.includes(zone.name);
            const shouldHighlight = isTarget;

            // Visibility logic:
            // If navigating -> only show navigation (unless we want landmarks?)
            if (isNavigating) return null;

            // If not navigating:
            //   If all -> show all labels softly
            //   If category selected -> highlight targets strongly, HIDE others to reduce clutter
            if (!isAll && !shouldHighlight) return null;

            // Skip if rect is a polygon path (Array)
            if (Array.isArray(zone.rect)) return null;

            return (
                <div
                    key={idx}
                    style={{
                        position: 'absolute',
                        left: zone.rect.left,
                        top: zone.rect.top,
                        width: zone.rect.width,
                        height: zone.rect.height,
                        // Remove background and border for cleaner look
                        backgroundColor: 'transparent',
                        border: 'none',

                        // Layout for text centering
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',

                        // Text Styling
                        fontSize: shouldHighlight && !isAll ? '18px' : '11px',
                        fontWeight: shouldHighlight && !isAll ? '900' : 'bold',
                        color: shouldHighlight && !isAll ? '#da291c' : '#555', // Daiso Red for highlight
                        zIndex: shouldHighlight ? 20 : 1,

                        // Text Shadow / Glow for readability on map
                        textShadow: shouldHighlight && !isAll
                            ? '2px 2px 0 #fff, -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff, 1px 1px 0 #fff'
                            : '0 0 2px rgba(255,255,255,0.8)',

                        // Optional: Scale effect
                        transform: shouldHighlight && !isAll ? 'scale(1.1)' : 'none',
                        transition: 'all 0.3s ease-in-out',
                        pointerEvents: 'none', // Allow clicks to pass through if needed, though they are just labels
                    }}
                >
                    {zone.name}
                </div>
            );
        });
    };

    return (
        <div className="kiosk-container flex flex-col bg-gray-50">
            <Header />

            <main className="flex-1 flex p-5 gap-5 overflow-hidden">
                {/* Map Container */}
                <div className="flex-1 flex gap-4">
                    {/* B1 Floor Card */}
                    <div className={`flex-1 bg-white rounded-2xl shadow-soft p-5 flex flex-col transition-opacity duration-300 ${(activeCategory !== 'all' && targetInfo.floor === 'B2') ? 'opacity-40' : 'opacity-100'
                        }`}>
                        <h3 className="font-suite font-semibold text-lg text-gray-700 mb-3 text-center">
                            B1 Floor
                        </h3>
                        <div className="flex-1 relative bg-gray-50 rounded-xl border border-gray-200 overflow-hidden">
                            <MapNavigation
                                floor="B1"
                                path={navFloor === 'B1' ? navPath : []}
                                className="" // Always visible
                            />
                            {!isNavigating && renderZones('B1', b1Zones)}
                        </div>
                    </div>

                    {/* B2 Floor Card */}
                    <div className={`flex-1 bg-white rounded-2xl shadow-soft p-5 flex flex-col transition-opacity duration-300 ${(activeCategory !== 'all' && targetInfo.floor === 'B1') ? 'opacity-40' : 'opacity-100'
                        }`}>
                        <h3 className="font-suite font-semibold text-lg text-gray-700 mb-3 text-center">
                            B2 Floor
                        </h3>
                        <div className="flex-1 relative bg-gray-50 rounded-xl border border-gray-200 overflow-hidden">
                            <MapNavigation
                                floor="B2"
                                path={navFloor === 'B2' ? navPath : []}
                                className="" // Always visible
                            />
                            {!isNavigating && renderZones('B2', b2Zones)}
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
                            onClick={() => {
                                setActiveCategory(cat.id);
                                setIsNavigating(false); // Reset navigation when picking category
                                setNavPath([]);
                                const newParams = new URLSearchParams(searchParams.toString());
                                newParams.set('category', cat.id);
                                router.push(`?${newParams.toString()}`);
                            }}
                        />
                    ))}
                </div>
            </main>

            {/* Bottom Navigation */}
            <BottomNav />
        </div>
    );
}
