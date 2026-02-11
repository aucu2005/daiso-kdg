export type Floor = 'B1' | 'B2';
export type NodeType = 'path' | 'zone';

export interface MapNode {
    id: string;
    x: number; // Percentage 0-100
    y: number; // Percentage 0-100
    floor: Floor;
    type: NodeType;
    label?: string; // e.g. "A1", "Snack Corner"
    neighbors: string[]; // IDs of connected nodes
}

export interface MapData {
    nodes: MapNode[];
}
