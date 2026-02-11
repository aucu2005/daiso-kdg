import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
    title: "어디다있소 | 다이소 상품 찾기",
    description: "다이소 매장 내 상품 위치를 빠르게 찾아드립니다.",
    keywords: ["다이소", "상품찾기", "매장안내", "키오스크"],
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="ko">
            <body className="antialiased">{children}</body>
        </html>
    );
}
