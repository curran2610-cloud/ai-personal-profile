#!/usr/bin/env python3
"""
Cut out ONLY the foreground subject/prop silhouette using macOS Apple Vision
(VNGenerateForegroundInstanceMaskRequest) and apply an adaptive sticker edge:
  --edge torn   : organic serrated torn-paper off-white contour
  --edge white  : smooth die-cut white sticker stroke
  --edge none   : clean transparent silhouette (for shadow-only float)

Usage:
  python3 make_torn_sticker.py input.jpg output.png --edge torn --width 680
"""
import argparse
import math
import os
import random
import subprocess
import tempfile
from PIL import Image, ImageFilter

SWIFT_SRC = r"""
import Foundation
import Vision
import CoreImage
import AppKit

let args = CommandLine.arguments
let inputURL = URL(fileURLWithPath: args[1])
let outputURL = URL(fileURLWithPath: args[2])

guard let ciImage = CIImage(contentsOf: inputURL) else { exit(1) }
let handler = VNImageRequestHandler(ciImage: ciImage, options: [:])
let req = VNGenerateForegroundInstanceMaskRequest()
try handler.perform([req])
guard let result = req.results?.first else { exit(2) }
let masked = try result.generateMaskedImage(ofInstances: result.allInstances, from: handler, croppedToInstancesExtent: true)
let outCI = CIImage(cvPixelBuffer: masked)
let ctx = CIContext()
guard let cg = ctx.createCGImage(outCI, from: outCI.extent) else { exit(3) }
let rep = NSBitmapImageRep(cgImage: cg)
guard let data = rep.representation(using: .png, properties: [:]) else { exit(4) }
try data.write(to: outputURL)
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Create contour-following sticker cutout.")
    parser.add_argument("input", help="Source image path")
    parser.add_argument("output", help="Output PNG path")
    parser.add_argument("--edge", choices=["torn", "white", "none"], default="torn")
    parser.add_argument("--width", type=int, default=680, help="Target subject width in px")
    parser.add_argument("--stroke", type=int, default=25, help="MaxFilter kernel size (odd int, default 25)")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        swift_file = os.path.join(tmp, "cut.swift")
        fg_png = os.path.join(tmp, "fg.png")
        with open(swift_file, "w", encoding="utf-8") as f:
            f.write(SWIFT_SRC)
        subprocess.run(["swift", swift_file, args.input, fg_png], check=True)

        im = Image.open(fg_png).convert("RGBA")
        w, h = im.size
        th = int(h * args.width / w)
        im = im.resize((args.width, th), Image.LANCZOS)

        if args.edge == "none":
            im.save(args.output)
            print(f"Saved clean silhouette: {im.size} -> {args.output}")
            return

        pad = 24
        ow, oh = args.width + pad * 2, th + pad * 2
        canvas = Image.new("RGBA", (ow, oh), (0, 0, 0, 0))
        canvas.paste(im, (pad, pad))

        alpha = canvas.split()[3].point(lambda p: 255 if p > 120 else 0)
        k = args.stroke if args.stroke % 2 == 1 else args.stroke + 1
        border = alpha.filter(ImageFilter.MaxFilter(k))

        if args.edge == "torn":
            random.seed(7)
            soft = border.filter(ImageFilter.GaussianBlur(2.2))
            sp = soft.load()
            mask = Image.new("L", (ow, oh), 0)
            mp = mask.load()
            for y in range(oh):
                for x in range(ow):
                    v = sp[x, y]
                    if v > 235:
                        mp[x, y] = 255
                    elif v > 25:
                        n = (math.sin(x * 0.42 + y * 0.17) + math.cos(y * 0.37 - x * 0.21)) * 32 + random.uniform(-22, 22)
                        mp[x, y] = 255 if (v + n) > 128 else 0
            paper_col = (246, 245, 242, 255)
        else:
            mask = border.filter(ImageFilter.GaussianBlur(0.8))
            paper_col = (255, 255, 255, 255)

        out = Image.new("RGBA", (ow, oh), (0, 0, 0, 0))
        paper = Image.new("RGBA", (ow, oh), paper_col)
        out.paste(paper, (0, 0), mask)
        out.paste(im, (pad, pad), im)

        bbox = out.getbbox()
        if bbox:
            out = out.crop(bbox)
        out.save(args.output)
        print(f"Saved {args.edge} sticker: {out.size} -> {args.output}")


if __name__ == "__main__":
    main()
