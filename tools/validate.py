from pathlib import Path
import re,json,hashlib,xml.etree.ElementTree as ET
from PIL import Image
import numpy as np
root=Path(__file__).resolve().parents[1]
repo=root
readme=(repo/'README.md').read_text(encoding='utf-8')
checks={}
checks['all_relative_image_paths_exist']=all((repo/p.split('?',1)[0]).is_file() for p in re.findall(r'(?:src|srcset)="(assets/[^"]+)"',readme))
checks['no_script_style_iframe_in_readme']=not re.search(r'<(?:script|style|iframe)\b|\sstyle=',readme,re.I)
checks['all_eight_repositories_linked']=all(f'https://github.com/erfan-tahvilian/{r}' in readme for r in ['FoxVPN','config-pilot','compiler-lexer-parser','mptcp','srtf-scheduler','simulated-annealing-tsp','simple-des','bisection-root-finder'])
selected=readme.split('## Selected work',1)[1].split('<details>',1)[0]
checks['four_selected_projects_in_requested_order']=re.findall(r'<a href="https://github.com/erfan-tahvilian/([^"]+)"',selected)==['FoxVPN','config-pilot','compiler-lexer-parser','mptcp']
count=0
for p in repo.rglob('*.svg'):
    t=ET.parse(p);count+=1
    for e in t.iter():
        assert e.tag.split('}')[-1] not in ['script','foreignObject','animate','animateTransform','set'],p
        assert not any(k.lower().startswith('on') for k in e.attrib),p
        for k,v in e.attrib.items():
            if k.endswith('href'):assert v.startswith('data:image/png;base64,'),p
checks['svg_well_formed_self_contained_static']=True
checks['svg_count']=count
source=repo/'assets/branding/logo-source.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks['corrected_source_preserved_byte_for_byte']=sha(source)=='be54a1c910e6d24204b7f6d50b522d186c04c4f126a9fd6066437fa81b9f6fab'
src=np.asarray(Image.open(source).convert('RGBA')).astype(float)
expected=src[:,:,:3].max(axis=2)*src[:,:,3]/255
expected[expected<=8]=0
mask=np.round(expected).astype('uint8')
for n in ['gold','metallic','dark','light','monochrome']:
    arr=np.asarray(Image.open(repo/f'assets/branding/logo-{n}.png'))
    assert np.array_equal(arr[:,:,3],mask),n
    assert not np.any((arr[:,:,0]==255)&(arr[:,:,1]==107)&(arr[:,:,2]==15)&(arr[:,:,3]>0)),n
checks['all_logo_variants_share_identical_geometry_and_alpha']=True
checks['black_background_removed']=int(mask[0,0])==0
white=(src[:,:,0]>250)&(abs(src[:,:,0]-src[:,:,1])<2)
checks['white_logo_components_preserved']=bool(np.all(mask[white]>245))
checks['original_source_sha256']=sha(source)
checks['total_repo_bytes']=sum(p.stat().st_size for p in repo.rglob('*') if p.is_file())
checks['largest_asset_bytes']=max(p.stat().st_size for p in repo.rglob('*') if p.is_file())
def luminance(c):
    a=[int(c[i:i+2],16)/255 for i in [1,3,5]]
    a=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in a]
    return sum(x*w for x,w in zip(a,[.2126,.7152,.0722]))
def contrast(a,b):
    x,y=sorted([luminance(a),luminance(b)])
    return round((y+.05)/(x+.05),2)
checks['contrast_ratios']={f'{a} on {b}':contrast(a,b) for a,b in [('#A1A1AA','#101114'),('#D4AF37','#101114'),('#57575E','#FFFEFA'),('#8C6A22','#FFFEFA'),('#F5F3EB','#08090B')]}
assert all(v is not False for v in checks.values())
(root/'tools/validation.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print(json.dumps(checks,indent=2))
