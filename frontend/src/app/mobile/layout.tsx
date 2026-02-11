import type { Metadata } from 'next';

export const metadata: Metadata = {
    title: '어디다있소 | 모바일 안내',
    description: '다이소 매장 내 상품 위치 안내',
    viewport: 'width=390, initial-scale=1, maximum-scale=1',
};

export default function MobileLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center">
            {children}
        </div>
    );
}
