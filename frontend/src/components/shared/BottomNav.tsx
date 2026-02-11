'use client';

import { Search, LayoutGrid, User, ShoppingCart } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { clsx } from 'clsx';

interface NavItem {
    icon: React.ReactNode;
    label: string;
    href: string;
}

const navItems: NavItem[] = [
    { icon: <Search className="w-6 h-6" />, label: '검색', href: '/kioskmode' },
    { icon: <LayoutGrid className="w-6 h-6" />, label: '매장지도', href: '/kioskmode/map' },
    { icon: <User className="w-6 h-6" />, label: 'My', href: '#' },
];

export default function BottomNav() {
    const pathname = usePathname();

    return (
        <nav className="w-full h-nav bg-white shadow-[0_-2px_8px_rgba(0,0,0,0.06)] flex items-center justify-around">
            {navItems.map((item) => {
                const isActive = pathname === item.href ||
                    (item.href === '/kioskmode' && pathname?.startsWith('/kioskmode') && pathname !== '/kioskmode/map');

                return (
                    <Link
                        key={item.href}
                        href={item.href}
                        className={clsx(
                            'flex flex-col items-center gap-1 transition-colors',
                            isActive ? 'text-daiso-red' : 'text-gray-500 hover:text-gray-700'
                        )}
                    >
                        {item.icon}
                        <span className={clsx(
                            'font-suite text-xs',
                            isActive ? 'font-semibold' : 'font-normal'
                        )}>
                            {item.label}
                        </span>
                    </Link>
                );
            })}
        </nav>
    );
}
