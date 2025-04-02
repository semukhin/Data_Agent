// process.js
const processPolyfill = {
  env: {
    NODE_ENV: 'development' // Используем константу вместо обращения к process.env
  },
  nextTick: callback => setTimeout(callback, 0)
};

window.process = processPolyfill;
export default processPolyfill;