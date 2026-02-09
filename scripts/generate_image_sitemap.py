#!/usr/bin/env python3
"""
Generate sitemap-images.xml by scanning assets/img directory.
Usage: python scripts/generate_image_sitemap.py --base-url https://example.com
If --base-url is omitted, uses https://example.com as placeholder.
"""
import os
import sys
import argparse
from datetime import datetime

IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.webp', '.svg', '.gif'}


def iso_date(ts):
    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d')


def gather_images(root):
    images = []
    for dirpath, dirs, files in os.walk(root):
        for fn in files:
            if os.path.splitext(fn)[1].lower() in IMAGE_EXTS:
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, start=os.getcwd())
                images.append((rel.replace('\\','/'), full))
    return sorted(images)


def write_sitemap(images, base_url, out_path):
    base = base_url.rstrip('/')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n')
        for rel, full in images:
            url = f"{base}/{rel}"
            try:
                mtime = iso_date(os.path.getmtime(full))
            except Exception:
                mtime = None
            f.write('  <url>\n')
            f.write(f'    <loc>{url}</loc>\n')
            if mtime:
                f.write(f'    <lastmod>{mtime}</lastmod>\n')
            f.write('    <image:image>\n')
            f.write(f'      <image:loc>{url}</image:loc>\n')
            f.write('    </image:image>\n')
            f.write('  </url>\n')
        f.write('</urlset>\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', default='https://example.com', help='Base URL to prefix (include scheme)')
    parser.add_argument('--assets-dir', default='assets/img', help='Directory to scan for images')
    parser.add_argument('--out', default='sitemap-images.xml', help='Output sitemap path')
    args = parser.parse_args()

    if not os.path.isdir(args.assets_dir):
        print(f'Error: assets dir not found: {args.assets_dir}', file=sys.stderr)
        sys.exit(1)

    images = gather_images(args.assets_dir)
    if not images:
        print('No images found, nothing written.')
        sys.exit(0)

    write_sitemap(images, args.base_url, args.out)
    print(f'Wrote {args.out} with {len(images)} images. Replace BASE URL if needed.')


if __name__ == '__main__':
    main()
