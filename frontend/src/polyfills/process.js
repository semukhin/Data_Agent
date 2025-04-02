// process polyfill
const processPolyfill = {
  env: {
    NODE_ENV: process.env.NODE_ENV || 'development'
  },
  nextTick: callback => setTimeout(callback, 0)
};

window.process = processPolyfill;
export default processPolyfill;
module.exports = processPolyfill;