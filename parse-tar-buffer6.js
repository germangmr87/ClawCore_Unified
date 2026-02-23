const fs = require('fs');
const zlib = require('zlib');
const buf = fs.readFileSync('test/fixtures/hooks-install/npm-pack-hooks.tgz');
const unzipped = zlib.gunzipSync(buf);
console.log('Unzipped size:', unzipped.length);
