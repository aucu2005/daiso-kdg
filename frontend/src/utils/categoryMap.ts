// frontend/src/utils/categoryMap.ts

export interface ZoneMapping {
    floor: 'B1' | 'B2';
    zone: string;
}

// B1 Zones: 시즌, 화장품, 건강기능식품, 캐릭터, 문구, 파티·유아동, 패션, 포장, 디지털, 인테리어소품, 식품
// B2 Zones: 욕실, 청소, 세탁, 득템, 일본수입, ALL, 수납, 홈패브릭, 공구, 내추럴코너, 주방, 반려동물, 캠핑, 여행, 원예

export const CATEGORY_MAP: Record<string, ZoneMapping> = {
    // POC v6 Categories
    "문구/팬시": { floor: 'B1', zone: '문구' },
    "뷰티/위생": { floor: 'B1', zone: '화장품' }, // Or divide based on middle category
    "공구/디지털": { floor: 'B2', zone: '공구' }, // Warning: B1 has Digital, B2 has Tools. Check middle category.
    "인테리어/원예": { floor: 'B2', zone: '원예' }, // Check middle
    "청소/욕실": { floor: 'B2', zone: '욕실' }, // Check middle
    "반려동물": { floor: 'B2', zone: '반려동물' },
    "수납/정리": { floor: 'B2', zone: '수납' },
    "주방용품": { floor: 'B2', zone: '주방' },
    "식품": { floor: 'B1', zone: '식품' },
    "패션": { floor: 'B1', zone: '패션' },
    "시즌상품": { floor: 'B1', zone: '시즌' },
    "캐릭터": { floor: 'B1', zone: '캐릭터' },
};

export function getZoneFromCategory(categoryMajor: string | undefined, categoryMiddle: string | undefined): ZoneMapping | null {
    if (!categoryMajor) return null;

    // Direct match
    if (CATEGORY_MAP[categoryMajor]) {
        const mapping = CATEGORY_MAP[categoryMajor];

        // Refine based on middle category for mixed groups
        if (categoryMajor === "공구/디지털") {
            if (categoryMiddle?.includes("디지털") || categoryMiddle?.includes("컴퓨터") || categoryMiddle?.includes("모바일")) {
                return { floor: 'B1', zone: '디지털' };
            }
            return { floor: 'B2', zone: '공구' };
        }

        if (categoryMajor === "청소/욕실") {
            if (categoryMiddle?.includes("청소")) return { floor: 'B2', zone: '청소' };
            if (categoryMiddle?.includes("세탁")) return { floor: 'B2', zone: '세탁' };
            return { floor: 'B2', zone: '욕실' };
        }

        if (categoryMajor === "인테리어/원예") {
            if (categoryMiddle?.includes("원예") || categoryMiddle?.includes("식물")) return { floor: 'B2', zone: '원예' };
            // B1 has "인테리어소품", B2 has "홈패브릭", "내추럴코너"
            // Default location for Interior? Maybe B1 '인테리어소품'
            if (categoryMiddle?.includes("소품")) return { floor: 'B1', zone: '인테리어소품' };
        }

        return mapping;
    }

    // Fallback based on keywords in category name
    if (categoryMajor.includes("문구")) return { floor: 'B1', zone: '문구' };
    if (categoryMajor.includes("화장품") || categoryMajor.includes("뷰티")) return { floor: 'B1', zone: '화장품' };
    if (categoryMajor.includes("식품")) return { floor: 'B1', zone: '식품' };
    if (categoryMajor.includes("주방")) return { floor: 'B2', zone: '주방' };
    if (categoryMajor.includes("욕실")) return { floor: 'B2', zone: '욕실' };
    if (categoryMajor.includes("청소")) return { floor: 'B2', zone: '청소' };

    return null;
}
