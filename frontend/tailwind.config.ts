import type { Config } from 'tailwindcss';

const config: Config = {
    content: [
        './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
        './src/components/**/*.{js,ts,jsx,tsx,mdx}',
        './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
        extend: {
            colors: {
                daiso: {
                    red: '#E60012',
                    'red-light': '#FF6B6B',
                    'red-dark': '#B8000E',
                    gray: {
                        50: '#FAFAFA',
                        100: '#F5F5F5',
                        200: '#E8E8E8',
                        300: '#E0E0E0',
                        400: '#CCCCCC',
                        500: '#999999',
                        600: '#666666',
                        700: '#333333',
                        800: '#1A1A1A',
                    }
                }
            },
            fontFamily: {
                suite: ['SUITE', 'sans-serif'],
                pretendard: ['Pretendard', 'sans-serif'],
            },
            fontSize: {
                'kiosk-title': ['48px', { lineHeight: '1.2', fontWeight: '700' }],
                'kiosk-heading': ['24px', { lineHeight: '1.3', fontWeight: '800' }],
                'kiosk-body': ['20px', { lineHeight: '1.5', fontWeight: '400' }],
                'kiosk-label': ['16px', { lineHeight: '1.4', fontWeight: '600' }],
                'mobile-title': ['20px', { lineHeight: '1.3', fontWeight: '800' }],
                'mobile-body': ['16px', { lineHeight: '1.5', fontWeight: '400' }],
            },
            spacing: {
                'header': '80px',
                'header-mobile': '56px',
                'nav': '60px',
            },
            borderRadius: {
                'btn': '8px',
                'card': '12px',
                'modal': '24px',
                'pill': '9999px',
            },
            boxShadow: {
                'soft': '0 4px 8px rgba(0, 0, 0, 0.08)',
                'medium': '0 8px 20px rgba(0, 0, 0, 0.12)',
                'red': '0 4px 12px rgba(230, 0, 18, 0.3)',
            },
            animation: {
                'pulse-slow': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'wave': 'wave 1s ease-in-out infinite',
            },
            keyframes: {
                wave: {
                    '0%, 100%': { height: '20px' },
                    '50%': { height: '60px' },
                }
            }
        },
    },
    plugins: [],
};

export default config;
