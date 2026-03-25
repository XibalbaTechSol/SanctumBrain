/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: "frame-ancestors 'self' http://localhost:8080 http://localhost:3000 http://localhost:3005 http://localhost:3006 http://localhost:3007 http://localhost:3008 http://localhost:3009",
          },
          {
            key: 'X-Frame-Options',
            value: 'ALLOW-FROM http://localhost:8080',
          }
        ],
      },
    ];
  },
};

module.exports = nextConfig;
