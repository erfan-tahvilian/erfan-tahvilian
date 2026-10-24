from pathlib import Path
from PIL import Image
import numpy as np
import base64, io, shutil, html, json, re, hashlib

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs'
REPO=ROOT
for d in ['branding','hero','projects','components']:
    (REPO/'assets'/d).mkdir(parents=True,exist_ok=True)
SOURCE=REPO/'assets/branding/logo-source.png'
# The corrected source logo is already stored beside the generated assets.
im=Image.open(SOURCE).convert('RGBA')
px=np.asarray(im).astype(float)
rgb=px[:,:,:3]
orange=(rgb[:,:,0]>rgb[:,:,1]*1.5)&(rgb[:,:,0]>8)
alpha=rgb.max(axis=2)*px[:,:,3]/255
alpha[alpha<=8]=0
H,W=alpha.shape
GOLD=['#71501B','#B88A2B','#F5DE91','#D4AF37','#8C6A22']
def color(s):return np.array([int(s[i:i+2],16) for i in [1,3,5]])
gradient=np.zeros((H,W,3))
stops=[0,.25,.48,.72,1]
for c in range(3):
    gradient[:,:,c]=np.interp(np.linspace(0,1,H),stops,[color(s)[c] for s in GOLD])[:,None]
variants={}
for name in ['gold','metallic','dark','light','monochrome']:
    arr=np.zeros((H,W,4),dtype=np.uint8)
    arr[:,:,:3]=color('#D4AF37')
    if name=='metallic':arr[:,:,:3]=gradient
    if name=='dark':arr[:,:,:3]=np.where(orange[:,:,None],gradient,color('#F5F3EB'))
    if name=='light':arr[:,:,:3]=np.where(orange[:,:,None],color('#8C6A22'),color('#1A1B1F'))
    if name=='monochrome':arr[:,:,:3]=color('#F5F3EB')
    arr[:,:,3]=np.round(alpha)
    img=Image.fromarray(arr)
    img.save(REPO/f'assets/branding/logo-{name}.png',optimize=True)
    buf=io.BytesIO();img.save(buf,format='PNG',optimize=True)
    variants[name]='data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()
    (REPO/f'assets/branding/logo-{name}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title"><title id="title">Erfan Tahvilian official logo - {name}</title><image width="{W}" height="{H}" xlink:href="{variants[name]}"/></svg>',encoding='utf-8')
    if name=='gold':
        for size in [16,32,48,64,180]:img.resize((size,size),Image.Resampling.LANCZOS).save(REPO/f'assets/branding/favicon-{size}.png')
        img.save(REPO/'assets/branding/favicon.ico',sizes=[(16,16),(32,32),(48,48),(64,64)])

def esc(t):return html.escape(str(t),quote=True)
def text(x,y,t,size=20,fill='fg',weight=400,spacing=0,family='sans'):
    font='Consolas, monospace' if family=='mono' else 'Segoe UI, Arial, sans-serif'
    return f'<text x="{x}" y="{y}" fill="{P.get(fill,fill)}" font-family="{font}" font-size="{size}" font-weight="{weight}" letter-spacing="{spacing}">{esc(t)}</text>'
def line(x,y,x2,y2,stroke='line',width=1,opacity=1):return f'<path d="M{x} {y}H{x2}" stroke="{P.get(stroke,stroke)}" stroke-width="{width}" opacity="{opacity}"/>' if y==y2 else f'<path d="M{x} {y}L{x2} {y2}" stroke="{P.get(stroke,stroke)}" stroke-width="{width}" opacity="{opacity}"/>'
def path(d,stroke='gold',width=1,fill='none',opacity=1):return f'<path d="{d}" fill="{P.get(fill,fill)}" stroke="{P.get(stroke,stroke)}" stroke-width="{width}" opacity="{opacity}"/>'
def circle(x,y,r,stroke='line',fill='none',width=1):return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{P.get(fill,fill)}" stroke="{P.get(stroke,stroke)}" stroke-width="{width}"/>'
def rect(x,y,w,h,fill='panel',stroke='line',rx=0):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{P.get(fill,fill)}" stroke="{P.get(stroke,stroke)}"/>'
def logo(x,y,s,theme):return f'<image x="{x}" y="{y}" width="{s}" height="{s*H/W:.3f}" xlink:href="{variants[theme]}"/>'
def svg(w,h,body,title,desc=''):
    defs='<linearGradient id="metal" x1="0" y1="0" x2=".8" y2="1">'+''.join(f'<stop offset="{o*100}%" stop-color="{c}"/>' for o,c in zip(stops,GOLD))+'</linearGradient><radialGradient id="aura"><stop stop-color="#D4AF37" stop-opacity=".12"/><stop offset="1" stop-color="#D4AF37" stop-opacity="0"/></radialGradient>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">{esc(title)}</title><desc id="desc">{esc(desc)}</desc><defs>{defs}</defs>{body}</svg>'
def save(pathname,w,h,b,title,desc=''):(REPO/'assets'/pathname).write_text(svg(w,h,b,title,desc),encoding='utf-8')
def theme(mode):
    global P
    P=({'bg':'#08090B','panel':'#101114','line':'#303027','fg':'#F5F3EB','muted':'#A1A1AA','gold':'#D4AF37','soft':'#F2D479'} if mode=='dark' else {'bg':'#F5F3EB','panel':'#FFFEFA','line':'#D8CEB9','fg':'#1A1B1F','muted':'#57575E','gold':'#8C6A22','soft':'#71501B'})
def motif(kind,x,y,s=1):
    b=''
    if kind=='network':
        pts=[(10,65),(80,20),(80,110),(160,65),(240,20),(240,110)]
        for a,c in [(0,1),(0,2),(1,3),(2,3),(3,4),(3,5)]:b+=line(*pts[a],*pts[c],'gold',1.5,.7)
        for i,(a,c) in enumerate(pts):b+=circle(a,c,6,'gold','panel',1.5)+circle(a,c,2,'none','gold')
    elif kind=='config':
        b+=rect(0,12,78,112,'panel','line',7)
        for yy in [40,68,96]:
            b+=line(12,yy,43,yy,'gold',1.5)+circle(60,yy,4,'gold','panel',1.5)
        b+=line(78,68,118,68,'gold',1.5)+path('M110 60L118 68L110 76','gold',1.5)
        b+=rect(126,44,48,48,'panel','gold',5)+rect(138,56,24,24,'panel','line',2)
        for xx in [140,150,160]:b+=line(xx,36,xx,44,'gold')+line(xx,92,xx,100,'gold')
        b+=line(174,68,204,68,'gold',1.5)
        b+=path('M212 42C212 30 254 30 254 42V96C254 108 212 108 212 96ZM212 42C212 54 254 54 254 42M212 68C212 80 254 80 254 68','gold',1.5)
    elif kind=='parser':
        b+=path('M125 18V50M125 50H45V88M125 50H205V88M45 88V115M205 88V115','gold',1.5)
        for a,c,t in [(104,0,'S'),(24,88,'A'),(184,88,'B')]:b+=rect(a,c,42,34)+text(a+12,c+23,t,19,'gold',family='mono')
    elif kind=='scheduler':
        for i,(a,l) in enumerate([(0,85),(85,45),(130,75),(205,45)]):b+=rect(a,45,l-3,44,'gold' if i%2==0 else 'panel','gold')
        b+=line(0,110,250,110)+text(0,138,'PREEMPT · EXECUTE · REPEAT',13,'muted',family='mono')
    elif kind=='annealing':
        pts=[(5,100),(60,25),(115,115),(180,10),(245,80)]
        b+=path('M5 100L60 25L180 10L245 80L115 115Z','gold',1.8)
        for a,c in pts:b+=circle(a,c,5,'gold','panel',1.5)
    elif kind=='cipher':
        b+=path('M30 10H100L210 115M210 10H140L30 115','gold',1.5)
        for a,c,t in [(8,0,'L'),(188,0,'R'),(100,48,'⊕'),(8,110,'R'),(188,110,'L')]:b+=rect(a,c,42,32)+text(a+12,c+23,t,19,'gold',family='mono')
    elif kind=='bisection':
        b+=line(0,90,255,90)+line(128,0,128,145)+path('M5 140C70 140 80 125 128 90S180 20 250 8','gold',2)
        for a in [35,80,105,128,150,180,220]:b+=line(a,84,a,96,'gold')
        b+=circle(128,90,5,'gold','panel',2)
    return f'<g transform="translate({x} {y}) scale({s})">{b}</g>'

projects=[
 ('foxvpn','01','FoxVPN','APPLICATION DEVELOPMENT','network',['A cross-platform VPN client unifying system tunneling,','per-app routing and connection diagnostics in one workspace.'],['Electron','Node.js','JavaScript'],'FoxVPN'),
 ('config-pilot','02','Config Pilot','CLOUD APPLICATIONS','config',['A self-hosted subscription-config manager with bilingual','web controls and Telegram automation on Cloudflare.'],['JavaScript','Cloudflare Workers','KV'],'config-pilot'),
 ('compiler','02','Compiler / Lexer / Parser','LANGUAGE PROCESSING','parser',['From tokens to parsing tables: recursive descent,','LL(1), LR(1) and LALR(1) in C++.'],['C++','Grammar analysis','CLI'],'compiler-lexer-parser'),
 ('mptcp','03','Multipath TCP','NETWORK SIMULATION','network',['An ns-3 module for multipath transport experiments','with LIA, OLIA and BALIA congestion control.'],['C++','ns-3','CMake'],'mptcp'),
 ('scheduler','04','SRTF Scheduler','OPERATING SYSTEMS','scheduler',['Preemptive scheduling with CSV input, Gantt output','and waiting-time / turnaround-time statistics.'],['C++','Scheduling','CSV'],'srtf-scheduler'),
 ('annealing','05','Simulated Annealing / TSP','OPTIMIZATION','annealing',['A configurable annealing search over a distance','matrix, with route costs and cooling parameters.'],['C++','Metaheuristics','CSV'],'simulated-annealing-tsp'),
 ('des','06','Simplified DES','CRYPTOGRAPHY STUDY','cipher',['An educational 8-bit block cipher with a 10-bit key,','visible key scheduling and round transformations.'],['C++','S-DES','CLI'],'simple-des'),
 ('bisection','07','Bisection Root Finder','NUMERICAL METHODS','bisection',['Serial bisection and an OpenMP implementation','for exploring interval-based root finding.'],['C++','OpenMP','Numerical methods'],'bisection-root-finder')
]
projects=[(p[0],f'{i:02}',*p[2:]) for i,p in enumerate(projects,1)]
for mode in ['dark','light']:
    theme(mode)
    for mobile in [False,True]:
        suffix=f'{mode}'+('-mobile' if mobile else '')
        w,h=(600,680) if mobile else (1200,560)
        b=rect(0,0,w,h,'bg','none')
        if not mobile:
            b+='<ellipse cx="920" cy="260" rx="350" ry="300" fill="url(#aura)"/>'
            for r in [153,203,252,301]:b+=circle(939,262,r,'line')
            b+=path('M700 440A301 301 0 0 1 1008 -31','gold',1,opacity=.55)
            b+=line(700,262,1199,262,'line')+line(939,0,939,498,'line')
            b+=logo(806,132,266,mode)
            b+=text(64,66,'ERFAN TAHVILIAN',17,'gold',600,2)+text(64,99,'THE ART OF ENGINEERING',12,'muted',family='mono',spacing=1.4)
            b+=text(60,227,'ERFAN',88,'fg',600,-3)+text(60,316,'TAHVILIAN',88,'fg',600,-3)
            b+=line(64,357,120,357,'gold',2)+text(138,364,'WHERE LOGIC MEETS CRAFT.',20,'soft',500,1)
            b+=text(64,416,'Applications. Algorithms. Networks.',22,'muted')
        else:
            b+='<ellipse cx="468" cy="150" rx="270" ry="250" fill="url(#aura)"/>'
            for r in [90,130,172]:b+=circle(476,126,r,'line')
            b+=logo(410,62,124,mode)
            b+=text(32,58,'ERFAN TAHVILIAN',18,'gold',600,2)+text(32,89,'THE ART OF',13,'muted',family='mono')+text(32,111,'ENGINEERING',13,'muted',family='mono')
            b+=text(28,322,'ERFAN',76,'fg',600,-2)+text(28,407,'TAHVILIAN',76,'fg',600,-2)
            b+=line(32,454,82,454,'gold',2)+text(32,499,'WHERE LOGIC MEETS CRAFT.',24,'soft',500)
            b+=text(32,548,'Applications. Algorithms. Networks.',23,'muted')
        b+=line(32 if mobile else 64,h-55,w-32 if mobile else 700,h-55)
        b+=text(32 if mobile else 64,h-23,'ERFAN-TAHVILIAN / GITHUB',14 if mobile else 13,'muted',family='mono',spacing=1)
        if not mobile:b+=text(866,h-23,'PRECISION × ELEGANCE',13,'gold',family='mono',spacing=1)
        save(f'hero/hero-{suffix}.svg',w,h,b,'Erfan Tahvilian - Where logic meets craft.','Erfan Tahvilian visual identity. The complete original logo, recolored gold and ivory, surrounded by measured arcs.')
        for slug,num,title,category,kind,desc,tags,repo in projects:
            w,h=(600,510) if mobile else (1200,292 if slug!='foxvpn' else 340)
            b=rect(.5,.5,w-1,h-1,'panel','line',12)
            b+=line(32,0,170,0,'gold',2)
            b+=text(32,44,f'{num} / {category}',19 if mobile else 15,'gold',family='mono',spacing=1)
            if not mobile:
                b+=text(32,112,title,40,'fg',600,-.6)
                for i,t in enumerate(desc):b+=text(32,161+i*30,t,23,'muted')
                b+=motif(kind,887,89,1)
                b+=line(32,h-61,w-32,h-61)
                b+=text(32,h-25,'  /  '.join(tags),16,'soft',family='mono')+text(947,h-25,'VIEW SOURCE ↗',15,'gold',family='mono')
                if slug=='foxvpn':b+=text(32,257,'FEATURED PROJECT',13,'gold',family='mono',spacing=1.5)
            else:
                # Reflow long project titles rather than shrinking essential type.
                titles={'compiler':['Compiler / Lexer','/ Parser'],'annealing':['Simulated Annealing','/ TSP'],'bisection':['Bisection','Root Finder']}.get(slug,[title])
                for i,t in enumerate(titles):b+=text(30,103+i*43,t,38,'fg',600,-.4)
                # Diagram lives behind no text; mobile gets a separate engineering strip.
                b+=motif(kind,390,292,.6)
                mobile_desc={
                 'foxvpn':['Cross-platform VPN with','system tunneling, per-app routing','and connection diagnostics.'],
                 'config-pilot':['Self-hosted config management.','Bilingual panel and Telegram','automation on Workers and KV.'],
                 'compiler':['Tokenization, grammar analysis','and four parsing strategies','implemented in C++.'],
                 'mptcp':['Multipath transport in ns-3.','LIA, OLIA and BALIA','congestion control.'],
                 'scheduler':['Preemptive scheduling, CSV,','Gantt output and process','timing statistics.'],
                 'annealing':['Configurable route search','over a distance matrix.','Cooling and cost analysis.'],
                 'des':['Educational 8-bit cipher.','Key scheduling and round','transformations made visible.'],
                 'bisection':['Serial root finding and','an OpenMP implementation.','Interval-based computation.']
                }[slug]
                for i,t in enumerate(mobile_desc):b+=text(32,211+i*32,t,26,'muted')
                b+=line(32,390,w-32,390)
                b+=text(32,434,' / '.join(tags),24,'soft',family='mono')+text(32,480,'VIEW SOURCE ↗',24,'gold',family='mono')
            save(f'projects/{slug}-{suffix}.svg',w,h,b,title+' - '+category,' '.join(desc)+' Technologies: '+', '.join(tags)+'. Diagram is schematic, not measured data.')
        w,h=(600,225) if mobile else (1200,170)
        b=rect(0,0,w,h,'bg','none')+line(32,1,w-32,1,'gold')
        b+=logo(32,35,66,mode)
        b+=text(120,64,"LET’S BUILD WITH INTENT.",26 if mobile else 32,'fg',600,-.3)
        b+=text(120,99,'Precision in the details.',20,'muted')
        b+=text(32 if mobile else 900,186 if mobile else 95,'ERFAN TAHVILIAN',15,'gold',family='mono',spacing=1)
        save(f'components/footer-{suffix}.svg',w,h,b,'Let’s build with intent. Erfan Tahvilian.')
    save(f'components/divider-{mode}.svg',1200,34,line(0,17,1200,17)+line(532,17,668,17,'gold',1.5)+line(532,14,532,20,'gold',1,.5)+line(668,14,668,20,'gold',1,.5),'Precision chapter divider')
    icon_paths=json.loads((REPO/'tools/social-icons.json').read_text(encoding='utf-8'))
    for key,label in [('portfolio','Portfolio'),('linkedin','LinkedIn'),('telegram','Telegram'),('github','GitHub')]:
        b=rect(.5,.5,167,51,'panel','line',8)
        if key=='portfolio':b+=logo(16,12,28,mode)
        else:b+=f'<g transform="translate(18 14)" fill="{P["gold"]}"><path d="{icon_paths[key]["path"]}"/></g>'
        b+=text(56,32,label,17,'fg',500)
        save(f'components/social-{key}-{mode}.svg',168,52,b,label)

def picture(folder,stem,alt,link=None):
    base=f'assets/{folder}/{stem}'
    s=f'<picture>\n  <source media="(prefers-color-scheme: dark) and (max-width: 640px)" srcset="{base}-dark-mobile.svg">\n  <source media="(max-width: 640px)" srcset="{base}-light-mobile.svg">\n  <source media="(prefers-color-scheme: dark)" srcset="{base}-dark.svg">\n  <img src="{base}-light.svg" width="1200" alt="{esc(alt)}">\n</picture>'
    if folder=='projects':s=s.replace('.svg"','.svg?v=3"')
    return f'<p>\n<a href="{link}">\n{s}\n</a>\n</p>' if link else s
def card(p):
    slug,num,title,category,kind,desc,tags,repo=p
    return picture('projects',slug,f'{title}: {" ".join(desc)} Built with {", ".join(tags)}. View repository.',f'https://github.com/erfan-tahvilian/{repo}')
readme=picture('hero','hero','Erfan Tahvilian. Where logic meets craft. Applications, algorithms and networks.')
readme+='''

# Erfan Tahvilian

I build applications and explore the systems beneath them - from connection controls in FoxVPN to language parsing, scheduling and multipath transport. My public work pairs practical software with focused implementations of core computing ideas.

[Selected work](#selected-work) · [Engineering toolkit](#engineering-toolkit) · [GitHub activity](#github-activity) · [Connect](#connect)

## Selected work

'''
readme+='\n\n'.join(card(p) for p in projects[:4])
readme+='''

<details>
<summary><strong>Four more engineering studies - scheduling, optimization, cryptography and numerical methods</strong></summary>
<br>

'''
readme+='\n\n'.join(card(p) for p in projects[4:])
readme+='''

Simplified DES is an educational cipher implementation. The diagrams above illustrate project concepts; they are not benchmark results.

</details>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/components/divider-dark.svg">
  <img src="assets/components/divider-light.svg" width="1200" alt="">
</picture>

## Engineering toolkit

| Area | Used in my public projects |
| :--- | :--- |
| Languages | C++ · JavaScript · HTML · CSS |
| Application development | Electron · Node.js · desktop interfaces |
| Systems & algorithms | Lexical analysis · parsing · CPU scheduling · simulated annealing |
| Networking & computation | ns-3 · Multipath TCP · OpenMP · numerical methods |
| Build & verification | npm scripts · CMake · command-line tooling |

## GitHub activity

Follow the code as it evolves: [public activity](https://github.com/erfan-tahvilian?tab=overview) · [all repositories](https://github.com/erfan-tahvilian?tab=repositories).

## Connect

<p>
<a href="https://erfantahvilian.cv"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/components/social-portfolio-dark.svg"><img src="assets/components/social-portfolio-light.svg" width="168" alt="Portfolio"></picture></a> &nbsp;&nbsp;
<a href="https://www.linkedin.com/in/erfan-tahvilian"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/components/social-linkedin-dark.svg"><img src="assets/components/social-linkedin-light.svg" width="168" alt="LinkedIn"></picture></a> &nbsp;&nbsp;
<a href="https://t.me/Erfan_Thvn"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/components/social-telegram-dark.svg"><img src="assets/components/social-telegram-light.svg" width="168" alt="Telegram"></picture></a> &nbsp;&nbsp;
<a href="https://github.com/erfan-tahvilian"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/components/social-github-dark.svg"><img src="assets/components/social-github-light.svg" width="168" alt="GitHub"></picture></a>
</p>

'''
readme+=picture('components','footer','Let’s build with intent. Precision in the details. Erfan Tahvilian.','https://github.com/erfan-tahvilian')+'\n'
(REPO/'README.md').write_text(readme,encoding='utf-8')
print(f'Generated {len(list(REPO.rglob("*.*")))} files in {REPO}')
