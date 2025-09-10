/** @type {import('next').NextConfig} */
const path = require('path');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const { DefinePlugin } = require('webpack');

const nextConfig = {
  reactStrictMode: true,
  webpack: (config: { plugins: any[]; }, { isServer }: any) => {
    // Check if the plugins array exists, if not, initialize it.
    if (!config.plugins) {
      config.plugins = [];
    }

    // Only apply these configurations on the client-side build
    if (!isServer) {
      config.plugins.push(
        new DefinePlugin({
          // Define relative base path for Cesium
          CESIUM_BASE_URL: JSON.stringify('/cesium/'),
        }),
        new CopyWebpackPlugin({
          patterns: [
            {
              from: path.join('node_modules', 'cesium', 'Build', 'Cesium', 'Workers'),
              to: 'cesium/Workers',
            },
            {
              from: path.join('node_modules', 'cesium', 'Build', 'Cesium', 'ThirdParty'),
              to: 'cesium/ThirdParty',
            },
            {
              from: path.join('node_modules', 'cesium', 'Build', 'Cesium', 'Assets'),
              to: 'cesium/Assets',
            },
            {
              from: path.join('node_modules', 'cesium', 'Build', 'Cesium', 'Widgets'),
              to: 'cesium/Widgets',
            },
          ],
        })
      );
    }

    return config;
  },
};

module.exports = nextConfig;
