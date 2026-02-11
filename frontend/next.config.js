/** @type {import('next').NextConfig} */
const nextConfig = {
    // Enable static export if needed for deployment
    // output: 'export',

    // Exclude bjy folder from compilation
    webpack: (config) => {
        config.watchOptions = {
            ignored: ['**/bjy/**', '**/node_modules/**']
        };
        return config;
    }
};

module.exports = nextConfig;
