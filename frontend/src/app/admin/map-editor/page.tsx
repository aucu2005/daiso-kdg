'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Floor } from '@/types/MapData';
import { fetchMapZones, saveMapZone, deleteMapZone, MapZone, fetchCategories } from '@/lib/api';
import mapB1 from '@/assets/images/map_b1.jpg';
import mapB2 from '@/assets/images/map_b2.jpg';

type Point = { x: number; y: number };

export default function MapEditorPage() {
    const [floor, setFloor] = useState<Floor>('B1');
    const [zones, setZones] = useState<MapZone[]>([]);
    const [mode, setMode] = useState<'view' | 'draw-poly' | 'draw-rect' | 'delete'>('view');
    const [currentPoints, setCurrentPoints] = useState<Point[]>([]);
    const [categories, setCategories] = useState<Record<string, string[]>>({});
    const containerRef = useRef<HTMLDivElement>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [mousePos, setMousePos] = useState<Point | null>(null);

    // Rectangle drawing state
    const [rectStart, setRectStart] = useState<Point | null>(null);
    const [currentRect, setCurrentRect] = useState<{ top: number, left: number, width: number, height: number } | null>(null);

    const mapImageSrc = floor === 'B1' ? mapB1.src : mapB2.src;

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
        fetchCategories().then(setCategories).catch(console.error);
        setCurrentPoints([]);
        setRectStart(null);
        setCurrentRect(null);
    }, [floor]);

    const getRelativeCoords = (e: React.MouseEvent) => {
        if (!containerRef.current) return { x: 0, y: 0 };
        const rect = containerRef.current.getBoundingClientRect();
        return {
            x: ((e.clientX - rect.left) / rect.width) * 100,
            y: ((e.clientY - rect.top) / rect.height) * 100
        };
    };

    const handleClick = (e: React.MouseEvent) => {
        if (mode === 'draw-poly') {
            const coords = getRelativeCoords(e);
            setCurrentPoints(prev => [...prev, coords]);
        }
    };

    const handleMouseDown = (e: React.MouseEvent) => {
        if (mode === 'draw-rect') {
            const coords = getRelativeCoords(e);
            setRectStart(coords);
            setCurrentRect({ top: coords.y, left: coords.x, width: 0, height: 0 });
        }
    };

    const handleMouseMove = (e: React.MouseEvent) => {
        const coords = getRelativeCoords(e);
        if (mode === 'draw-poly') {
            setMousePos(coords);
        } else if (mode === 'draw-rect' && rectStart) {
            const left = Math.min(rectStart.x, coords.x);
            const top = Math.min(rectStart.y, coords.y);
            const width = Math.abs(coords.x - rectStart.x);
            const height = Math.abs(coords.y - rectStart.y);
            setCurrentRect({ top, left, width, height });
        }
    };

    const handleMouseUp = async (e: React.MouseEvent) => {
        if (mode === 'draw-rect' && rectStart && currentRect) {
            // Finish rect drawing
            if (currentRect.width < 1 || currentRect.height < 1) {
                setRectStart(null);
                setCurrentRect(null);
                return;
            }

            const name = prompt('Enter Zone Name (e.g., 과자, 욕실):');
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
                    color: '#E1F5FE'
                };
                await saveAndReload(newZone);
            }
            setRectStart(null);
            setCurrentRect(null);
            setMode('view');
        }
    };

    const finishPolyDrawing = async () => {
        if (currentPoints.length < 3) {
            alert('A polygon needs at least 3 points.');
            return;
        }

        const name = prompt('Enter Zone Name (e.g., 과자, 욕실):');
        if (!name) return;

        const newZone: Omit<MapZone, 'id'> = {
            floor,
            name,
            rect: currentPoints,
            color: '#E1F5FE'
        };
        await saveAndReload(newZone);
        setCurrentPoints([]);
        setMode('view');
    };

    const saveAndReload = async (zone: Omit<MapZone, 'id'>) => {
        try {
            await saveMapZone(zone);
            await loadZones();
        } catch (error) {
            console.error(error);
            alert('Failed to save zone');
        }
    };

    const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === 'Enter' && mode === 'draw-poly') {
            finishPolyDrawing();
        }
        if (e.key === 'Escape') {
            setCurrentPoints([]);
            setRectStart(null);
            setCurrentRect(null);
            setMode('view');
        }
    };

    useEffect(() => {
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [mode, currentPoints, rectStart]);

    const handleDelete = async (id: number) => {
        if (!confirm('Delete this zone?')) return;
        try {
            await deleteMapZone(id);
            await loadZones();
        } catch (error) {
            alert('Failed to delete');
        }
    };

    // Helper to render zones (Polygons or Rects)
    const renderZone = (zone: MapZone) => {
        const isPoly = Array.isArray(zone.rect);

        if (isPoly) {
            const points = (zone.rect as Point[]).map(p => `${p.x},${p.y}`).join(' ');
            return (
                <polygon
                    key={zone.id}
                    points={points}
                    fill={zone.color}
                    fillOpacity={0.4}
                    stroke={mode === 'delete' ? 'red' : 'blue'}
                    strokeWidth={0.5}
                    onClick={(e) => {
                        if (mode === 'delete' && zone.id) {
                            e.stopPropagation();
                            handleDelete(zone.id);
                        }
                    }}
                    className={mode === 'delete' ? 'cursor-pointer hover:fill-red-200' : ''}
                >
                    <title>{zone.name}</title>
                </polygon>
            );
        } else {
            const rect = zone.rect as any;
            const x = parseFloat(rect.left);
            const y = parseFloat(rect.top);
            const w = parseFloat(rect.width);
            const h = parseFloat(rect.height);

            return (
                <rect
                    key={zone.id}
                    x={x} y={y} width={w} height={h}
                    fill={zone.color}
                    fillOpacity={0.4}
                    stroke={mode === 'delete' ? 'red' : 'blue'}
                    strokeWidth={0.5}
                    onClick={(e) => {
                        if (mode === 'delete' && zone.id) {
                            e.stopPropagation();
                            handleDelete(zone.id);
                        }
                    }}
                    className={mode === 'delete' ? 'cursor-pointer hover:fill-red-200' : ''}
                >
                    <title>{zone.name}</title>
                </rect>
            );
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
                            onClick={() => setMode('draw-rect')}
                            className={`px-3 py-1 rounded ${mode === 'draw-rect' ? 'bg-blue-500 text-white shadow' : ''}`}
                        >
                            Draw Rect
                        </button>
                        <button
                            onClick={() => setMode('draw-poly')}
                            className={`px-3 py-1 rounded ${mode === 'draw-poly' ? 'bg-purple-500 text-white shadow' : ''}`}
                        >
                            Draw Poly
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

            <div className={`p-2 text-center text-sm ${mode.startsWith('draw') ? 'bg-yellow-100' : 'bg-gray-100'}`}>
                {mode === 'draw-rect' && (
                    <span><b>Rectangle Mode:</b> Click and drag to draw a box.</span>
                )}
                {mode === 'draw-poly' && (
                    <span>
                        <b>Polygon Mode:</b> Click points. Press <b>Enter</b> to finish, <b>Esc</b> to cancel.
                        Points: {currentPoints.length}
                    </span>
                )}
                {mode === 'view' && <span>Select a mode to start editing.</span>}
                {mode === 'delete' && <span className="text-red-600">Click a zone to delete it.</span>}
            </div>

            {/* Main Content */}
            <div className="flex flex-1 overflow-hidden">
                {/* Left: Map Area */}
                <div className="flex-1 bg-gray-50 overflow-auto relative border-r border-gray-300 flex justify-center items-start p-10">
                    <div
                        ref={containerRef}
                        className="relative shadow-lg bg-white bg-no-repeat bg-contain"
                        style={{
                            width: 'fit-content',
                            backgroundImage: `url(${mapImageSrc})`,
                            backgroundSize: 'contain',
                        }}
                        onClick={handleClick}
                        onMouseDown={handleMouseDown}
                        onMouseMove={handleMouseMove}
                        onMouseUp={handleMouseUp}
                    >
                        {/* We use an IMG to set the container size correctly, but we render SVG on top */}
                        <img
                            src={mapImageSrc}
                            alt="Map"
                            className="max-w-none h-auto object-contain pointer-events-none opacity-0" // Hide img but keep layout
                            style={{ maxHeight: '80vh' }}
                        />

                        {/* SVG Overlay */}
                        <svg
                            className="absolute inset-0 w-full h-full pointer-events-none"
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 100 100"
                            preserveAspectRatio="none"
                        >
                            {/* Re-enable pointer events for zones so we can click them */}
                            <g style={{ pointerEvents: 'auto' }}>
                                {zones.map(renderZone)}
                            </g>

                            {/* Poly Drawing Preview */}
                            {mode === 'draw-poly' && (
                                <g style={{ pointerEvents: 'none' }}>
                                    <polyline
                                        points={
                                            currentPoints.map(p => `${p.x},${p.y}`).join(' ') +
                                            (mousePos ? ` ${mousePos.x},${mousePos.y}` : '')
                                        }
                                        fill="none"
                                        stroke="purple"
                                        strokeWidth="0.5"
                                        strokeDasharray="1"
                                    />
                                    {currentPoints.map((p, i) => (
                                        <circle key={i} cx={p.x} cy={p.y} r="0.8" fill="purple" />
                                    ))}
                                    {currentPoints.length > 0 && mousePos && (
                                        <line
                                            x1={currentPoints[currentPoints.length - 1].x}
                                            y1={currentPoints[currentPoints.length - 1].y}
                                            x2={mousePos.x}
                                            y2={mousePos.y}
                                            stroke="purple"
                                            strokeWidth="0.5"
                                            strokeDasharray="1"
                                        />
                                    )}
                                </g>
                            )}

                            {/* Rect Drawing Preview */}
                            {mode === 'draw-rect' && currentRect && (
                                <rect
                                    x={currentRect.left}
                                    y={currentRect.top}
                                    width={currentRect.width}
                                    height={currentRect.height}
                                    fill="rgba(0,0,255,0.2)"
                                    stroke="blue"
                                    strokeWidth="0.5"
                                    strokeDasharray="1"
                                />
                            )}
                        </svg>
                    </div>
                </div>

                {/* Right: Sidebar */}
                <div className="w-80 bg-white shadow-xl z-10 flex flex-col border-l">
                    <div className="p-4 border-b bg-gray-50">
                        <h2 className="font-bold text-lg">Map Editor</h2>
                        <p className="text-sm text-gray-500">
                            Floor: {floor}
                        </p>
                    </div>

                    {/* Zone List Section (Top Half) */}
                    <div className="flex-1 flex flex-col min-h-0 border-b">
                        <div className="px-4 py-2 bg-blue-50 text-blue-800 font-bold text-sm flex justify-between items-center">
                            <span>Defined Zones ({zones.length})</span>
                        </div>
                        <div className="flex-1 overflow-y-auto p-4 space-y-2">
                            {zones.length === 0 ? (
                                <div className="text-center text-gray-400 py-8 text-sm">No zones defined.</div>
                            ) : (
                                zones.map((zone) => (
                                    <div
                                        key={zone.id}
                                        className="p-3 border rounded-lg hover:bg-gray-50 flex justify-between items-center group bg-white shadow-sm"
                                    >
                                        <div className="flex items-center gap-2 overflow-hidden">
                                            <div
                                                className="w-3 h-3 rounded-full flex-shrink-0"
                                                style={{ backgroundColor: zone.color }}
                                            />
                                            <span className="font-medium text-gray-700 truncate" title={zone.name}>{zone.name}</span>
                                            <span className="text-xs text-gray-400 flex-shrink-0">
                                                {Array.isArray(zone.rect) ? 'Poly' : 'Rect'}
                                            </span>
                                        </div>
                                        <button
                                            onClick={() => zone.id && handleDelete(zone.id)}
                                            className="text-gray-400 hover:text-red-500 p-1 opacity-100"
                                        >
                                            <span className="sr-only">Delete</span>
                                            🗑️
                                        </button>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>

                    {/* Category List Section (Bottom Half) */}
                    <div className="flex-1 flex flex-col min-h-0 bg-gray-50">
                        <div className="px-4 py-2 bg-green-50 text-green-800 font-bold text-sm border-b">
                            Available Categories
                        </div>
                        <div className="flex-1 overflow-y-auto p-4">
                            <div className="space-y-4">
                                {Object.entries(categories).map(([major, middles]) => (
                                    <div key={major} className="bg-white p-3 rounded-lg border shadow-sm">
                                        <div className="font-bold text-blue-600 text-base mb-2 border-b pb-1">{major}</div>
                                        <div className="flex flex-wrap gap-2">
                                            {middles.map(middle => (
                                                <span
                                                    key={middle}
                                                    className="inline-block px-2 py-1 bg-gray-100 text-gray-700 text-sm rounded hover:bg-blue-50 cursor-default"
                                                >
                                                    {middle}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                                {Object.keys(categories).length === 0 && (
                                    <div className="text-center text-gray-400 py-4 text-sm">
                                        No categories found.<br />
                                        Please check database.
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );

    function isDrawingMode() {
        return mode.startsWith('draw');
    }
}

