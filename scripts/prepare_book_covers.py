"""Prepare the owner's original covers; no cropping, retouching or substitute artwork."""
import hashlib
import json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
RESOURCE=ROOT/'design-references'
PUBLIC=ROOT/'public/covers'
definitions=[('fe','fe-vol-1.png','New FE Textbook Vol. 1: IT Fundamentals'),('ip','ip-main-2017.png','New IT Passport Examination Preparation Book, 2017'),('ap','ap-vol-1.png','AP Exam Preparation Book, Volume 1: Keywords and Exam Questions')]
sha=lambda data:hashlib.sha256(data).hexdigest()
def prepare():
    PUBLIC.mkdir(exist_ok=True);manifest=[]
    for level,name,title in definitions:
        source=RESOURCE/name
        if not source.is_file():raise FileNotFoundError(f'Missing owner-provided original cover: {source}')
        with Image.open(source) as original:
            original=original.convert('RGBA');variants=[]
            for width in [320,original.width]:
                image=original if width==original.width else original.resize((width,round(original.height*width/original.width)),Image.Resampling.LANCZOS)
                temporary=PUBLIC/f'{level}-{width}.webp';image.save(temporary,'WEBP',lossless=True,exact=True,method=6)
                with Image.open(temporary) as check:
                    if check.convert('RGBA').tobytes()!=image.tobytes():raise ValueError('Cover pixels changed during encoding')
                encoded=temporary.read_bytes();digest=sha(encoded);target=PUBLIC/f'{digest}.webp';temporary.replace(target)
                variants.append({'path':f'covers/{target.name}','width':image.width,'height':image.height,'sha256':digest,'bytes':len(encoded)})
            manifest.append({'level':level,'title':title,'sourcePath':f'design-references/{name}','sourceSha256':sha(source.read_bytes()),'width':original.width,'height':original.height,'variants':variants})
    (ROOT/'src/content/book-covers.json').write_text(json.dumps(manifest,indent=2)+'\n','utf8')
    print(f'Prepared 3 original covers and 6 lossless responsive WebPs ({sum(v["bytes"] for c in manifest for v in c["variants"]):,} bytes). Full-size decoded pixels match the originals exactly.')
if __name__=='__main__':prepare()
