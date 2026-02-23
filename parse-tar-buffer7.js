import fs from 'fs';
import zlib from 'zlib';
const buf = fs.readFileSync('test/fixtures/hooks-install/npm-pack-hooks.tgz');
const unzipped = zlib.gunzipSync(buf);
console.log('Unzipped size:', unzipped.length);
