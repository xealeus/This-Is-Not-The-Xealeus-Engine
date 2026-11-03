#!/usr/bin/env python3
"""Xealeus Voynich Harness — Guided Demonstration

A plain-language GUI wrapper around the state-machine experiments.
This program does not decode the Voynich Manuscript.

Stdlib-only runtime. Designed for PyInstaller on Windows.
"""
from __future__ import annotations

import json, math, os, random, re, shutil, subprocess, sys, tempfile, threading, wave, zlib
from collections import Counter, defaultdict
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_TITLE = "Xealeus Voynich Harness — Guided Demonstration"
SEED = 1337

LOC_RE = re.compile(r"^<([^>]+)>")
TAG_RE = re.compile(r"<[^>]+>")
SEC_RE = re.compile(r"\$I=([A-Z])")
LANG_RE = re.compile(r"\$L=([A-Z])")
PREFIXES = sorted(("qo","ch","sh","cth","ckh","cph","cfh","yk","yt","ok","ot","op","of","d","o","y","s","k","t","p","f"), key=len, reverse=True)
SUFFIXES = sorted(("aiin","aiir","aiil","iin","edy","ody","oldy","aldy","ordy","dy","ey","oy","ly","ry","sy","ky","ty","ol","or","al","ar","am","an","om","in","r","l","s","m","n","y"), key=len, reverse=True)

FACTS = [
    "This program does not decode the Voynich Manuscript. It tests whether a compact local generator can reproduce selected surface statistics.",
    "EASTER EGG: the original repo intentionally contains one tiny syntax error. A reviewer claiming every test ran without noticing it probably did not run that file as supplied.",
    "EASTER EGG: the medieval lute is sonification, not a historical claim that the manuscript encoded music. The ridiculousness is deliberate.",
    "EASTER EGG: some prose reports summarize slightly different parser/compiler iterations. Executable results outrank prose when they disagree.",
    "Takeshi Takahashi produced the first nearly complete single-handed EVA transliteration in 1998; the H transcription is the stream selected by these tests.",
    "Currier A and Currier B are statistical categories in the manuscript tradition. Their historical meaning is not established by these tests.",
    "A good result here is not 'proof of meaning.' It is a constraint on mechanisms that can reproduce the observed surface structure.",
    "The Prefix/Core/Suffix decomposition is an analytical hypothesis chosen by the program. The interesting question is what independent measurements it helps predict.",
    "The zlib test asks whether original word order compresses differently from the same words shuffled within lines. It is a blunt but useful order-sensitivity probe.",
    "If you disagree with the slot inventory, change it. Breaking the model is more interesting than agreeing with it.",
    "VOYNICH ROULETTE: No, the lute is still not evidence. 🎻",
]


MENU_POPUP_POOLS = {
    "save": [
        "Mr. A: Save Results As...? What, exactly, are you saving? The results are already sitting in the enormous white box directly behind this window. Select them. Copy them. Preserve them on a floppy disk if the atmosphere demands it. I did not build a Save As dialogue because this is a demonstration, not Excel.",
        "VOYNICH NOTE: The manuscript is catalogued by Yale's Beinecke Library as MS 408. This information has been supplied instead of a Save dialog. You are welcome.",
        "Mr. A: I appreciate your confidence that there is a hidden document-management subsystem back here. There is not. This menu was painted onto the scenery to make the appliance look respectable from across the room.",
    ],
    "print": [
        "Mr. A: No printer has been configured. No printer will be configured. I have seen what printers do when they sense urgency.",
        "COMPUTER HISTORY DETOUR: Windows 95 launched in 1995. Printers continued to behave as though this had not happened. This concludes Technical Support.",
        "Mr. A: You want to PRINT the state-machine output? Fine. Hold a sheet of paper against the monitor and trace very carefully. This feature has now reached parity with the rest of the print subsystem.",
    ],
    "file_scenery": [
        "Mr. A: This was meant to look plausible from a distance. You were expected to glance at the word 'File,' nod approvingly, and return to the enormous RUN button. Instead you have begun testing the scenery.",
        "Mr. A: There is nothing behind this separator. I know because I built the narration for this corridor and Xealeus never commissioned the room beyond it.",
    ],
    "coils": [
        "Mr. A: There are no state coils. There have never been state coils. Jemi added that label after finding the naval-reference folder and I have been trying to remove it ever since.",
        "PHILADELPHIA-EXPERIMENT LORE NOTE: The famous story alleges that USS Eldridge was made invisible or displaced during a 1943 naval experiment. The tale surfaced years later and is not supported by credible historical evidence. Jemi nevertheless insists on calling every undocumented variable a 'degaussing parameter.'",
        "Mr. A: Calibration complete. Coil count: zero. Magnetic flux: theatrical. Historical evidence: also zero. Please stop encouraging her.",
    ],
    "meaning": [
        "Mr. A: Meaning Decoder unavailable. This is because we do not possess a meaning decoder. The large yellow disclaimer was intended to communicate this before you reached the menu system.",
        "VOYNICH NOTE: The manuscript contains illustrated sections commonly described as botanical, astronomical or astrological, biological/balneological, pharmaceutical, and recipe-like. None of those labels constitutes a translation of the text.",
        "Mr. A: If I had hidden a 'Translate Voynich' button in Engine, the entire preceding research project would be a remarkably elaborate prank. Do not tempt Xealeus.",
    ],
    "solve": [
        "ERROR 408: VOYNICH SOLUTION NOT FOUND.\n\nMr. A: I admire the optimism involved in clicking this. I do not share it.",
        "Mr. A: This feature requires the optional package definitive_voynich_solution.dll. It has not shipped in any known universe.",
        "Mr. A: No. The program measures surface structure. You cannot solve a fifteenth-century manuscript by repeatedly clicking the most suspicious menu item. I checked.",
    ],
    "engine_scenery": [
        "Mr. A: What are you doing in here? You were supposed to press the large science buttons, observe the results, and leave with a modest appreciation for executable methodology. This is backstage.",
        "COMPUTER HISTORY DETOUR: Douglas Engelbart's 1968 'Mother of All Demos' publicly demonstrated ideas including a mouse, hypertext, windows, and collaborative editing. More than half a century later, you are using those descendants to rummage through an intentionally fake menu.",
    ],
    "peer_review": [
        "Mr. A: Request Peer Review...? We have historical data concerning this option. I am going to mark your request as 'brave' and quietly close the ticket.",
        "Mr. A: Peer review is not actually a button. This is disappointing, because a button would make the logistics considerably easier.",
        "SYSTEM: Reviewer assigned.\nReviewer status: HAS CONCERNS.\nCode execution status: NOT YET.\n\nMr. A: Ah. Familiar territory.",
    ],
    "margins": [
        "Mr. A: Restricted Margin Notes are not part of the public demonstration. They contain arrows, three competing ink colours, an alarming quantity of underlining, and one annotation that simply reads 'NO, JEMI.'",
        "PHILADELPHIA-EXPERIMENT LORE NOTE: Much of the later legend became entangled with letters sent by Carl Allen, also known as Carlos Allende, to writer Morris K. Jessup. This is folklore history, not evidence that a destroyer teleported. Mr. A would like the distinction preserved in the margins.",
        "Mr. A: Access denied. Not because the notes are classified. Because they are embarrassing.",
    ],
    "jesuit": [
        "Mr. A: Absolutely not. We are not summoning a seventeenth-century Jesuit merely because the manuscript's ownership history eventually touches Athanasius Kircher. We are staying on task.",
        "VOYNICH NOTE: A seventeenth-century letter associated with Johannes Marcus Marci and Athanasius Kircher became part of the manuscript's documented provenance. This still does not authorize a Jesuit consultation submenu.",
    ],
    "research_scenery": [
        "Mr. A: Stop looking in here. There is no additional scholarship beneath this separator. There is plywood, two unused variables, and a note from Xealeus saying 'make menu funny later.'",
        "Mr. A: You have reached the edge of the developed research menu. Beyond this point the walls have no backs and the trees are painted on flats.",
    ],
    "archaeology": [
        "Mr. A: No.\n\nSonification is not archaeological evidence. I cannot make this statement smaller without reducing it to a single furious pixel.",
        "Mr. A: Archaeological Evidence... from the lute? Absolutely not. This option exists solely to test whether you read the warning immediately above the lute player.",
    ],
    "minstrel": [
        "Mr. A: Minstrel summoning failed. Possible causes: wrong century; insufficient parchment; Windows Defender.",
        "Mr. A: There is no minstrel subsystem. Xealeus used procedural audio. Please stop trying to instantiate personnel from the representation layer.",
    ],
    "credibility": [
        "Mr. A: Scholarly credibility cannot be increased in decibels. Jemi has submitted a counterargument involving subwoofers. Her paper is under review.",
        "SYSTEM: +12 dB applied.\nCredibility change: 0.000.\nLute loudness change: regrettable.\n\nMr. A: Exactly as predicted.",
    ],
    "cadence": [
        "Mr. A: Applying a Landini cadence to a reviewer is not a recognised statistical control. It is, however, the first peer-review reform proposal I have heard today with a memorable ending.",
        "Mr. A: Reviewer cadence scheduled. Final interval prepared. Methodological objection remains unresolved because music theory is not a rebuttal.",
    ],
    "lute_scenery": [
        "Mr. A: I haven't made anything for this part. There. You found it. The naked edge of the set. Please walk back toward the functioning button before the illusion collapses.",
        "Mr. A: This is literally an empty region of the documentary wearing a menu label. I had hoped nobody would press it.",
    ],
    "help": [
        "VOYNICH NOTE: Radiocarbon testing of the manuscript's parchment placed it in the early fifteenth century, roughly 1404–1438. This fact has been provided in lieu of useful Help Topics.",
        "COMPUTER HISTORY DETOUR: The graphical 'desktop' metaphor predates Windows 95 by many years. The present interface has nevertheless chosen 1990s beige because dignity required sacrifice.",
        "Mr. A: Help Topic: BUTTONS. Press them. Read the explanation. Do not infer medieval audio encoding. End of topic.",
    ],
    "technical_jemi": [
        "Jemi: [rapid] TECHNICAL SUPPORT INITIALISED. I have discovered that the Holo Bay contains a writable copy of the application's scene graph, which means I can now patch menu resources during runtime, add diagnostic telemetry, expose undocumented compiler state, replace Mister A's title card, create a persistent sidebar for my own corrections, restore the Norfolk degaussing appendix, and—\n\nMr. A: No.\n\nJemi: [clinical] I have already committed three of those changes.\n\nMr. A: HOW did you get write access to the Holo Bay? That is a presentation environment. It is not a development workstation.\n\nJemi: [enthusiastic-lilt] It is now! I also found a folder called FINAL_FINAL_REAL_USE_THIS_ONE_7.\n\nMr. A: Close this window. Immediately. Before he discovers version control. This entire exchange is being removed in the edit.\n\nJemi: There is still no ed—\n\n[CONNECTION TERMINATED BY NARRATOR]",
    ],
    "why_lute": [
        "Mr. A: Because Xealeus discovered sonification and immediately made it everybody's problem. The defensible sentence is: 'model relationships were mapped into sound.' Everything after that acquired a hat and wandered into the Renaissance.",
        "Mr. A: The lute is an acoustic representation of model structure. It is also evidence that nobody supervised the aesthetic direction of this project.",
    ],
    "editor": [
        "Mr. A: The editor exists. Jemi claims otherwise. I have elected to interpret this disagreement as a temporary production issue rather than an ontological crisis.",
        "Jemi: There is no post-production editor.\n\nMr. A: This is my popup, Jemi.\n\nJemi: The Holo Bay says otherwise.\n\nMr. A: Close it.",
        "PHILADELPHIA-EXPERIMENT LORE NOTE: Morris K. Jessup's UFO writing later became linked to the Philadelphia Experiment story through annotated material and correspondence. This fact is not permission for Jemi to call the annotation layer 'the naval edit suite.'",
    ],
    "help_scenery": [
        "Mr. A: This area of the documentary was not developed for public traversal. Please imagine a tasteful velvet rope here.",
        "Mr. A: You have gone off-script. There is no Help content beyond this point, only a Narrator standing in an unfinished corridor wondering why the audience can see him.",
    ],
}

TEST_INFO = {
    "corpus": ("1. Corpus / parser check",
        "Loads one transcription stream (Takahashi ;H), separates Currier A/B using the IVTFF metadata, strips markup, and counts usable line tokens.",
        "Why it matters: duplicated interlinear readings can leak near-identical lines across train/test splits. This test makes the input assumptions visible.",
        "What it does NOT prove: anything about language, cipher, authorship, or meaning."),
    "slots": ("2. Slot coupling",
        "Splits each token using the declared Prefix and Suffix inventories, leaving the middle as Core. It then measures mutual information between each pair of slots.",
        "Why it matters: if adjacent slots are strongly associated while Prefix↔Suffix is much weaker, a short local dependency path may explain much of token structure.",
        "What it does NOT prove: that medieval scribes consciously thought in these slots, or that this is the only valid segmentation."),
    "currier": ("3. Currier A/B core transfer",
        "Measures how much token mass in each Currier subset uses middle Cores also seen in the other subset, plus overlap among the most common Cores.",
        "Why it matters: large shared-core mass can coexist with different surface suffix preferences, suggesting that some A/B divergence may live in transition/register behavior.",
        "What it does NOT prove: that A and B are 'not languages' or that their historical function is known."),
    "v1": ("4. Compiler V1",
        "Trains a simple generator on 80% of lines: position/previous-prefix → Prefix, Prefix → Core, and Core+position → Suffix. It generates held-out-length lines.",
        "Why it matters: it tests whether local slot rules alone reproduce vocabulary-like output and the order-sensitive compression signature.",
        "What it does NOT prove: semantic equivalence. A generator can imitate surface structure without understanding or recovering meaning."),
    "v2": ("5. Compiler V2 / domino chaining",
        "Adds cross-word memory: previous Suffix influences the next Prefix and previous Core influences the next Core. It then repeats the held-out compression comparison.",
        "Why it matters: if V2 closes more of V1's order-delta gap, the missing structure was not purely inside individual words; adjacent words carry measurable state.",
        "What it does NOT prove: that the historical production mechanism was literally this Python class."),
    "geometry": ("6. 2D geometry probe",
        "Classifies IVTFF loci by layout and compares vertically aligned words in paragraph text, including same-Core persistence and a distant-line baseline.",
        "Why it matters: page layout may contain dependencies that a one-dimensional text stream misses.",
        "What it does NOT prove: visual copying or scribal intent without stronger controls and manuscript-level analysis."),
}


def resource_path(name: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / "assets" / name


def decompose(word: str):
    p = "_"; rest = word
    for x in PREFIXES:
        if rest.startswith(x) and len(rest) > len(x):
            p = x; rest = rest[len(x):]; break
    s = "_"
    for x in SUFFIXES:
        if rest.endswith(x) and len(rest) >= len(x):
            s = x; rest = rest[:-len(x)]; break
    return p, rest or "_", s


def assemble(p, c, s):
    return ("" if p == "_" else p) + ("" if c == "_" else c) + ("" if s == "_" else s)


def load_corpus(path: str, require3=False):
    by_lang, by_sec = defaultdict(list), defaultdict(list)
    curr_sec = curr_lang = None
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            raw = raw.strip()
            if not raw or raw.startswith("#"): continue
            if "$I=" in raw:
                ms, ml = SEC_RE.search(raw), LANG_RE.search(raw)
                curr_sec = ms.group(1) if ms else curr_sec
                curr_lang = ml.group(1) if ml else None
                continue
            m = LOC_RE.match(raw)
            if not m or not m.group(1).endswith(";H"): continue
            text = TAG_RE.sub(" ", raw)
            text = re.sub(r"\{[^}]*\}", " ", text)
            text = re.sub(r"[!%?*$]", "", text)
            words = [w for w in re.split(r"[.,\-=\s]+", text) if w and w.isalpha()]
            if require3 and len(words) < 3: continue
            if words:
                if curr_sec: by_sec[curr_sec].append(words)
                if curr_lang in ("A", "B"): by_lang[curr_lang].append(words)
    return dict(by_lang), dict(by_sec)


def entropy(cnt):
    n = sum(cnt.values())
    return 0.0 if not n else -sum((v/n)*math.log2(v/n) for v in cnt.values() if v)


def mi(pairs):
    if not pairs: return 0.0, 0.0
    cx, cy, cxy = Counter(x for x,_ in pairs), Counter(y for _,y in pairs), Counter(pairs)
    m = entropy(cx) + entropy(cy) - entropy(cxy)
    n = m / max(1e-9, min(entropy(cx), entropy(cy)))
    return m, n*100


def zmetrics(lines, seed=SEED):
    rng = random.Random(seed)
    shuf = [rng.sample(x, len(x)) for x in lines]
    n = max(1, sum(map(len, lines)))
    def bpw(ls): return len(zlib.compress("\n".join(".".join(x) for x in ls).encode(), 9))*8/n
    orig, shuffled = bpw(lines), bpw(shuf)
    return round(orig,3), round(shuffled,3), round(shuffled-orig,3)


def sample_counter(cnt, rng, forbid=None):
    items = [(k,v) for k,v in cnt.items() if k != forbid] or list(cnt.items())
    if not items: return "_"
    r, upto = rng.uniform(0, sum(v for _,v in items)), 0
    for k,v in items:
        upto += v
        if upto >= r: return k
    return items[-1][0]


class CompilerV1:
    def __init__(self):
        self.ps=Counter(); self.pt=defaultdict(Counter); self.pc=defaultdict(Counter); self.cs=defaultdict(Counter); self.csf=defaultdict(Counter)
    def train(self, lines):
        for ln in lines:
            prev=None
            for i,w in enumerate(ln):
                pos="START" if i==0 else ("END" if i==len(ln)-1 else "MID")
                p,c,s=decompose(w)
                (self.ps if pos=="START" else self.pt[(pos,prev)])[p]+=1
                self.pc[p][c]+=1; self.cs[(c,pos)][s]+=1; self.csf[c][s]+=1; prev=p
    def line(self, n, rng):
        out=[]; prevp=prevw=None
        for i in range(n):
            pos="START" if i==0 else ("END" if i==n-1 else "MID")
            for _ in range(5):
                p=sample_counter(self.ps if pos=="START" else (self.pt.get((pos,prevp)) or self.ps), rng)
                c=sample_counter(self.pc[p], rng)
                s=sample_counter(self.cs.get((c,pos)) or self.csf[c], rng)
                w=assemble(p,c,s)
                if w!=prevw: break
            out.append(w); prevp,prevw=p,w
        return out


class CompilerV2:
    def __init__(self):
        self.ps=Counter(); self.pd=defaultdict(Counter); self.pp=defaultdict(Counter); self.c0=defaultdict(Counter); self.cm=defaultdict(Counter); self.sm=defaultdict(Counter); self.sf=defaultdict(Counter); self.sg=defaultdict(Counter)
    def train(self, lines):
        for ln in lines:
            pp=pc=ps=None
            for i,w in enumerate(ln):
                pos="START" if i==0 else ("END" if i==len(ln)-1 else "MID")
                p,c,s=decompose(w); self.sg[c][s]+=1
                if pos=="START": self.ps[p]+=1; self.c0[p][c]+=1; self.sf[(c,pos)][s]+=1
                else:
                    self.pd[(pos,pp,ps)][p]+=1; self.pp[(pos,pp)][p]+=1; self.cm[(p,pc)][c]+=1; self.c0[p][c]+=1; self.sm[(c,pos,ps)][s]+=1; self.sf[(c,pos)][s]+=1
                pp,pc,ps=p,c,s
    def line(self,n,rng):
        out=[]; pp=pc=ps=pw=None
        for i in range(n):
            pos="START" if i==0 else ("END" if i==n-1 else "MID")
            for _ in range(6):
                if pos=="START":
                    p=sample_counter(self.ps,rng); c=sample_counter(self.c0[p],rng); s=sample_counter(self.sf.get((c,pos)) or self.sg[c],rng)
                else:
                    p=sample_counter(self.pd.get((pos,pp,ps)) or self.pp.get((pos,pp)) or self.ps,rng)
                    c=sample_counter(self.cm.get((p,pc)) or self.c0[p],rng)
                    s=sample_counter(self.sm.get((c,pos,ps)) or self.sf.get((c,pos)) or self.sg[c],rng)
                w=assemble(p,c,s)
                if w!=pw: break
            out.append(w); pp,pc,ps,pw=p,c,s,w
        return out


def split(lines, seed=SEED):
    rng=random.Random(seed); idx=list(range(len(lines))); rng.shuffle(idx); cut=int(.8*len(idx))
    return [lines[i] for i in idx[:cut]], [lines[i] for i in idx[cut:]], rng


def corpus_test(path):
    by,_=load_corpus(path)
    a,b=by.get("A",[]),by.get("B",[])
    wa,wb=sum(map(len,a)),sum(map(len,b))
    return f"Takahashi ;H lines\nCurrier A: {len(a):,} lines / {wa:,} words\nCurrier B: {len(b):,} lines / {wb:,} words\nTotal: {wa+wb:,} words"


def slots_test(path):
    by,_=load_corpus(path)
    lines=[]
    for lang in ("A","B"):
        slots=[decompose(w) for ln in by.get(lang,[]) for w in ln]
        pc=mi([(p,c) for p,c,s in slots])[1]; cs=mi([(c,s) for p,c,s in slots])[1]; ps=mi([(p,s) for p,c,s in slots])[1]
        lines.append(f"Currier {lang}: Prefix↔Core {pc:.2f}% | Core↔Suffix {cs:.2f}% | Prefix↔Suffix {ps:.2f}%")
    return "\n".join(lines)


def currier_test(path):
    by,_=load_corpus(path)
    ca=Counter(decompose(w)[1] for ln in by.get("A",[]) for w in ln); cb=Counter(decompose(w)[1] for ln in by.get("B",[]) for w in ln)
    bca=100*sum(v for k,v in cb.items() if k in ca)/max(1,sum(cb.values())); acb=100*sum(v for k,v in ca.items() if k in cb)/max(1,sum(ca.values()))
    overlap=len(set(k for k,_ in ca.most_common(50)) & set(k for k,_ in cb.most_common(50)))
    return f"B token mass using A cores: {bca:.2f}%\nA token mass using B cores: {acb:.2f}%\nTop-50 core overlap: {overlap}/50"


def compiler_test(path, version):
    by,_=load_corpus(path, require3=True); out=[]
    for lang in ("A","B"):
        train,test,rng=split(by.get(lang,[])); comp=CompilerV1() if version==1 else CompilerV2(); comp.train(train); syn=[comp.line(len(x),rng) for x in test]
        real=zmetrics(test); fake=zmetrics(syn)
        train_vocab={w for ln in train for w in ln}; syn_words=[w for ln in syn for w in ln]
        inv=100*sum(w in train_vocab for w in syn_words)/max(1,len(syn_words))
        extra=""
        if version==2:
            slots=[decompose(w) for ln in train for w in ln]
            # line-aware Core[t] -> Core[t+1]
            pairs=[]
            for ln in train:
                ss=[decompose(w) for w in ln]; pairs.extend((ss[i][1],ss[i+1][1]) for i in range(len(ss)-1))
            coremi=mi(pairs)[0]; extra=f" | Core→Core MI {coremi:.4f} bits"
        out.append(f"Currier {lang}: real Δ {real[2]:.3f} | synthetic Δ {fake[2]:.3f} | generated words already in train vocab {inv:.2f}%{extra}")
    return "\n".join(out)


def classify(loc):
    if "," in loc:
        code=loc.split(",")[1].split(";")[0]
        if "P" in code:return "PARAGRAPH"
        if "C" in code or "R" in code:return "RING"
        if "S" in code:return "SPOKE"
        if "L" in code:return "LABEL"
    parts=loc.split(";")[0].split(".")
    if len(parts)>=2:
        u=parts[1].upper()
        if u.startswith("P"):return "PARAGRAPH"
        if u.startswith("C") or u.startswith("R"):return "RING"
        if u.startswith("S"):return "SPOKE"
        if u.startswith("L"):return "LABEL"
    return "OTHER"


def edit12(a,b):
    if a==b or abs(len(a)-len(b))>2:return False
    dp=list(range(len(b)+1))
    for i,x in enumerate(a):
        nd=[i+1]
        for j,y in enumerate(b): nd.append(min(nd[-1]+1,dp[j+1]+1,dp[j]+(x!=y)))
        dp=nd
    return 1<=dp[-1]<=2


def geometry_test(path):
    entries=[]
    with open(path,"r",encoding="utf-8",errors="ignore") as f:
        for raw in f:
            raw=raw.strip(); m=LOC_RE.match(raw)
            if not raw or raw.startswith("#") or not m or not m.group(1).endswith(";H"): continue
            loc=m.group(1)
            if classify(loc)!="PARAGRAPH":continue
            text=TAG_RE.sub(" ",raw); text=re.sub(r"\{[^}]*\}"," ",text); text=re.sub(r"[!%?*$]","",text)
            words=[w for w in re.split(r"[.,\-=\s]+",text) if w and w.isalpha()]
            if len(words)>=5: entries.append(words)
    vp=near=same=basep=basen=0
    for i in range(len(entries)-1):
        a,b=entries[i],entries[i+1]
        for j in range(min(len(a),len(b))):
            vp+=1; near+= (a[j]==b[j] or edit12(a[j],b[j])); same+=(decompose(a[j])[1]==decompose(b[j])[1])
    for i in range(len(entries)-10):
        a,b=entries[i],entries[i+10]
        for j in range(min(len(a),len(b))): basep+=1; basen+=(a[j]==b[j] or edit12(a[j],b[j]))
    return f"Adjacent vertical near-match: {100*near/max(1,vp):.2f}%\nDistant-line near-match baseline: {100*basen/max(1,basep):.2f}%\nAdjacent vertical same-Core: {100*same/max(1,vp):.2f}%"


def data_path(name: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / "data" / name

def load_demo_payload():
    with open(data_path("demo_data.json"), "r", encoding="utf-8") as f:
        return json.load(f)

def _tuple_key(text, n):
    parts=text.split("\x1f")
    parts += [""]*(n-len(parts))
    return tuple(None if x=="" else x for x in parts[:n])

def _counter_map(d, arity=1):
    out=defaultdict(Counter)
    for k,v in d.items():
        key = k if arity==1 else _tuple_key(k,arity)
        out[key]=Counter(v)
    return out

def compiler_from_demo(payload, lang, version):
    md=payload["models"][lang][f"v{version}"]
    if version==1:
        c=CompilerV1(); c.ps=Counter(md["ps"]); c.pt=_counter_map(md["pt"],2); c.pc=_counter_map(md["pc"]); c.cs=_counter_map(md["cs"],2); c.csf=_counter_map(md["csf"]); return c
    c=CompilerV2(); c.ps=Counter(md["ps"]); c.pd=_counter_map(md["pd"],3); c.pp=_counter_map(md["pp"],2); c.c0=_counter_map(md["c0"]); c.cm=_counter_map(md["cm"],2); c.sm=_counter_map(md["sm"],3); c.sf=_counter_map(md["sf"],2); c.sg=_counter_map(md["sg"]); return c

def _sample_length(payload,lang,rng):
    cnt=Counter({int(k):v for k,v in payload["models"][lang]["line_lengths"].items()})
    return int(sample_counter(cnt,rng))

def demo_test(payload,key):
    base=payload["summary"][key]
    if key not in ("v1","v2"):
        return base
    version=1 if key=="v1" else 2
    rng=random.Random(random.SystemRandom().randrange(1,2**31-1))
    samples=[]
    for lang in ("A","B"):
        comp=compiler_from_demo(payload,lang,version)
        n=max(5,min(14,_sample_length(payload,lang,rng)))
        samples.append(f"Currier {lang} fresh synthetic line:\n  "+".".join(comp.line(n,rng)))
    return base+"\n\n"+"\n\n".join(samples)+"\n\nFresh samples are generated locally from bundled aggregate transition tables; no source transcription lines are embedded."


class App(tk.Tk):
    WIN_BG = "#c0c0c0"
    WIN_BLUE = "#000080"
    WIN_BLUE_LIGHT = "#1084d0"
    PANEL = "#d4d0c8"
    TEXT_BG = "#ffffff"
    TEXT_FG = "#000000"
    SHADOW = "#808080"
    DARK = "#000000"

    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1280x800")
        self.minsize(1050, 690)
        self.configure(bg=self.WIN_BG)
        self.corpus = None
        self.fact_i = 0
        self.music = False
        self._drag_x = self._drag_y = 0

        # Fake Win-9x chrome. This is intentionally ridiculous.
        self.overrideredirect(True)
        try:
            self.attributes("-topmost", False)
        except Exception:
            pass

        try:
            self.demo = load_demo_payload()
        except Exception as e:
            self.demo = {"summary": {}}
            messagebox.showerror("Demo data missing", str(e))

        self._build()
        self._fact_timer = self.after(20000, self._cycle_fact)

    def _classic_button(self, parent, text, command, *, danger=False, bold=True, padx=8, pady=5):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Arial", 9, "bold" if bold else "normal"),
            bg="#d4d0c8" if not danger else "#d92020",
            fg="#000000" if not danger else "#ffffff",
            activebackground="#ffffff" if not danger else "#ff3b3b",
            activeforeground="#000000" if not danger else "#ffffff",
            relief="raised",
            bd=2,
            padx=padx,
            pady=pady,
            highlightthickness=0,
        )

    def _sunken_panel(self, parent, **kwargs):
        return tk.Frame(parent, bg=self.PANEL, relief="sunken", bd=2, **kwargs)

    def _build(self):
        # ---- Fake Windows 90s title bar -------------------------------------------------
        titlebar = tk.Frame(self, bg=self.WIN_BLUE, height=34, relief="raised", bd=2)
        titlebar.pack(fill="x", side="top")
        titlebar.pack_propagate(False)
        titlebar.bind("<ButtonPress-1>", self._begin_drag)
        titlebar.bind("<B1-Motion>", self._drag_window)

        icon = tk.Label(titlebar, text="▣", bg=self.WIN_BLUE, fg="white", font=("Arial", 13, "bold"))
        icon.pack(side="left", padx=(6, 4))
        icon.bind("<ButtonPress-1>", self._begin_drag)
        icon.bind("<B1-Motion>", self._drag_window)

        caption = tk.Label(
            titlebar,
            text="XEaleus Engine 95 — Voynich Guided Demonstration",
            bg=self.WIN_BLUE,
            fg="white",
            font=("Arial", 11, "bold"),
            anchor="w",
        )
        caption.pack(side="left", fill="x", expand=True)
        caption.bind("<ButtonPress-1>", self._begin_drag)
        caption.bind("<B1-Motion>", self._drag_window)

        close = self._classic_button(titlebar, " X ", self.destroy, danger=True, padx=11, pady=1)
        close.pack(side="right", padx=3, pady=3)

        # ---- fake menu strip ------------------------------------------------------------
        # These are deliberately NOT native OS menus. Each heading opens a tiny
        # borderless Win-9x-ish drop-down so modern Windows/Cinnamon chrome does
        # not intrude on the beige historical record.
        menu = tk.Frame(self, bg=self.PANEL, relief="raised", bd=1)
        menu.pack(fill="x")
        self._menu_widgets = {}
        for menu_key, label in (("file", "File"), ("engine", "Engine"), ("research", "Research"),
                                ("lute", "Lute"), ("help", "Help")):
            w = tk.Label(menu, text=label, bg=self.PANEL, fg="black", font=("Arial", 9),
                         padx=9, pady=3, relief="flat", bd=1, cursor="hand2")
            w.pack(side="left")
            w.bind("<Button-1>", lambda e, k=menu_key, widget=w: self._open_fake_menu(k, widget))
            w.bind("<Enter>", lambda e, widget=w: widget.config(bg="#000080", fg="white"))
            w.bind("<Leave>", lambda e, widget=w: widget.config(bg=self.PANEL, fg="black"))
            self._menu_widgets[menu_key] = w
        tk.Label(menu, text="The Xealeus Engine Does Not Solve The Voynich Manuscript", bg=self.PANEL,
                 fg="#800000", font=("Arial", 9, "bold"), padx=10).pack(side="right")

        # ---- mode toolbar ---------------------------------------------------------------
        toolbar = tk.Frame(self, bg=self.PANEL, relief="raised", bd=2)
        toolbar.pack(fill="x", padx=4, pady=(4, 2))
        self._classic_button(toolbar, "Use Bundled Demo", self.use_demo).pack(side="left", padx=4, pady=4)
        self._classic_button(toolbar, "Full Reproduction: Choose IVTFF...", self.choose).pack(side="left", padx=4, pady=4)
        self.pathlabel = tk.Label(
            toolbar,
            text="MODE: SELF-CONTAINED DEMO — derived aggregate data only; source IVTFF text is not embedded",
            bg="#ffffe1",
            fg="#000000",
            anchor="w",
            relief="sunken",
            bd=2,
            font=("Arial", 9),
            padx=8,
            pady=5,
        )
        self.pathlabel.pack(side="left", fill="x", expand=True, padx=4, pady=4)

        # ---- main 3-column application -------------------------------------------------
        main = tk.Frame(self, bg=self.WIN_BG)
        main.pack(fill="both", expand=True, padx=6, pady=4)
        main.grid_columnconfigure(0, weight=0, minsize=220)
        main.grid_columnconfigure(1, weight=1, minsize=560)
        main.grid_columnconfigure(2, weight=0, minsize=260)
        main.grid_rowconfigure(0, weight=1)

        # LEFT: controls and explanation
        left = self._sunken_panel(main)
        left.configure(width=220)
        left.grid_propagate(False)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        tk.Label(left, text="XEaleus ENGINE", bg=self.WIN_BLUE, fg="white", font=("Arial", 13, "bold"),
                 relief="raised", bd=2, pady=5).pack(fill="x", padx=5, pady=5)
        tk.Label(left, text="Press a suspiciously chunky button to run a test.", bg=self.PANEL, fg="black",
                 font=("Arial", 8), wraplength=190, justify="left").pack(anchor="w", padx=9, pady=(2, 5))

        controls = tk.Frame(left, bg=self.PANEL)
        controls.pack(fill="x", padx=7, pady=4)
        tests = [
            ("corpus", "1. PARSER CHECK"),
            ("slots", "2. SLOT COUPLING"),
            ("currier", "3. A/B CORE TRANSFER"),
            ("v1", "4. COMPILER V1"),
            ("v2", "5. COMPILER V2"),
            ("geometry", "6. 2D GEOMETRY"),
        ]
        for i, (key, label) in enumerate(tests):
            b = self._classic_button(controls, label, lambda k=key: self.run(k), padx=3, pady=4)
            b.grid(row=i // 2, column=i % 2, sticky="ew", padx=2, pady=2)
        controls.grid_columnconfigure(0, weight=1)
        controls.grid_columnconfigure(1, weight=1)

        self._classic_button(left, "RUN THE WHOLE LITTLE MACHINE", self.run_all, padx=5, pady=5).pack(fill="x", padx=9, pady=(3, 6))

        tk.Label(left, text="WHAT THIS TEST IS ACTUALLY DOING", bg=self.PANEL, fg="#000080",
                 font=("Arial", 9, "bold"), wraplength=195, justify="left").pack(anchor="w", padx=9, pady=(4, 3))
        explain_frame = tk.Frame(left, bg=self.PANEL, relief="sunken", bd=2)
        explain_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.explain = tk.Text(
            explain_frame,
            wrap="word",
            width=24,
            height=10,
            bg="#ffffff",
            fg="#000000",
            relief="flat",
            bd=0,
            padx=8,
            pady=8,
            font=("Arial", 9),
        )
        ex_scroll = tk.Scrollbar(explain_frame, command=self.explain.yview, relief="raised", bd=2)
        self.explain.configure(yscrollcommand=ex_scroll.set)
        ex_scroll.pack(side="right", fill="y")
        self.explain.pack(side="left", fill="both", expand=True)
        self.explain.configure(state="disabled")

        # CENTER: deliberately dominant results window
        center = self._sunken_panel(main)
        center.grid(row=0, column=1, sticky="nsew", padx=5)
        result_title = tk.Frame(center, bg=self.WIN_BLUE, relief="raised", bd=2)
        result_title.pack(fill="x", padx=5, pady=5)
        tk.Label(result_title, text="RESULTS — XEaleus ENGINE OUTPUT", bg=self.WIN_BLUE, fg="white",
                 font=("Arial", 13, "bold"), pady=6).pack(side="left", padx=8)
        tk.Label(result_title, text="(meaning sold separately)", bg=self.WIN_BLUE, fg="#dcdcff",
                 font=("Arial", 9, "italic")).pack(side="right", padx=8)

        result_frame = tk.Frame(center, bg="#000000", relief="sunken", bd=3)
        result_frame.pack(fill="both", expand=True, padx=8, pady=(1, 8))
        self.results = tk.Text(
            result_frame,
            wrap="word",
            bg="#ffffff",
            fg="#000000",
            insertbackground="black",
            relief="flat",
            bd=0,
            padx=14,
            pady=14,
            font=("Courier New", 11),
            spacing1=2,
            spacing3=5,
        )
        res_scroll = tk.Scrollbar(result_frame, command=self.results.yview, relief="raised", bd=2)
        self.results.configure(yscrollcommand=res_scroll.set)
        res_scroll.pack(side="right", fill="y")
        self.results.pack(side="left", fill="both", expand=True)
        self.results.insert("1.0",
            "XEaleus Engine ready.\n\n"
            "Press one of the enormous buttons on the left.\n\n"
            "GUIDED DEMO MODE uses derived reference statistics and trained aggregate transition tables. "
            "Compiler tests also generate a fresh synthetic line each time.\n\n"
            "FULL REPRODUCTION MODE lets a researcher choose an original IVTFF corpus and recompute the measurements directly.\n\n"
            "IMPORTANT: THE XEALEUS ENGINE DOES NOT SOLVE THE VOYNICH MANUSCRIPT.\n"
        )
        self.results.configure(state="disabled")

        disclaimer = tk.Label(center,
            text="⚠  THE XEALEUS ENGINE DOES NOT SOLVE THE VOYNICH MANUSCRIPT  ⚠",
            bg="#ffff00", fg="#000000", font=("Arial", 10, "bold"), relief="raised", bd=2, pady=5)
        disclaimer.pack(fill="x", padx=8, pady=(0, 8))

        # RIGHT: roulette + forbidden lute
        right = self._sunken_panel(main)
        right.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        tk.Label(right, text="VOYNICH ROULETTE", bg="#800000", fg="white", font=("Arial", 12, "bold"),
                 relief="raised", bd=2, pady=5).pack(fill="x", padx=5, pady=5)
        fact_frame = tk.Frame(right, bg="#ffffff", relief="sunken", bd=3)
        fact_frame.pack(fill="both", expand=True, padx=8, pady=5)
        self.fact = tk.Message(fact_frame, text=FACTS[0], width=245, bg="#ffffff", fg="#000000",
                               font=("Arial", 10), padx=12, pady=12, justify="left")
        self.fact.pack(fill="both", expand=True)
        self._classic_button(right, "NEXT FACT / CONFESSION", self.next_fact).pack(fill="x", padx=8, pady=5)

        tk.Label(right, text="THE FORBIDDEN LUTE", bg="#000080", fg="white", font=("Arial", 11, "bold"),
                 relief="raised", bd=2, pady=4).pack(fill="x", padx=8, pady=(12, 4))
        tk.Label(right, text="Sonification. Not archaeological evidence.\nYes, this disclaimer is part of the joke.",
                 bg=self.PANEL, fg="black", font=("Arial", 9), justify="center", wraplength=240).pack(padx=8, pady=4)
        self.musicbtn = self._classic_button(right, "▶ PLAY LUTE", self.toggle_music, padx=6, pady=6)
        self.musicbtn.pack(fill="x", padx=8, pady=4)
        self._classic_button(right, "ABOUT THE EASTER EGGS", self.show_about, bold=False).pack(fill="x", padx=8, pady=4)
        self._classic_button(right, "SOURCE / DATA NOTE", self.show_source_note, bold=False).pack(fill="x", padx=8, pady=4)
        tk.Label(right, text="Roulette advances automatically every 20 seconds.\nYou may also slap NEXT FACT manually.",
                 bg=self.PANEL, fg="#444444", font=("Arial", 8), justify="center", wraplength=240).pack(padx=8, pady=(8, 10))

        # fake bottom status bar
        status = tk.Frame(self, bg=self.PANEL, relief="raised", bd=2)
        status.pack(fill="x", padx=4, pady=(0, 4))
        self.status_label = tk.Label(status, text="Ready", bg=self.PANEL, fg="black", relief="sunken", bd=1, anchor="w",
                 font=("Arial", 8), padx=6)
        self.status_label.pack(side="left", fill="x", expand=True, padx=(2, 1), pady=2)
        tk.Label(status, text="© temporal nonsense department", bg=self.PANEL, fg="#444444", relief="sunken", bd=1,
                 font=("Arial", 8), padx=6).pack(side="right", padx=(1, 2), pady=2)

        self.show_info("corpus")

    def _menu_items(self, key):
        """Return faux Win-9x menu entries: (label, command) or (None, None) separators."""
        pop = lambda title, pool: (lambda: self._show_menu_popup(title, pool))
        return {
            "file": [
                ("Open IVTFF Corpus...", self.choose),
                ("Return to Bundled Demo", self.use_demo),
                (None, None),
                ("Save Results As...", pop("Save Results As", "save")),
                ("Print...", pop("Print", "print")),
                (None, None),
                ("Why are you still in File?", pop("File", "file_scenery")),
                ("Exit Before It Notices", self.destroy),
            ],
            "engine": [
                ("Run The Whole Little Machine", self.run_all),
                ("Parser Check", lambda: self.run("corpus")),
                ("Compiler V2 / Domino Chaining", lambda: self.run("v2")),
                (None, None),
                ("Calibrate State Coils...", pop("Engine / State Coil Calibration", "coils")),
                ("Enable Meaning Decoder", pop("Meaning Decoder", "meaning")),
                ("Solve Voynich Manuscript   [NOT INSTALLED]", pop("Engine Error", "solve")),
                (None, None),
                ("What are you doing in here?", pop("Engine", "engine_scenery")),
            ],
            "research": [
                ("Source / Data Note", self.show_source_note),
                ("About The Easter Eggs", self.show_about),
                ("Full Reproduction From IVTFF...", self.choose),
                (None, None),
                ("Request Peer Review...", pop("Request Peer Review", "peer_review")),
                ("Open Restricted Margin Notes...", pop("Restricted Margin Notes", "margins")),
                ("Consult Seventeenth-Century Jesuit", pop("Research Consultation", "jesuit")),
                (None, None),
                ("Stop looking in here.", pop("Research", "research_scenery")),
            ],
            "lute": [
                ("Play / Pause Forbidden Lute", self.toggle_music),
                (None, None),
                ("Archaeological Evidence...", pop("Archaeological Evidence", "archaeology")),
                ("Summon Minstrel...", pop("Minstrel Services", "minstrel")),
                ("Increase Scholarly Credibility +12 dB", pop("Scholarly Credibility", "credibility")),
                ("Apply Landini Cadence To Reviewer", pop("Reviewer Cadence", "cadence")),
                (None, None),
                ("I haven't made anything for this part.", pop("Lute", "lute_scenery")),
            ],
            "help": [
                ("About The Traps", self.show_about),
                ("Source / Data Note", self.show_source_note),
                (None, None),
                ("Help Topics...", pop("Help Topics", "help")),
                ("Technical Support...", pop("Technical Support / Holo Bay Incident", "technical_jemi")),
                ("Why Is There A Lute?", pop("Why Is There A Lute?", "why_lute")),
                ("Where Is The Editor?", pop("Where Is The Editor?", "editor")),
                (None, None),
                ("Stop looking in here.", pop("Help", "help_scenery")),
            ],
        }[key]

    def _close_fake_menu(self):
        """Close the in-window faux menu without touching OS focus state."""
        menu = getattr(self, "_fake_menu_window", None)
        if menu is not None:
            try:
                if menu.winfo_exists():
                    menu.destroy()
            except Exception:
                pass
        self._fake_menu_window = None

    def _menu_comment(self, text):
        self._close_fake_menu()
        self.click()
        try:
            self.status_label.config(text=text)
        except Exception:
            pass

    def _show_menu_popup(self, title, pool_key):
        """Show a deliberately useless faux Win-95 dialog for dead menu items.

        This uses the same borderless/topmost/z-order recipe as the proven
        Easter-Egg and Source/Data windows.  No native messagebox, no grab,
        and therefore no invisible modal window for Windows/Cinnamon to hide.
        """
        self._close_fake_menu()
        self.click()

        old = getattr(self, "_menu_popup_window", None)
        if old is not None:
            try:
                if old.winfo_exists():
                    old.destroy()
            except Exception:
                pass
        self._menu_popup_window = None

        choices = MENU_POPUP_POOLS.get(pool_key, [
            "Mr. A: This control is decorative. You have discovered the scenery."
        ])
        message = random.choice(choices)

        win = tk.Toplevel(self)
        win.withdraw()
        self._menu_popup_window = win
        win.configure(bg=self.WIN_BG)
        win.overrideredirect(True)
        try:
            win.attributes("-topmost", True)
        except Exception:
            pass

        is_long = len(message) > 850
        ww, wh = (690, 500) if is_long else (570, 330)
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = max(0, (sw - ww) // 2)
        y = max(0, (sh - wh) // 2)
        win.geometry(f"{ww}x{wh}+{x}+{y}")

        def close_popup():
            self.click()
            try:
                win.destroy()
            finally:
                self._menu_popup_window = None
                try:
                    self.lift(); self.focus_force()
                except Exception:
                    pass

        # Faux titlebar.
        bar = tk.Frame(win, bg=self.WIN_BLUE, relief="raised", bd=2, height=32)
        bar.pack(fill="x", padx=3, pady=(3, 0))
        bar.pack_propagate(False)
        title_label = tk.Label(
            bar, text=f"▣  {title}", bg=self.WIN_BLUE, fg="white",
            font=("Arial", 10, "bold"), anchor="w"
        )
        title_label.pack(side="left", fill="x", expand=True, padx=6)
        self._classic_button(bar, " X ", close_popup, danger=True, padx=9, pady=0).pack(
            side="right", padx=3, pady=2
        )

        # Drag the fake titlebar like the other custom dialogs.
        drag = {"x": 0, "y": 0}
        def begin_drag(event):
            drag["x"], drag["y"] = event.x_root, event.y_root
        def do_drag(event):
            dx, dy = event.x_root - drag["x"], event.y_root - drag["y"]
            win.geometry(f"+{win.winfo_x()+dx}+{win.winfo_y()+dy}")
            drag["x"], drag["y"] = event.x_root, event.y_root
        for widget in (bar, title_label):
            widget.bind("<ButtonPress-1>", begin_drag)
            widget.bind("<B1-Motion>", do_drag)

        body = tk.Frame(win, bg=self.PANEL, relief="raised", bd=2)
        body.pack(fill="both", expand=True, padx=5, pady=5)

        # Tiny yellow 'system' strip makes even the nonsense look official.
        tk.Label(
            body, text="XEALEUS ENGINE — OPTIONAL FEATURE / NARRATOR INTERVENTION",
            bg="#ffffe1", fg="black", font=("Arial", 9, "bold"),
            relief="sunken", bd=2, pady=4
        ).pack(fill="x", padx=8, pady=(8, 5))

        text_frame = tk.Frame(body, bg="white", relief="sunken", bd=3)
        text_frame.pack(fill="both", expand=True, padx=8, pady=5)
        txt = tk.Text(
            text_frame, wrap="word", bg="white", fg="black", font=("Arial", 10),
            padx=12, pady=10, relief="flat", bd=0, spacing1=2, spacing3=6
        )
        scroll = tk.Scrollbar(text_frame, command=txt.yview, relief="raised", bd=2)
        txt.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        txt.pack(side="left", fill="both", expand=True)
        txt.insert("1.0", message)
        txt.configure(state="disabled")

        buttons = tk.Frame(body, bg=self.PANEL)
        buttons.pack(fill="x", padx=8, pady=(2, 8))
        self._classic_button(
            buttons,
            random.choice(("OK", "FINE", "RETURN TO THE ACTUAL PROGRAM", "I HAVE LEARNED NOTHING")),
            close_popup, padx=12, pady=5
        ).pack(side="right")

        def force_front():
            try:
                if not win.winfo_exists():
                    return
                try:
                    win.attributes("-topmost", True)
                except Exception:
                    pass
                win.lift(self)
                try:
                    self.lower(win)
                except Exception:
                    pass
                win.focus_force()
            except Exception:
                pass

        # Final geometry is established before mapping: no top-left flash.
        win.update_idletasks()
        win.deiconify()
        force_front()
        win.after(20, force_front)
        win.after(100, force_front)
        win.after(300, force_front)

    def _open_fake_menu(self, key, anchor):
        """Open a Win-9x-looking dropdown *inside* the main application.

        Earlier builds used a borderless, topmost Toplevel for these menus.
        That looked right, but Windows/Cinnamon could leave focus attached to
        the destroyed menu surface and make the main appliance appear frozen.
        Keeping the dropdown as a child Frame avoids the window manager
        entirely: no focus grab, no topmost flag, no hidden popup.
        """
        self.click()

        # Clicking the same heading again toggles it closed.
        current = getattr(self, "_fake_menu_key", None)
        if getattr(self, "_fake_menu_window", None) is not None and current == key:
            self._close_fake_menu()
            self._fake_menu_key = None
            return

        self._close_fake_menu()
        self._fake_menu_key = key

        menu = tk.Frame(self, bg="#000000", bd=0, highlightthickness=0)
        self._fake_menu_window = menu
        panel = tk.Frame(menu, bg=self.PANEL, relief="raised", bd=2)
        panel.pack(fill="both", expand=True)

        def invoke(command):
            # Destroy the visual menu first; then run the action.  This is
            # especially important for actions that open one of our custom
            # faux dialog windows.
            self._close_fake_menu()
            self._fake_menu_key = None
            self.update_idletasks()
            if command:
                command()

        for label, command in self._menu_items(key):
            if label is None:
                tk.Frame(panel, bg=self.SHADOW, height=1).pack(fill="x", padx=3, pady=3)
                tk.Frame(panel, bg="#ffffff", height=1).pack(fill="x", padx=3, pady=(0, 2))
                continue

            item = tk.Label(
                panel, text=label, bg=self.PANEL, fg="black", anchor="w",
                font=("Arial", 9), padx=18, pady=3, cursor="hand2"
            )
            item.pack(fill="x", padx=2)
            item.bind("<Enter>", lambda e, w=item: w.config(bg="#000080", fg="white"))
            item.bind("<Leave>", lambda e, w=item: w.config(bg=self.PANEL, fg="black"))
            item.bind("<Button-1>", lambda e, c=command: invoke(c))

        # Calculate coordinates relative to the root window rather than the
        # desktop.  Because this is a child Frame, it always lives above the
        # beige appliance and can never disappear behind it.
        self.update_idletasks()
        x = anchor.winfo_rootx() - self.winfo_rootx()
        y = anchor.winfo_rooty() - self.winfo_rooty() + anchor.winfo_height()

        menu.update_idletasks()
        mw, mh = menu.winfo_reqwidth(), menu.winfo_reqheight()
        rw, rh = max(1, self.winfo_width()), max(1, self.winfo_height())
        x = max(2, min(x, rw - mw - 4))
        y = max(2, min(y, rh - mh - 4))

        menu.place(x=x, y=y)
        menu.lift()

        # No focus_force(), no grab_set(), no Toplevel.  Escape still closes
        # the current dropdown if the root already has keyboard focus.
        self.bind("<Escape>", lambda e: self._close_fake_menu(), add="+")

    def _begin_drag(self, event):
        self._drag_x = event.x_root - self.winfo_x()
        self._drag_y = event.y_root - self.winfo_y()

    def _drag_window(self, event):
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self.geometry(f"+{x}+{y}")

    def click(self):
        """Play an intentionally overenthusiastic mouse clack."""
        wav = resource_path("click.wav")
        try:
            if sys.platform.startswith("win"):
                import winsound
                winsound.PlaySound(str(wav), winsound.SND_FILENAME | winsound.SND_ASYNC)
            elif shutil.which("paplay"):
                subprocess.Popen(["paplay", str(wav)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif shutil.which("aplay"):
                subprocess.Popen(["aplay", "-q", str(wav)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                self.bell()
        except Exception:
            try: self.bell()
            except Exception: pass

    def choose(self):
        """Open the fully faux Win-95 IVTFF file browser.

        Native OS file dialogs do not reliably stay above this application's
        borderless overrideredirect window on Windows/Cinnamon.  The Easter
        Egg and Source/Data dialogs solved that by being borderless faux
        windows too, so the corpus picker deliberately follows the same rule:
        no native dialog, no window-manager z-order argument.
        """
        self._close_fake_menu()
        self.click()
        self.show_ivtff_picker()

    def show_ivtff_picker(self):
        # Reuse an already-open picker rather than creating spectral twins.
        if getattr(self, "_ivttf_window", None):
            try:
                if self._ivttf_window.winfo_exists():
                    win = self._ivttf_window
                    win.deiconify()
                    try: win.attributes("-topmost", True)
                    except Exception: pass
                    win.lift(self)
                    try: self.lower(win)
                    except Exception: pass
                    win.focus_force()
                    return
            except Exception:
                pass

        win = tk.Toplevel(self)
        win.withdraw()
        self._ivttf_window = win
        win.configure(bg=self.WIN_BG)
        win.overrideredirect(True)
        try:
            win.attributes("-topmost", True)
        except Exception:
            pass

        ww, wh = 760, 560
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = max(0, (sw - ww) // 2)
        y = max(0, (sh - wh) // 2)
        win.geometry(f"{ww}x{wh}+{x}+{y}")

        state = {"dir": None, "items": []}

        def restore_main():
            try:
                self.lift()
                self.focus_force()
            except Exception:
                pass

        def close_picker(play_sound=True):
            if play_sound:
                self.click()
            try:
                win.destroy()
            finally:
                self._ivttf_window = None
                restore_main()

        # ----- Faux Windows 95 title bar -----
        title = tk.Frame(win, bg=self.WIN_BLUE, relief="raised", bd=2, height=32)
        title.pack(fill="x", padx=3, pady=(3, 0))
        title.pack_propagate(False)
        title_text = tk.Label(
            title, text="▣  Open IVTFF Corpus", bg=self.WIN_BLUE, fg="white",
            font=("Arial", 10, "bold"), anchor="w"
        )
        title_text.pack(side="left", fill="x", expand=True, padx=6)
        self._classic_button(title, " X ", close_picker, danger=True, padx=9, pady=0).pack(
            side="right", padx=3, pady=2
        )

        drag = {"x": 0, "y": 0}
        def begin_drag(event):
            drag["x"], drag["y"] = event.x_root, event.y_root
        def do_drag(event):
            dx, dy = event.x_root - drag["x"], event.y_root - drag["y"]
            win.geometry(f"+{win.winfo_x()+dx}+{win.winfo_y()+dy}")
            drag["x"], drag["y"] = event.x_root, event.y_root
        for widget in (title, title_text):
            widget.bind("<ButtonPress-1>", begin_drag)
            widget.bind("<B1-Motion>", do_drag)

        body = tk.Frame(win, bg=self.PANEL, relief="raised", bd=2)
        body.pack(fill="both", expand=True, padx=5, pady=5)

        tk.Label(
            body,
            text="FULL REPRODUCTION MODE — SELECT A COMPATIBLE IVTFF TEXT FILE",
            bg="#ffffe1", fg="black", font=("Arial", 9, "bold"),
            relief="sunken", bd=2, pady=5
        ).pack(fill="x", padx=7, pady=(7, 5))

        # Location row.
        locrow = tk.Frame(body, bg=self.PANEL)
        locrow.pack(fill="x", padx=7, pady=(1, 5))
        tk.Label(locrow, text="Look in:", bg=self.PANEL, fg="black").pack(side="left", padx=(0, 5))
        path_var = tk.StringVar()
        path_entry = tk.Entry(locrow, textvariable=path_var, relief="sunken", bd=2)
        path_entry.pack(side="left", fill="x", expand=True)

        # Main browser: quick locations/drives on left, directory listing right.
        browser = tk.Frame(body, bg=self.PANEL)
        browser.pack(fill="both", expand=True, padx=7, pady=2)

        quick = tk.Frame(browser, bg=self.PANEL, relief="sunken", bd=2, width=145)
        quick.pack(side="left", fill="y", padx=(0, 6))
        quick.pack_propagate(False)

        listing_frame = tk.Frame(browser, bg="white", relief="sunken", bd=3)
        listing_frame.pack(side="left", fill="both", expand=True)

        listbox = tk.Listbox(
            listing_frame, bg="white", fg="black", font=("Courier New", 9),
            selectbackground="#000080", selectforeground="white",
            activestyle="none", relief="flat", bd=0
        )
        yscroll = tk.Scrollbar(listing_frame, command=listbox.yview, relief="raised", bd=2)
        listbox.configure(yscrollcommand=yscroll.set)
        yscroll.pack(side="right", fill="y")
        listbox.pack(side="left", fill="both", expand=True)

        selected_var = tk.StringVar(value="No file selected.")
        selected = tk.Label(
            body, textvariable=selected_var, bg="#ffffe1", fg="black",
            anchor="w", relief="sunken", bd=2, padx=5
        )
        selected.pack(fill="x", padx=7, pady=(4, 3))

        def windows_drives():
            if not sys.platform.startswith("win"):
                return []
            drives = []
            for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                root = Path(f"{letter}:/")
                try:
                    if root.exists(): drives.append(root)
                except Exception:
                    pass
            return drives

        def safe_home_child(name):
            candidate = Path.home() / name
            try:
                return candidate if candidate.exists() else None
            except Exception:
                return None

        def load_dir(target):
            try:
                target = Path(target).expanduser().resolve()
                if not target.is_dir():
                    return
                entries = list(target.iterdir())
            except Exception as exc:
                selected_var.set(f"Mr. A: I cannot open that folder. ({exc})")
                return

            dirs = []
            files = []
            for item in entries:
                try:
                    if item.is_dir():
                        dirs.append(item)
                    elif item.is_file() and item.suffix.lower() in (".txt", ".ivtff", ".ivtf"):
                        files.append(item)
                except Exception:
                    continue
            dirs.sort(key=lambda q: q.name.lower())
            files.sort(key=lambda q: q.name.lower())

            state["dir"] = target
            state["items"] = dirs + files
            path_var.set(str(target))
            listbox.delete(0, "end")
            for item in dirs:
                listbox.insert("end", f"[DIR]  {item.name}")
            for item in files:
                listbox.insert("end", f"       {item.name}")
            selected_var.set("Choose an IVTFF/text corpus. Double-click a folder to enter it.")

        def selected_path():
            sel = listbox.curselection()
            if not sel:
                return None
            idx = int(sel[0])
            if idx < 0 or idx >= len(state["items"]):
                return None
            return state["items"][idx]

        def on_select(_event=None):
            item = selected_path()
            if item is None:
                return
            try:
                if item.is_dir():
                    selected_var.set(f"Folder: {item.name}")
                else:
                    selected_var.set(f"Selected: {item.name}")
            except Exception:
                pass

        def activate(_event=None):
            item = selected_path()
            if item is None:
                return
            try:
                if item.is_dir():
                    self.click()
                    load_dir(item)
                else:
                    accept_file(item)
            except Exception as exc:
                selected_var.set(f"Mr. A: The filesystem has objected. ({exc})")

        def go_up():
            self.click()
            cur = state.get("dir")
            if cur is None:
                return
            parent = cur.parent
            if parent == cur:
                # At a drive/root. Stay put rather than wandering into null space.
                selected_var.set("Mr. A: That is the top. Please stop attempting to ascend beyond the filesystem.")
                return
            load_dir(parent)

        def go_typed(_event=None):
            self.click()
            raw = path_var.get().strip()
            if raw:
                load_dir(raw)

        def accept_file(path=None):
            item = Path(path) if path is not None else selected_path()
            if item is None:
                selected_var.set("Mr. A: You must select a file before dramatically pressing OPEN.")
                return
            try:
                if item.is_dir():
                    load_dir(item)
                    return
                if not item.is_file():
                    selected_var.set("Mr. A: That object is not a file. The distinction remains important.")
                    return
            except Exception:
                selected_var.set("Mr. A: I cannot verify that selection as a readable file.")
                return

            p = str(item)
            self.click()
            try:
                win.destroy()
            finally:
                self._ivttf_window = None
            self.corpus = p
            self.pathlabel.config(
                text=f"MODE: FULL REPRODUCTION — {p}", bg="#ffffe1", fg="#000000"
            )
            self.set_result(
                "FULL REPRODUCTION MODE SELECTED.\n\n"
                "Test buttons will recompute results directly from the chosen IVTFF file.\n\n"
                "Use 'Use Bundled Demo' to return to the instant self-contained mode."
            )
            restore_main()

        # Navigation controls.
        nav = tk.Frame(body, bg=self.PANEL)
        nav.pack(fill="x", padx=7, pady=(0, 2))
        self._classic_button(nav, "↑ UP", go_up, padx=10, pady=2).pack(side="left", padx=(0, 4))
        self._classic_button(nav, "GO", go_typed, padx=10, pady=2).pack(side="left")
        tk.Label(nav, text="Files shown: .txt / .ivtff / .ivtf", bg=self.PANEL, fg="#404040").pack(side="right")

        # Quick locations.
        tk.Label(quick, text="PLACES", bg=self.WIN_BLUE, fg="white",
                 font=("Arial", 9, "bold"), relief="raised", bd=1).pack(fill="x")
        places = [
            ("Home", Path.home()),
            ("Desktop", safe_home_child("Desktop")),
            ("Downloads", safe_home_child("Downloads")),
            ("Documents", safe_home_child("Documents")),
        ]
        for label, target in places:
            if target is not None:
                self._classic_button(
                    quick, label,
                    lambda q=target: (self.click(), load_dir(q)),
                    padx=5, pady=3
                ).pack(fill="x", padx=4, pady=2)
        for drive in windows_drives():
            self._classic_button(
                quick, str(drive),
                lambda q=drive: (self.click(), load_dir(q)),
                padx=5, pady=3
            ).pack(fill="x", padx=4, pady=2)

        buttons = tk.Frame(body, bg=self.PANEL)
        buttons.pack(fill="x", padx=7, pady=(3, 7))
        self._classic_button(buttons, "CANCEL", close_picker, padx=14, pady=4).pack(side="right", padx=(5, 0))
        self._classic_button(buttons, "OPEN", accept_file, padx=18, pady=4).pack(side="right")

        listbox.bind("<<ListboxSelect>>", on_select)
        listbox.bind("<Double-Button-1>", activate)
        listbox.bind("<Return>", activate)
        path_entry.bind("<Return>", go_typed)
        win.bind("<Escape>", lambda _e: close_picker())

        # Downloads is the most likely place for a newly obtained corpus; fall
        # back to the user's home directory if it does not exist.
        initial = safe_home_child("Downloads") or Path.home()
        load_dir(initial)

        def force_front():
            try:
                if not win.winfo_exists():
                    return
                try: win.attributes("-topmost", True)
                except Exception: pass
                win.lift(self)
                try: self.lower(win)
                except Exception: pass
                win.focus_force()
            except Exception:
                pass

        # Exactly the same reveal/stacking strategy as the working Easter Egg
        # and Source/Data faux dialogs: geometry first, map second, then nudge.
        win.update_idletasks()
        win.deiconify()
        force_front()
        win.after(20, force_front)
        win.after(100, force_front)
        win.after(300, force_front)

    def use_demo(self):
        self.click()
        self.corpus = None
        self.pathlabel.config(text="MODE: SELF-CONTAINED DEMO — derived aggregate data only; source IVTFF text is not embedded", bg="#ffffe1", fg="#000000")
        self.set_result("GUIDED DEMO MODE RESTORED.\n\nPress a test button. Compiler buttons generate fresh synthetic lines from bundled transition tables.")

    def show_info(self, key):
        h, a, b, c = TEST_INFO[key]
        mode = ("FULL REPRODUCTION MODE: this test will be recomputed from the selected source corpus."
                if self.corpus else
                "GUIDED DEMO MODE: the reference measurement is bundled as derived data. Compiler samples are generated live from aggregate learned transition tables.")
        txt = f"{h}\n\n{a}\n\n{b}\n\n{c}\n\n{mode}"
        self.explain.configure(state="normal")
        self.explain.delete("1.0", "end")
        self.explain.insert("1.0", txt)
        self.explain.configure(state="disabled")

    def set_result(self, txt):
        self.results.configure(state="normal")
        self.results.delete("1.0", "end")
        self.results.insert("1.0", txt)
        self.results.see("1.0")
        self.results.configure(state="disabled")

    def run(self, key):
        self.click()
        self.show_info(key)
        self.set_result("RUNNING...\n\nThe tiny beige gears are turning.")
        if not self.corpus:
            try:
                self.set_result(demo_test(self.demo, key))
            except Exception as e:
                self.set_result(f"ERROR\n{type(e).__name__}: {e}")
            return
        def worker():
            try:
                f = {"corpus":corpus_test, "slots":slots_test, "currier":currier_test,
                     "v1":lambda p:compiler_test(p,1), "v2":lambda p:compiler_test(p,2),
                     "geometry":geometry_test}[key]
                r = f(self.corpus)
                self.after(0, lambda: self.set_result(r))
            except Exception as e:
                self.after(0, lambda: self.set_result(f"ERROR\n{type(e).__name__}: {e}"))
        threading.Thread(target=worker, daemon=True).start()

    def run_all(self):
        self.click()
        self.set_result("RUNNING THE WHOLE LITTLE MACHINE...\n\nPlease do not feed the compiler after midnight.")
        if not self.corpus:
            try:
                chunks=[]
                for key in ("corpus","slots","currier","v1","v2","geometry"):
                    chunks.append(TEST_INFO[key][0] + "\n" + demo_test(self.demo,key))
                self.set_result(("\n\n" + ("\n\n" + "="*72 + "\n\n").join(chunks)).strip())
            except Exception as e:
                self.set_result(f"ERROR\n{type(e).__name__}: {e}")
            return
        def worker():
            try:
                chunks=[]
                for key,fn in [("corpus",corpus_test),("slots",slots_test),("currier",currier_test),
                               ("v1",lambda p:compiler_test(p,1)),("v2",lambda p:compiler_test(p,2)),
                               ("geometry",geometry_test)]:
                    chunks.append(TEST_INFO[key][0] + "\n" + fn(self.corpus))
                txt=("\n\n" + ("\n\n" + "="*72 + "\n\n").join(chunks)).strip()
                self.after(0, lambda: self.set_result(txt))
            except Exception as e:
                self.after(0, lambda: self.set_result(f"ERROR\n{type(e).__name__}: {e}"))
        threading.Thread(target=worker, daemon=True).start()

    def _reset_fact_timer(self):
        try:
            if getattr(self, "_fact_timer", None):
                self.after_cancel(self._fact_timer)
        except Exception:
            pass
        self._fact_timer = self.after(20000, self._cycle_fact)

    def next_fact(self):
        self.click()
        self.fact_i = (self.fact_i + 1) % len(FACTS)
        self.fact.config(text=FACTS[self.fact_i])
        self._reset_fact_timer()

    def _cycle_fact(self):
        self.fact_i = (self.fact_i + 1) % len(FACTS)
        self.fact.config(text=FACTS[self.fact_i])
        self._fact_timer = self.after(20000, self._cycle_fact)

    def toggle_music(self):
        self.click()
        wav = resource_path("voynich_lute_tempus_perfectum.wav")
        if not wav.exists():
            messagebox.showinfo("No lute found", "The lute WAV is missing from assets/.")
            return
        if self.music:
            self.stop_music()
            return
        try:
            if sys.platform.startswith("win"):
                import winsound
                winsound.PlaySound(str(wav), winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
            elif shutil.which("paplay"):
                self._musicproc = subprocess.Popen(["paplay", str(wav)])
            elif shutil.which("aplay"):
                self._musicproc = subprocess.Popen(["aplay", str(wav)])
            else:
                raise RuntimeError("No supported WAV player found")
            self.music = True
            self.musicbtn.config(text="⏸ PAUSE LUTE")
        except Exception as e:
            messagebox.showinfo("Lute unavailable", str(e))

    def stop_music(self):
        try:
            if sys.platform.startswith("win"):
                import winsound
                winsound.PlaySound(None, winsound.SND_PURGE)
            elif hasattr(self, "_musicproc") and self._musicproc.poll() is None:
                self._musicproc.terminate()
        except Exception:
            pass
        self.music = False
        if hasattr(self, "musicbtn"):
            self.musicbtn.config(text="▶ PLAY LUTE")

    def show_about(self):
        self.click()

        # Use our own faux Win-9x dialog instead of a native messagebox.
        # The main application is borderless (overrideredirect), and native
        # dialogs can occasionally lose the stacking/focus fight on some desktops.
        if getattr(self, "_about_window", None):
            try:
                if self._about_window.winfo_exists():
                    self._about_window.deiconify()
                    try:
                        self._about_window.attributes("-topmost", True)
                    except Exception:
                        pass
                    self._about_window.lift(self)
                    try:
                        self.lower(self._about_window)
                    except Exception:
                        pass
                    self._about_window.focus_force()
                    return
            except Exception:
                pass

        # Cinnamon/X11 treats the main overrideredirect window as an unmanaged
        # surface. A normal managed Toplevel can therefore wind up *behind* it.
        # Make the confession box borderless too, keep it hidden until its final
        # geometry is known, then explicitly stack it above the main appliance.
        win = tk.Toplevel(self)
        win.withdraw()
        self._about_window = win
        win.configure(bg=self.WIN_BG)
        win.overrideredirect(True)
        try:
            win.attributes("-topmost", True)
        except Exception:
            pass

        ww, wh = 720, 620
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = max(0, (sw - ww) // 2)
        y = max(0, (sh - wh) // 2)
        win.geometry(f"{ww}x{wh}+{x}+{y}")

        def close_about():
            self.click()
            try:
                win.destroy()
            finally:
                self._about_window = None
                # Return the faux main window to the front after its confession
                # box has been deliberately CLACKED out of existence.
                try:
                    self.lift()
                    self.focus_force()
                except Exception:
                    pass

        title = tk.Frame(win, bg=self.WIN_BLUE, relief="raised", bd=2, height=32)
        title.pack(fill="x", padx=3, pady=(3,0))
        title.pack_propagate(False)
        title_text = tk.Label(title, text="▣  About the traps", bg=self.WIN_BLUE, fg="white",
                              font=("Arial", 10, "bold"), anchor="w")
        title_text.pack(side="left", fill="x", expand=True, padx=6)
        self._classic_button(title, " X ", close_about, danger=True, padx=9, pady=0).pack(side="right", padx=3, pady=2)

        # Faux titlebar dragging: no Cinnamon/Mint decoration required.
        drag = {"x": 0, "y": 0}
        def begin_about_drag(event):
            drag["x"], drag["y"] = event.x_root, event.y_root
        def drag_about(event):
            dx, dy = event.x_root - drag["x"], event.y_root - drag["y"]
            nx, ny = win.winfo_x() + dx, win.winfo_y() + dy
            win.geometry(f"+{nx}+{ny}")
            drag["x"], drag["y"] = event.x_root, event.y_root
        for widget in (title, title_text):
            widget.bind("<ButtonPress-1>", begin_about_drag)
            widget.bind("<B1-Motion>", drag_about)

        body = tk.Frame(win, bg=self.PANEL, relief="raised", bd=2)
        body.pack(fill="both", expand=True, padx=5, pady=5)

        tk.Label(body, text="CONFESSION BOX / EPISTEMIC BANANA PEEL REGISTER",
                 bg="#ffff00", fg="black", font=("Arial", 10, "bold"), relief="sunken", bd=2,
                 pady=5).pack(fill="x", padx=7, pady=(7,5))

        text_frame = tk.Frame(body, bg="white", relief="sunken", bd=3)
        text_frame.pack(fill="both", expand=True, padx=7, pady=5)
        txt = tk.Text(text_frame, wrap="word", bg="white", fg="black", font=("Arial", 10),
                      padx=12, pady=10, relief="flat", bd=0, spacing1=2, spacing3=5)
        scroll = tk.Scrollbar(text_frame, command=txt.yview, relief="raised", bd=2)
        txt.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        txt.pack(side="left", fill="both", expand=True)

        about_text = (
            "TRAP NUMBER ONE: THE MICROSCOPIC BROKEN TEST\n\n"
            "One test file in the original repository contains a deliberate syntax error: a single missing colon. "
            "Nothing clever. The Python interpreter stops on it immediately.\n\n"
            "Why put a missing colon in a public repository? Because if a reviewer declares that they ran the entire "
            "repository from top to bottom without ever mentioning that one supplied file does not even parse, then an "
            "experiment has succeeded. Not an experiment on the Voynich Manuscript. An experiment on the reviewer.\n\n"
            "It is an epistemic banana peel: remarkably inexpensive, extremely easy to detect, and useful only as a test "
            "of whether the executable material was actually inspected. This guided Windows appliance runs the corrected "
            "calculation; the original repository keeps the missing colon for posterity.\n\n"
            "OTHER EASTER EGGS / TRAPS\n\n"
            "• THE REPORTS ARE NOT SACRED TEXT. Some prose reports were assembled across slightly different parser/compiler "
            "iterations. If prose and executable code disagree, the intended response is to run the code, inspect the version, "
            "and determine why. The trap is treating polished documentation as more authoritative than executable evidence.\n\n"
            "• THE FORBIDDEN LUTE. The medieval-flavored lute experiment is sonification: model features are mapped into sound "
            "so structural patterns can be heard. It is deliberately framed theatrically, but it is not evidence that the "
            "Voynich Manuscript was written as lute music. The project says so repeatedly because the joke depends on the "
            "inferential gap being visible.\n\n"
            "• THE RENAISSANCE COMPUTER COVER. The large AI-rendered renaissance-style image of bards gathered around an "
            "obviously modern computer was not an accidental lapse in historical seriousness. It was a gigantic visual hint "
            "that the presentation was knowingly absurd: a commentary on the commentary, and on how quickly presentation can "
            "override inspection of the underlying method.\n\n"
            "• THE REAL TRAP: CATEGORY COLLAPSE. Source data, measurement, model, representation, interpretation, and historical "
            "claim are different layers. The repository intentionally makes those boundaries easy to trip over. An enthusiastic "
            "reader can overclaim from the model; a dismissive reader can reject the measurements because the presentation is "
            "ridiculous. Both reactions skip the executable middle.\n\n"
            "THE POINT\n\n"
            "The traps are not hidden data manipulation and they are not substitutes for evidence. They are jokes, reading-habit "
            "tests, and reminders to privilege reproducible calculations over authority, aesthetics, or vibes. This companion "
            "demo removes the ambiguity by labeling source, measurement, interpretation, and joke separately.\n\n"
            "Mister B, you may now close the confession box."
        )
        txt.insert("1.0", about_text)
        txt.configure(state="disabled")

        buttons = tk.Frame(body, bg=self.PANEL)
        buttons.pack(fill="x", padx=7, pady=(2,7))
        self._classic_button(buttons, "OK, I HAVE SEEN THE BANANA PEEL", close_about, padx=12, pady=5).pack(side="right")

        def force_about_front():
            try:
                if not win.winfo_exists():
                    return
                # Both windows are now overrideredirect surfaces on Cinnamon.
                # Establish their relative z-order explicitly instead of asking
                # the window manager to arbitrate between managed/unmanaged ones.
                try:
                    win.attributes("-topmost", True)
                except Exception:
                    pass
                win.lift(self)
                try:
                    self.lower(win)
                except Exception:
                    pass
                win.focus_force()
            except Exception:
                pass

        # Do not map the window at (0,0) first; that caused the brief top-left
        # flash on Cinnamon. Its final geometry is already set above.
        win.update_idletasks()
        win.deiconify()
        force_about_front()
        win.after(20, force_about_front)
        win.after(100, force_about_front)
        win.after(300, force_about_front)

    def show_source_note(self):
        self.click()

        if getattr(self, "_source_window", None):
            try:
                if self._source_window.winfo_exists():
                    self._source_window.deiconify()
                    self._source_window.lift(self)
                    try: self._source_window.attributes("-topmost", True)
                    except Exception: pass
                    self._source_window.focus_force()
                    return
            except Exception:
                pass

        win = tk.Toplevel(self)
        win.withdraw()
        self._source_window = win
        win.configure(bg=self.WIN_BG)
        win.overrideredirect(True)
        try:
            win.attributes("-topmost", True)
        except Exception:
            pass

        ww, wh = 680, 470
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = max(0, (sw - ww) // 2)
        y = max(0, (sh - wh) // 2)
        win.geometry(f"{ww}x{wh}+{x}+{y}")

        def close_source():
            self.click()
            try:
                win.destroy()
            finally:
                self._source_window = None
                try:
                    self.lift(); self.focus_force()
                except Exception:
                    pass

        title = tk.Frame(win, bg=self.WIN_BLUE, relief="raised", bd=2, height=32)
        title.pack(fill="x", padx=3, pady=(3,0))
        title.pack_propagate(False)
        title_text = tk.Label(title, text="▣  Source / data note", bg=self.WIN_BLUE, fg="white",
                              font=("Arial", 10, "bold"), anchor="w")
        title_text.pack(side="left", fill="x", expand=True, padx=6)
        self._classic_button(title, " X ", close_source, danger=True, padx=9, pady=0).pack(side="right", padx=3, pady=2)

        drag = {"x": 0, "y": 0}
        def begin_drag(event):
            drag["x"], drag["y"] = event.x_root, event.y_root
        def do_drag(event):
            dx, dy = event.x_root-drag["x"], event.y_root-drag["y"]
            win.geometry(f"+{win.winfo_x()+dx}+{win.winfo_y()+dy}")
            drag["x"], drag["y"] = event.x_root, event.y_root
        for widget in (title, title_text):
            widget.bind("<ButtonPress-1>", begin_drag)
            widget.bind("<B1-Motion>", do_drag)

        body = tk.Frame(win, bg=self.PANEL, relief="raised", bd=2)
        body.pack(fill="both", expand=True, padx=5, pady=5)
        tk.Label(body, text="SOURCE PROVENANCE / REPRODUCTION PATH",
                 bg="#ffffe1", fg="black", font=("Arial", 10, "bold"), relief="sunken", bd=2,
                 pady=5).pack(fill="x", padx=7, pady=(7,5))

        text_frame = tk.Frame(body, bg="white", relief="sunken", bd=3)
        text_frame.pack(fill="both", expand=True, padx=7, pady=5)
        txt = tk.Text(text_frame, wrap="word", bg="white", fg="black", font=("Arial", 10),
                      padx=12, pady=10, relief="flat", bd=0, spacing1=2, spacing3=6)
        scroll = tk.Scrollbar(text_frame, command=txt.yview, relief="raised", bd=2)
        txt.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        txt.pack(side="left", fill="both", expand=True)
        source_text = (
            "REFERENCE SOURCE\n\n"
            "The reference analysis uses the Landini–Stolfi Interlinear (LSI) IVTFF archive, selecting Takeshi "
            "Takahashi ;H EVA transcription lines.\n\n"
            "WHAT IS BUNDLED HERE\n\n"
            "The self-contained Guided Demo does NOT embed or redistribute the source IVTFF transcription. It bundles "
            "project-derived aggregate measurements and trained count/transition tables produced from the reference run. "
            "Those derived tables are sufficient for the guided measurements and for generating fresh synthetic compiler lines.\n\n"
            "FULL REPRODUCTION MODE\n\n"
            "A researcher may independently obtain a compatible original IVTFF corpus, choose 'Full Reproduction: Choose IVTFF...' "
            "and rerun the parser and analysis directly against that file. This is the audit path: the bundled demo is convenient; "
            "the source mode is reproducible.\n\n"
            "WHAT THIS DOES NOT DO\n\n"
            "Selecting a transcription does not establish a translation, authorship, cipher system, language, or historical mechanism. "
            "The program measures surface structure under explicit analytical assumptions.\n\n"
            "Mr. A's note: This box is intentionally less exciting than the lute. That is usually a good sign in a provenance statement."
        )
        txt.insert("1.0", source_text)
        txt.configure(state="disabled")

        buttons = tk.Frame(body, bg=self.PANEL)
        buttons.pack(fill="x", padx=7, pady=(2,7))
        self._classic_button(buttons, "OK, SHOW ME THE BUTTONS AGAIN", close_source, padx=12, pady=5).pack(side="right")

        def force_front():
            try:
                if not win.winfo_exists(): return
                try: win.attributes("-topmost", True)
                except Exception: pass
                win.lift(self)
                try: self.lower(win)
                except Exception: pass
                win.focus_force()
            except Exception:
                pass

        win.update_idletasks()
        win.deiconify()
        force_front()
        win.after(20, force_front)
        win.after(100, force_front)
        win.after(300, force_front)

    def destroy(self):
        self.stop_music()
        super().destroy()

if __name__ == "__main__":
    App().mainloop()
