import { useState, useEffect } from 'react';
import { fetchMapZones, MapZone } from '@/lib/api';

export function useMapZones(floor: string | null) {
    const [zones, setZones] = useState<MapZone[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<unknown>(null);

    useEffect(() => {
        if (!floor) return;

        const load = async () => {
            setLoading(true);
            try {
                const data = await fetchMapZones(floor);
                setZones(data);
            } catch (err) {
                setError(err);
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        load();
    }, [floor]);

    return { zones, loading, error };
}

export function useAllMapZones() {
    const [b1Zones, setB1Zones] = useState<MapZone[]>([]);
    const [b2Zones, setB2Zones] = useState<MapZone[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const load = async () => {
            setLoading(true);
            try {
                const [b1, b2] = await Promise.all([
                    fetchMapZones('B1'),
                    fetchMapZones('B2')
                ]);
                setB1Zones(b1);
                setB2Zones(b2);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, []);

    return { b1Zones, b2Zones, loading };
}
