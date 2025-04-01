const webpack = require('webpack');
const path = require('path');

module.exports = function override(config, env) {
  config.resolve.fallback = {
    "buffer": require.resolve("buffer/"),
    "stream": require.resolve("stream-browserify"),
    "assert": require.resolve("assert/"),
    "util": require.resolve("util/"),
    "process": path.resolve(__dirname, 'src/polyfills/process.js')
  };
  
  config.plugins.push(
    new webpack.ProvidePlugin({
      Buffer: ['buffer', 'Buffer'],
      process: path.resolve(__dirname, 'src/polyfills/process.js')
    })
  );

  // Отключение source-map-loader для node_modules
  config.module.rules.forEach(rule => {
    if (rule.use && Array.isArray(rule.use)) {
      rule.use.forEach(use => {
        if (use.loader === 'source-map-loader' || use.loader?.includes('source-map-loader')) {
          rule.exclude = /node_modules/;
        }
      });
    }
  });
  
  return config;
}