const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Backend response types
export interface Product {
    id: number;
    name: string;
    price: number;
    category_major?: string;
    category_middle?: string;
    image_url?: string;
    floor?: string;
    location?: string; // Shelf ID (e.g. BA01)
    section?: string;
}

export interface SearchResponse {
    request_id: string;
    intent_valid: string;
    intent: string;
    slots: {
        item?: string;
        query_rewrite?: string;
    };
    products: Product[];
    needs_clarification: boolean;
    generated_question?: string;
    rerank?: {
        selected_id?: string;
        reason?: string;
    };
}

export async function searchProducts(query: string): Promise<SearchResponse> {
    const response = await fetch(`${API_BASE_URL}/api/query`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: query,
            history: [] // Add history if needed later
        }),
    });

    if (!response.ok) {
        throw new Error('Search failed');
    }

    return response.json();
}

export { API_BASE_URL };

// Map Zone API
export interface MapZone {
    id?: number;
    floor: string;
    name: string;
    rect: {
        top: string;
        left: string;
        width: string;
        height: string;
    };
    color: string;
    fontSize?: number;
}

export async function fetchMapZones(floor?: string): Promise<MapZone[]> {
    const url = floor ? `${API_BASE_URL}/api/map/zones?floor=${floor}` : `${API_BASE_URL}/api/map/zones`;
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch zones');
    return response.json();
}

export async function saveMapZone(zone: Omit<MapZone, 'id'>): Promise<{ id: number; success: boolean }> {
    const response = await fetch(`${API_BASE_URL}/api/map/zones`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(zone),
    });
    if (!response.ok) throw new Error('Failed to save zone');
    return response.json();
}

export async function deleteMapZone(id: number): Promise<{ success: boolean }> {
    const response = await fetch(`${API_BASE_URL}/api/map/zones/${id}`, {
        method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete zone');
    return response.json();
}
