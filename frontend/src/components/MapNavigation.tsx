'use client';

import React, { useRef, useEffect, useState } from 'react';
import mapB1 from '@/assets/images/map_b1.jpg';
import mapB2 from '@/assets/images/map_b2.jpg';

export type Point = {
    x: number;
    y: number;
};

interface MapNavigationProps {
    floor: 'B1' | 'B2';
    path: Point[];
    startPoint?: Point;
    endPoint?: Point;
    className?: string;
}

export default function MapNavigation({ floor, path, startPoint, endPoint, className }: MapNavigationProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const [mapSize, setMapSize] = useState({ width: 0, height: 0 });

    const mapSrc = floor === 'B1' ? mapB1.src : mapB2.src;

    // Handle resize
    useEffect(() => {
        const handleResize = () => {
            if (containerRef.current) {
                setMapSize({
                    width: containerRef.current.clientWidth,
                    height: containerRef.current.clientHeight
                });
            }
        };

        window.addEventListener('resize', handleResize);
        handleResize();

        return () => window.removeEventListener('resize', handleResize);
    }, []);

    // Draw path
    useEffect(() => {
        const canvas = canvasRef.current;
        const container = containerRef.current;
        if (!canvas || !container || mapSize.width === 0) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Adjust canvas size to match displayed image size (which might be scaled)
        // Note: The path coordinates from backend are based on original image size (e.g. 2000x1000).
        // We need to scale them to current display size.
        // Assuming mapB1/B2 intrinsic size is known or we can get it from an Image object.

        // For simplicity, let's assume path coordinates are relative (%) or we know the scale.
        // Actually backend returns pixel coordinates based on the image provided to MapProcessor.
        // So we need the original image dimensions.
        // Let's load the image to get dimensions.

        const img = new Image();
        img.src = mapSrc;
        img.onload = () => {
            const scaleX = mapSize.width / img.width;
            const scaleY = mapSize.height / img.height;

            // Draw Path
            if (path.length > 1) {
                ctx.beginPath();
                ctx.strokeStyle = '#FF0000';
                ctx.lineWidth = 4;
                ctx.setLineDash([10, 5]); // Dashed line

                // Move to start
                ctx.moveTo(path[0].x * scaleX, path[0].y * scaleY);

                for (let i = 1; i < path.length; i++) {
                    ctx.lineTo(path[i].x * scaleX, path[i].y * scaleY);
                }
                ctx.stroke();
            }

            // Draw Start Point
            if (startPoint || (path.length > 0)) {
                const p = startPoint || path[0];
                const x = p.x * scaleX;
                const y = p.y * scaleY;

                ctx.beginPath();
                ctx.fillStyle = '#0000FF';
                ctx.arc(x, y, 6, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = 'white';
                ctx.font = '12px Arial';
                ctx.fillText("Start", x + 8, y + 4);
            }

            // Draw End Point
            if (endPoint || (path.length > 0)) {
                const p = endPoint || path[path.length - 1];
                const x = p.x * scaleX;
                const y = p.y * scaleY;

                // Draw Marker Icon (simple circle for now)
                ctx.beginPath();
                ctx.fillStyle = '#FF0000';
                ctx.arc(x, y, 8, 0, Math.PI * 2);
                ctx.fill();

                // Pulse animation could be done here with requestAnimationFrame
            }
        };

    }, [path, mapSize, mapSrc, startPoint, endPoint]);

    return (
        <div ref={containerRef} className={`relative w-full h-full ${className}`}>
            <img
                src={mapSrc}
                alt={`${floor} Map`}
                className="w-full h-full object-contain pointer-events-none select-none"
            />
            <canvas
                ref={canvasRef}
                width={mapSize.width}
                height={mapSize.height}
                className="absolute top-0 left-0 w-full h-full pointer-events-none"
            />
        </div>
    );
}
