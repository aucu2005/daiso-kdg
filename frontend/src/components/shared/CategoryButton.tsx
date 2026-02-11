import { clsx } from 'clsx';
import { ReactNode } from 'react';

interface CategoryButtonProps {
    icon: ReactNode;
    label: string;
    isActive?: boolean;
    onClick?: () => void;
}

export default function CategoryButton({
    icon,
    label,
    isActive = false,
    onClick,
}: CategoryButtonProps) {
    return (
        <button
            onClick={onClick}
            className={clsx(
                'w-full h-11 rounded-lg flex items-center justify-center gap-2 transition-all font-suite',
                isActive
                    ? 'bg-daiso-red text-white font-bold'
                    : 'bg-red-50 text-daiso-red font-semibold hover:bg-red-100'
            )}
        >
            <span className="w-5 h-5">{icon}</span>
            <span className="text-sm">{label}</span>
        </button>
    );
}
