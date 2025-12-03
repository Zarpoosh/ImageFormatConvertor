// api/convert.js
const formidable = require('formidable');
const fs = require('fs');
const sharp = require('sharp');

module.exports = (req, res) => {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Only POST allowed' });
    return;
  }

  const form = formidable({ multiples: false, keepExtensions: true });
  form.parse(req, async (err, fields, files) => {
    try {
      if (err) throw err;
      if (!files.image) return res.status(400).json({ error: 'image field is required' });

      const file = files.image;
      const maxMB = 12;
      if (file.size > maxMB * 1024 * 1024) {
        return res.status(413).json({ error: `File too large. Max ${maxMB} MB` });
      }

      const format = (fields.format || 'webp').toLowerCase();
      const quality = Math.min(100, Math.max(10, parseInt(fields.quality || '85')));

      const inputBuffer = await fs.promises.readFile(file.filepath);
      let processor = sharp(inputBuffer).rotate();

      let outputBuffer;
      switch (format) {
        case 'webp':
          outputBuffer = await processor.webp({ quality }).toBuffer();
          break;
        case 'png':
          outputBuffer = await processor.png().toBuffer();
          break;
        case 'jpg':
        case 'jpeg':
          outputBuffer = await processor.jpeg({ quality }).toBuffer();
          break;
        case 'avif':
          outputBuffer = await processor.avif({ quality }).toBuffer();
          break;
        default:
          return res.status(400).json({ error: 'unsupported format' });
      }

      res.setHeader('Content-Type', 'application/octet-stream');
      res.setHeader('Content-Disposition', `attachment; filename="converted.${format}"`);
      res.status(200).send(outputBuffer);
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: e.message || 'internal error' });
    }
  });
};
