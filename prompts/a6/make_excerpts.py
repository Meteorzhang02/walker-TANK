# Makes labelled excerpts of claude -p transcripts that are over ~1 MB (A6 rule).
# Removes base64 image data (frames Claude read) and truncates very long strings.
# Written by Claude (chat); run by me. Full originals are kept outside the repo.
import json, os, sys

def scrub(o, limit):
    if isinstance(o, dict):
        if o.get('type') == 'image' and isinstance(o.get('source'), dict):
            n = len(str(o['source'].get('data', '')))
            return {'type': 'image', 'source': '[image removed in excerpt: %d base64 chars]' % n}
        return {k: scrub(v, limit) for k, v in o.items()}
    if isinstance(o, list):
        return [scrub(v, limit) for v in o]
    if isinstance(o, str) and len(o) > limit:
        return o[:limit] + ' ...[truncated in excerpt: %d chars total]' % len(o)
    return o

def excerpt(src, dst):
    for limit in (2000, 600, 200):
        lines = [json.dumps({'type': 'excerpt_note', 'note': 'Labelled excerpt of %s: base64 images removed, strings over %d chars truncated. Full file kept outside the repo.' % (os.path.basename(src), limit)})]
        with open(src, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    lines.append(json.dumps(scrub(json.loads(line), limit), ensure_ascii=False))
                except Exception:
                    lines.append(json.dumps({'type': 'unparsed_line_truncated', 'text': line[:limit]}))
        out = '\n'.join(lines) + '\n'
        if len(out.encode('utf-8')) < 1_000_000 or limit == 200:
            open(dst, 'w', encoding='utf-8', newline='\n').write(out)
            print('%s -> %s (%d bytes, limit %d)' % (src, dst, len(out.encode('utf-8')), limit))
            return

for src, dst in zip(sys.argv[1::2], sys.argv[2::2]):
    excerpt(src, dst)
