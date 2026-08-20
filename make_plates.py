#!/usr/bin/env python3
"""Paint the plates for the field book. One style paragraph, varied only by scene."""
import json, base64, os, sys, time, urllib.request

KEY = open('/home/claude/.secret/gemini_key').read().strip()
URL = ("https://generativelanguage.googleapis.com/v1beta/models/"
       "gemini-3-pro-image-preview:generateContent")
OUT = '/home/claude/PERMACULTURE_FIELD_BOOK/images'

STYLE = (
    "Dark moody watercolour on textured paper, in the manner of a nocturne. "
    "One warm amber light source glowing from inside the composition; everything else "
    "deep umber, warm black and soft indigo shadow. Loose wet brushwork, visible paper "
    "grain, soft bleeding edges. Silhouettes and suggestion rather than detail. "
    "Intimate, quiet, hand-painted. The painting fills the entire frame edge to edge "
    "with no white paper border, no margin and no mount. "
    "Absolutely no text, no letters, no words, no numbers, no symbols, no interface "
    "elements and no signature anywhere in the image. SCENE: "
)

SCENES = {
 "00_hero": "a terraced hillside at night with a long dry stone wall running across it, olive trees in silhouette, one amber lantern set on the top of the wall",
 "01_seedling": "one small seedling standing alone in dark freshly turned earth, a low amber lamp behind it casting a long shadow forward",
 "02_orchard": "an old orchard of gnarled fruit trees at night, one amber lantern hanging from a low branch, deep shadow between the trunks",
 "03_hands": "two open cupped human hands holding dark crumbling soil, warm amber light falling directly into the palms",
 "04_rings": "concentric circular rings scratched into dark bare earth seen from above, one small amber lamp burning at the very centre",
 "05_water": "a small dark still pool of water held behind a low curved earth bank on a hillside at night, amber light reflected on its surface",
 "06_soil": "a cut vertical section through dark earth showing distinct layers and fine pale roots, one amber light raking across the exposed face",
 "07_layers": "a dense stand of trees and undergrowth at many different heights, one amber lantern glowing deep inside among the trunks",
 "08_coop": "a low wooden animal shelter at night, warm amber light spilling out of its open doorway onto dark scattered straw",
 "09_wall": "a dry stone wall running across a bare rocky hillside, low wind bent shrubs behind it, one amber lantern set on the stones",
 "10_scale": "an old two pan balance scale standing on a dark wooden table, one pan heaped with grain, lit by a single amber lamp",
 "11_island": "a rocky island terrace above dark still water at night, old olive trees in silhouette, one amber lantern resting on a stone",
 "12_notebook": "an open blank notebook and a pencil lying on a dark table beside a window at night, one amber lamp, rain running down the glass",
}

def paint(name, scene, retries=3):
    body = json.dumps({
        "contents": [{"parts": [{"text": STYLE + scene}]}],
        "generationConfig": {"responseModalities": ["IMAGE"],
                             "imageConfig": {"aspectRatio": "16:9"}},
    }).encode()
    for attempt in range(retries):
        req = urllib.request.Request(URL, data=body, headers={
            "x-goog-api-key": KEY, "Content-Type": "application/json",
            "User-Agent": "mantra-field-books/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=240) as r:
                d = json.load(r)
        except urllib.error.HTTPError as e:
            code = e.code
            if code == 429:                      # valid key, throttled — rest it
                time.sleep(20 * (attempt + 1)); continue
            print(f"  {name}: HTTP {code}"); return False
        for p in d["candidates"][0]["content"]["parts"]:
            if "inlineData" in p:
                raw = base64.b64decode(p["inlineData"]["data"])
                open(f"{OUT}/{name}.jpg", "wb").write(raw)
                print(f"  {name}: {len(raw)//1024} KB")
                return True
        print(f"  {name}: no image part returned"); time.sleep(5)
    return False

if __name__ == "__main__":
    want = sys.argv[1:] or list(SCENES)
    ok = 0
    for n in want:
        if os.path.exists(f"{OUT}/{n}.jpg"):
            print(f"  {n}: already painted, skipping"); ok += 1; continue
        if paint(n, SCENES[n]): ok += 1
        time.sleep(2)
    print(f"painted {ok}/{len(want)}")
