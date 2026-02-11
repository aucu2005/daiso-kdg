'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Floor } from '@/types/MapData';
import { fetchMapZones, saveMapZone, deleteMapZone, MapZone } from '@/lib/api';
import mapB1 from '@/assets/images/map_b1.jpg';
import mapB2 from '@/assets/images/map_b2.jpg';

export default function MapEditorPage() {
    const [floor, setFloor] = useState<Floor>('B1');
    const [zones, setZones] = useState<MapZone[]>([]);
    const [mode, setMode] = useState<'view' | 'draw' | 'delete'>('view');
    const [isDrawing, setIsDrawing] = useState(false);
    const [startPos, setStartPos] = useState<{ x: number; y: number } | null>(null);
    const [currentRect, setCurrentRect] = useState<{ top: number; left: number; width: number; height: number } | null>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const [isLoading, setIsLoading] = useState(false);

    const mapImageSrc = floor === 'B1' ? mapB1.src : mapB2.src;

    // Load zones
    const loadZones = async () => {
        try {
            setIsLoading(true);
            const data = await fetchMapZones(floor);
            setZones(data);
        } catch (error) {
            console.error('Failed to load zones:', error);
            alert('Failed to load zones');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        loadZones();
    }, [floor]);

    const getRelativeCoords = (e: React.MouseEvent) => {
        if (!containerRef.current) return { x: 0, y: 0 };
        const rect = containerRef.current.getBoundingClientRect();
        return {
            x: ((e.clientX - rect.left) / rect.width) * 100,
            y: ((e.clientY - rect.top) / rect.height) * 100
        };
    };

    const handleMouseDown = (e: React.MouseEvent) => {
        if (mode !== 'draw') return;
        setIsDrawing(true);
        const { x, y } = getRelativeCoords(e);
        setStartPos({ x, y });
        setCurrentRect({ top: y, left: x, width: 0, height: 0 });
    };

    const handleMouseMove = (e: React.MouseEvent) => {
        if (!isDrawing || !startPos) return;
        const { x, y } = getRelativeCoords(e);

        const left = Math.min(startPos.x, x);
        const top = Math.min(startPos.y, y);
        const width = Math.abs(x - startPos.x);
        const height = Math.abs(y - startPos.y);

        setCurrentRect({ top, left, width, height });
    };

    const handleMouseUp = async (e: React.MouseEvent) => {
        if (!isDrawing || !currentRect) return;
        setIsDrawing(false);

        // Ignore small clicks
        if (currentRect.width < 1 || currentRect.height < 1) {
            setCurrentRect(null);
            setStartPos(null);
            return;
        }

        const name = prompt('Enter Zone Name (e.g., 욕실, 청소):');
        if (name) {
            const newZone: Omit<MapZone, 'id'> = {
                floor,
                name,
                rect: {
                    top: `${currentRect.top.toFixed(2)}%`,
                    left: `${currentRect.left.toFixed(2)}%`,
                    width: `${currentRect.width.toFixed(2)}%`,
                    height: `${currentRect.height.toFixed(2)}%`
                },
                color: '#E1F5FE' // Default color
            };

            try {
                await saveMapZone(newZone);
                await loadZones(); // Reload
            } catch (error) {
                console.error(error);
                alert('Failed to save zone');
            }
        }

        setCurrentRect(null);
        setStartPos(null);
    };

    const handleDelete = async (id: number) => {
        if (!confirm('Delete this zone?')) return;
        try {
            await deleteMapZone(id);
            await loadZones();
        } catch (error) {
            alert('Failed to delete');
        }
    };

    return (
        <div className="flex flex-col h-screen bg-gray-100">
            {/* Header */}
            <div className="bg-white p-4 shadow z-20 flex justify-between items-center">
                <h1 className="text-xl font-bold">Map Zone Editor</h1>
                <div className="flex gap-4 items-center">
                    <select
                        value={floor}
                        onChange={(e) => setFloor(e.target.value as Floor)}
                        className="border p-2 rounded"
                    >
                        <option value="B1">B1 Floor</option>
                        <option value="B2">B2 Floor</option>
                    </select>

                    <div className="flex bg-gray-200 rounded p-1">
                        <button
                            onClick={() => setMode('view')}
                            className={`px-3 py-1 rounded ${mode === 'view' ? 'bg-white shadow' : ''}`}
                        >
                            View
                        </button>
                        <button
                            onClick={() => setMode('draw')}
                            className={`px-3 py-1 rounded ${mode === 'draw' ? 'bg-blue-500 text-white shadow' : ''}`}
                        >
                            Draw Zone
                        </button>
                        <button
                            onClick={() => setMode('delete')}
                            className={`px-3 py-1 rounded ${mode === 'delete' ? 'bg-red-500 text-white shadow' : ''}`}
                        >
                            Delete
                        </button>
                    </div>

                    <button onClick={loadZones} className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300">
                        Refresh
                    </button>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex flex-1 overflow-hidden">
                {/* Left: Map Area */}
                <div className="flex-1 bg-gray-50 overflow-auto relative border-r border-gray-300 flex justify-center items-start p-10">
                    <div
                        ref={containerRef}
                        className={`relative shadow-lg bg-white ${mode === 'draw' ? 'cursor-crosshair' : 'cursor-default'}`}
                        style={{ width: 'fit-content' }}
                        onMouseDown={handleMouseDown}
                        onMouseMove={handleMouseMove}
                        onMouseUp={handleMouseUp}
                        // Prevent image drag
                        onDragStart={(e) => e.preventDefault()}
                    >
                        <img
                            src={mapImageSrc}
                            alt="Map"
                            className="max-w-none h-auto object-contain pointer-events-none select-none"
                            style={{ maxHeight: '80vh' }} // Limit height to keep it viewable
                        />

                        {/* Existing Zones */}
                        {zones.map((zone) => (
                            <div
                                key={zone.id}
                                style={{
                                    position: 'absolute',
                                    top: zone.rect.top,
                                    left: zone.rect.left,
                                    width: zone.rect.width,
                                    height: zone.rect.height,
                                    backgroundColor: zone.color,
                                    border: mode === 'delete' ? '2px solid red' : '1px solid blue',
                                    opacity: 0.5,
                                    cursor: mode === 'delete' ? 'pointer' : 'default',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    fontSize: '12px',
                                    fontWeight: 'bold'
                                }}
                                onClick={(e) => {
                                    if (mode === 'delete' && zone.id) {
                                        e.stopPropagation();
                                        handleDelete(zone.id);
                                    }
                                }}
                                title={zone.name}
                            >
                                {zone.name}
                            </div>
                        ))}

                        {/* Drawing Rect */}
                        {isDrawing && currentRect && (
                            <div
                                style={{
                                    position: 'absolute',
                                    top: `${currentRect.top}%`,
                                    left: `${currentRect.left}%`,
                                    width: `${currentRect.width}%`,
                                    height: `${currentRect.height}%`,
                                    backgroundColor: 'rgba(0, 0, 255, 0.3)',
                                    border: '1px dashed blue'
                                }}
                            />
                        )}

                        {isLoading && (
                            <div className="absolute inset-0 bg-white bg-opacity-50 flex items-center justify-center z-50">
                                Loading...
                            </div>
                        )}
                    </div>
                </div>

                {/* Right: Sidebar */}
                <div className="w-80 bg-white shadow-xl z-10 flex flex-col">
                    <div className="p-4 border-b">
                        <h2 className="font-bold text-lg">Zone List</h2>
                        <p className="text-sm text-gray-500">
                            Floor: {floor} | Total: {zones.length}
                        </p>
                    </div>

                    <div className="flex-1 overflow-y-auto p-4 space-y-2">
                        {zones.length === 0 ? (
                            <div className="text-center text-gray-400 py-8">
                                No zones defined.
                            </div>
                        ) : (
                            zones.map((zone) => (
                                <div
                                    key={zone.id}
                                    className="p-3 border rounded-lg hover:bg-gray-50 hover:shadow-sm transition-all flex justify-between items-center group bg-white"
                                >
                                    <div className="flex items-center gap-2">
                                        <div
                                            className="w-3 h-3 rounded-full"
                                            style={{ backgroundColor: zone.color }}
                                        />
                                        <span className="font-medium text-gray-700">{zone.name}</span>
                                    </div>
                                    <button
                                        onClick={() => zone.id && handleDelete(zone.id)}
                                        className="text-gray-400 hover:text-red-500 p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                                        title="Delete Zone"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                            <path d="M3 6h18"></path>
                                            <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
                                            <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
                                        </svg>
                                    </button>
                                </div>
                            ))
                        )}
                    </div>

                    <div className="p-4 border-t bg-gray-50 text-xs text-gray-500">
                        <p>Tips:</p>
                        <ul className="list-disc ml-4 mt-1 space-y-1">
                            <li>Draw mode: Click and drag to create a zone.</li>
                            <li>Delete mode: Click a zone on map or trash icon in list.</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
}
