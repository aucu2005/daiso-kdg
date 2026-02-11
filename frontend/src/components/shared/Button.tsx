import { clsx } from 'clsx';
import { ReactNode } from 'react';

interface ButtonProps {
    children: ReactNode;
    variant?: 'primary' | 'secondary' | 'ghost';
    size?: 'sm' | 'md' | 'lg';
    icon?: ReactNode;
    className?: string;
    disabled?: boolean;
    onClick?: () => void;
}

export default function Button({
    children,
    variant = 'primary',
    size = 'md',
    icon,
    className,
    disabled = false,
    onClick,
}: ButtonProps) {
    const baseStyles = 'font-suite font-semibold rounded-btn transition-all flex items-center justify-center gap-2';

    const variantStyles = {
        primary: 'bg-daiso-red text-white shadow-red hover:bg-daiso-red-dark active:scale-95',
        secondary: 'bg-white text-daiso-red border-2 border-daiso-red hover:bg-red-50 active:scale-95',
        ghost: 'bg-gray-100 text-gray-600 hover:bg-gray-200 active:scale-95',
    };

    const sizeStyles = {
        sm: 'h-10 px-4 text-sm',
        md: 'h-14 px-6 text-base',
        lg: 'h-16 px-8 text-lg',
    };

    return (
        <button
            className={clsx(
                baseStyles,
                variantStyles[variant],
                sizeStyles[size],
                disabled && 'opacity-50 cursor-not-allowed',
                className
            )}
            disabled={disabled}
            onClick={onClick}
        >
            {icon}
            {children}
        </button>
    );
}
