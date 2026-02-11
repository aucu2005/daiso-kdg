// frontend/src/utils/mapZones.ts

import { MapZone } from '@/lib/api';

export type { MapZone };

// B1 Floor zones (Base: ~500x400)
export const DEFAULT_B1_ZONES: MapZone[] = [
    { name: '시즌', color: '#FFF9C4', floor: 'B1', rect: { left: '20%', top: '5%', width: '16%', height: '12.5%' } }, // 100, 20
    { name: '화장품', color: '#FFE0E0', floor: 'B1', rect: { left: '38%', top: '5%', width: '16%', height: '12.5%' } }, // 190, 20
    { name: '건강기능식품', color: '#E8F5E9', floor: 'B1', rect: { left: '20%', top: '20%', width: '16%', height: '12.5%' } }, // 100, 80
    { name: '캐릭터', color: '#E3F2FD', floor: 'B1', rect: { left: '38%', top: '20%', width: '16%', height: '12.5%' } }, // 190, 80
    { name: '문구', color: '#F3E5F5', floor: 'B1', rect: { left: '4%', top: '35%', width: '16%', height: '12.5%' } }, // 20, 140
    { name: '파티·유아동', color: '#FFF3E0', floor: 'B1', rect: { left: '22%', top: '35%', width: '16%', height: '12.5%' } }, // 110, 140
    { name: '패션', color: '#FFEBEE', floor: 'B1', rect: { left: '40%', top: '35%', width: '16%', height: '12.5%' } }, // 200, 140
    { name: '포장', color: '#E1F5FE', floor: 'B1', rect: { left: '4%', top: '50%', width: '16%', height: '12.5%' } }, // 20, 200
    { name: '디지털', color: '#E8EAF6', floor: 'B1', rect: { left: '22%', top: '50%', width: '16%', height: '12.5%' } }, // 110, 200
    { name: '인테리어소품', color: '#FCE4EC', floor: 'B1', rect: { left: '40%', top: '50%', width: '16%', height: '12.5%' } }, // 200, 200
    { name: '식품', color: '#FBE9E7', floor: 'B1', rect: { left: '40%', top: '65%', width: '16%', height: '12.5%' } }, // 200, 260
];

// B2 Floor zones (Base: ~500x400)
export const DEFAULT_B2_ZONES: MapZone[] = [
    { name: '욕실', color: '#E1F5FE', floor: 'B2', rect: { left: '20%', top: '5%', width: '14%', height: '11%' } }, // 100, 20
    { name: '청소', color: '#F3E5F5', floor: 'B2', rect: { left: '36%', top: '5%', width: '14%', height: '11%' } }, // 180, 20
    { name: '세탁', color: '#FFF9C4', floor: 'B2', rect: { left: '52%', top: '5%', width: '14%', height: '11%' } }, // 260, 20
    { name: '득템', color: '#E8F5E9', floor: 'B2', rect: { left: '68%', top: '5%', width: '14%', height: '11%' } }, // 340, 20
    { name: '일본수입', color: '#FFE0B2', floor: 'B2', rect: { left: '20%', top: '19%', width: '14%', height: '11%' } }, // 100, 75
    { name: 'ALL', color: '#FFEBEE', floor: 'B2', rect: { left: '36%', top: '19%', width: '14%', height: '11%' } }, // 180, 75
    { name: '수납', color: '#F3E5F5', floor: 'B2', rect: { left: '52%', top: '19%', width: '14%', height: '11%' } }, // 260, 75
    { name: '홈패브릭', color: '#E8F5E9', floor: 'B2', rect: { left: '4%', top: '32.5%', width: '14%', height: '11%' } }, // 20, 130
    { name: '공구', color: '#FFF3E0', floor: 'B2', rect: { left: '20%', top: '32.5%', width: '14%', height: '11%' } }, // 100, 130
    { name: '내추럴코너', color: '#E1F5FE', floor: 'B2', rect: { left: '36%', top: '32.5%', width: '14%', height: '11%' } }, // 180, 130
    { name: '문구', color: '#FFEBEE', floor: 'B2', rect: { left: '52%', top: '32.5%', width: '14%', height: '11%' } }, // 260, 130
    { name: '주방', color: '#FCE4EC', floor: 'B2', rect: { left: '68%', top: '32.5%', width: '14%', height: '11%' } }, // 340, 130
    { name: '반려동물', color: '#F3E5F5', floor: 'B2', rect: { left: '4%', top: '46%', width: '14%', height: '11%' } }, // 20, 185
    { name: '캠핑', color: '#FBE9E7', floor: 'B2', rect: { left: '20%', top: '46%', width: '14%', height: '11%' } }, // 100, 185
    { name: '여행', color: '#E8EAF6', floor: 'B2', rect: { left: '36%', top: '46%', width: '14%', height: '11%' } }, // 180, 185
    { name: '원예', color: '#C8E6C9', floor: 'B2', rect: { left: '52%', top: '46%', width: '14%', height: '11%' } }, // 260, 185
];
