#!/usr/bin/env python3
"""
EXTRACTOR V5 - Estrategia definitiva mejorada:
- Detecta letras a/b/c/d y las elimina de las opciones
- Mejor heurística para separar pregunta vs opciones
- Radio Comunicaciones acepta preguntas de 2 opciones (Si/No, Verdadero/Falso)
- Para Daypo: las primeras opciones listadas son la respuesta correcta (index 0)
"""
import urllib.request
import re
import html as html_mod
import json
import hashlib

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

daypo_urls = [
    ('https://www.daypo.com/tes-validacion-n2.html',         'TES DE VALIDACION N2'),
    ('https://www.daypo.com/validacion-n1.html',             'Test Validacion N1'),
    ('https://www.daypo.com/estandares-2.html',              'ESTANDARES'),
    ('https://www.daypo.com/mandatorios-7.html',             'Mandatorios 7'),
    ('https://www.daypo.com/mandatorios.html',               'Mandatorios'),
    ('https://www.daypo.com/competencias-4.html',            'Test de Competencias'),
    ('https://www.daypo.com/nivelacion-mandatorios.html',    'Nivelacion Mandatorios'),
]

educaplay_urls = [
    ('24711897', 'test_de_mandatorios_de_la_policia_nacional.html', 'Mandatorios Educaplay'),
    ('25300876', 'radio_de_comunicaciones_policial.html',           'Radio Comunicaciones Policial'),
]

all_questions = []
seen_hashes = set()

def clean_text(t):
    t = html_mod.unescape(t)
    t = re.sub(r'<[^>]+>', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def q_hash(q):
    norm = re.sub(r'[^a-z0-9]', '', q.lower())[:80]
    return hashlib.md5(norm.encode()).hexdigest()

def fetch(url):
    req = urllib.request.Request(url, headers=headers)
    return urllib.request.urlopen(req, timeout=20).read().decode('utf-8', errors='ignore')

def strip_letter_prefix(text):
    """Remove leading 'a. ' 'b. ' 'c. ' 'd. ' '1. ' '2. ' etc from option text"""
    text = text.strip()
    text = re.sub(r'^[a-dA-D1-9][\.\)]\s*', '', text).strip()
    return text

def is_bridge_ending(text):
    """Returns True if text ends with prepositions/articles - meaning it's not complete, next part belongs to same sentence"""
    t = text.lower().rstrip()
    # Ends with articles, prepositions, connectors
    bridge_patterns = [
        r'\b(a la|al|el|la|los|las|de|del|sobre|para|que|en|con|por|sin|hacia|desde|a)\s*$',
        r'\b(son:|es:|siguiente:|siguientes:|como:|tales:|son los|son las|es el|es la)\s*$',
        r'[,;:]\s*$',
    ]
    for p in bridge_patterns:
        if re.search(p, t):
            return True
    return False

def parse_paragraph(p):
    """
    Strategy V5:
    1. Remove leading number "1. " or "10. "
    2. Split by ". " 
    3. Remove letter prefixes (a. b. c. d.) from segments
    4. Classify: question parts (long/complex) vs options (short/simple)
    5. Build back question from non-option parts
    6. First option in original order = correct answer (index 0)
    """
    if len(p) < 20:
        return None, []

    # Remove leading number "1. " or "10. " or "15. "
    p = re.sub(r'^\s*\d{1,2}[\.\)]\s+', '', p).strip()

    # === STRATEGY 1: Check for explicit letter markers a. b. c. d. in text ===
    # Pattern like "...question text. a. option1. b. option2. c. option3. d. option4"
    # or "...question. a) option. b) option..."
    letter_pattern = re.compile(
        r'^(.*?)\s*[Aa][\.\)]\s*(.+?)\s*[Bb][\.\)]\s*(.+?)\s*[Cc][\.\)]\s*(.+?)(?:\s*[Dd][\.\)]\s*(.+?))?\.?\s*$',
        re.DOTALL
    )
    m = letter_pattern.match(p)
    if m:
        question = m.group(1).strip().rstrip('.')
        opts = []
        for i in range(2, 7):
            try:
                val = m.group(i)
            except IndexError:
                break
            if val:
                opt = val.strip().rstrip('.')
                # Remove trailing letter of next option if present
                opt = re.sub(r'\s+[a-dA-D]$', '', opt).strip()
                if opt and len(opt) > 1:
                    opts.append(opt)
        if 2 <= len(opts) <= 4 and len(question) > 15:
            return question, opts[:4]

    # === STRATEGY 2: Split by ". " and analyze segments ===
    # First, try splitting on "?. " as question boundary
    q_boundary = re.search(r'(\?)\.\s+', p)
    if q_boundary:
        q_part = p[:q_boundary.start()+1]
        opts_text = p[q_boundary.end():]
        # Parse options from rest
        raw_opts = re.split(r'\.\s+', opts_text)
        opts = []
        for o in raw_opts:
            o_clean = strip_letter_prefix(o.strip().rstrip('.'))
            if o_clean and len(o_clean) > 1 and len(o_clean.split()) < 25:
                opts.append(o_clean)
        # Keep at most 4 options  
        if 2 <= len(opts[:4]) <= 4:
            return q_part.strip(), opts[:4]

    # === STRATEGY 3: Split by ". " and find option boundary ===
    parts = [pt.strip().rstrip('.') for pt in re.split(r'\.\s+', p) if pt.strip()]
    
    if len(parts) < 2:
        return p, []

    # Clean letter prefixes from ALL parts (some have "a. " "b. " etc)
    cleaned_parts = []
    for pt in parts:
        # Check if this part is ONLY a letter like "a" "b" "c" "d" - skip it
        if re.match(r'^[a-dA-D1-9]$', pt.strip()):
            continue
        cleaned = strip_letter_prefix(pt.strip())
        if cleaned:
            cleaned_parts.append(cleaned)
    
    parts = cleaned_parts
    
    if len(parts) < 2:
        return p, []

    # Score each part: how "option-like" vs "question-like"
    def is_option_like(text, all_parts, pos):
        """Returns True if this segment looks like an answer option."""
        words = text.split()
        char_len = len(text)
        
        # Very long = question (> 100 chars)
        if char_len > 120:
            return False
        
        # Very short single words OK as option
        if char_len < 5 and len(words) == 1:
            return True
        
        # Ends with bridge word = NOT an option (it's continuation of question)
        if is_bridge_ending(text):
            return False
        
        # Contains question markers = likely NOT an option
        question_markers = r'^(de acuerdo|conforme|seg[uú]n|cuando|si |toda|una vez|en caso|la guía|el manual|la resolución|el artículo|según|identifique|seleccione|cuál|qué|cuáles|determine|indique|marque|escoja|señale)'
        if re.match(question_markers, text.lower()):
            return False
        
        # Contains article/law references = part of question
        if re.search(r'artículo|numeral|literal|resolución|decreto|ley \d|código', text.lower()):
            return False
        
        # Contains colon at end = question continuation  
        if text.rstrip().endswith(':'):
            return False
        
        # Short text (< 80 chars) with simple structure = likely option
        if char_len < 80:
            return True
            
        return False  # Long and complex = question part

    # Find the split point: scan from end, find consecutive option-like segments
    # Try 4, 3, 2 options
    best_q_parts = None
    best_opts = None
    
    for n_opts in [4, 3, 2]:
        if len(parts) <= n_opts:
            continue
        q_parts = parts[:len(parts) - n_opts]
        o_parts = parts[len(parts) - n_opts:]
        
        # All options must look like options
        all_ok = all(is_option_like(o, parts, len(parts)-n_opts+i) for i, o in enumerate(o_parts))
        # All question parts must NOT look like options (or at least first 2 should be question-like)
        q_looks_like_question = not is_option_like(q_parts[-1], parts, len(q_parts)-1) if q_parts else True
        
        # Option length check: average < 80, max < 150
        avg_len = sum(len(o) for o in o_parts) / len(o_parts) if o_parts else 0
        max_len = max(len(o) for o in o_parts) if o_parts else 0
        
        if all_ok and avg_len < 90 and max_len < 160:
            best_q_parts = q_parts
            best_opts = o_parts
            break
    
    if best_q_parts is not None and best_opts:
        question = '. '.join(best_q_parts).strip()
        return question, best_opts
    
    # === FALLBACK: Take last 4 segments, they're options by default ===
    if len(parts) >= 5:
        q_parts = parts[:-4]
        o_parts = parts[-4:]
        avg_len = sum(len(o) for o in o_parts) / 4
        if avg_len < 100:
            question = '. '.join(q_parts).strip()
            return question, o_parts
    
    # Return full text as question, no options
    return '. '.join(parts), []


all_questions = []
seen_hashes = set()

def add_q(question, options, source, correct_idx=0):
    if not question or len(question) < 15:
        return False
    h = q_hash(question)
    if h in seen_hashes:
        return False
    seen_hashes.add(h)
    # Cap to 4 options max
    opts = [o for o in options[:4] if o and len(str(o)) > 0]
    if len(opts) < 2:
        opts = ['(Ver enunciado)']
    correct_idx = min(correct_idx, len(opts)-1)
    all_questions.append({
        'question': question.strip().lstrip('.').strip(),
        'options': opts,
        'correct': correct_idx,
        'source': source
    })
    return True


# ======= DAYPO =======
for url, source_name in daypo_urls:
    print(f"[Daypo] {url}")
    try:
        raw = fetch(url)
    except Exception as e:
        print(f"  ERROR: {e}"); continue

    match = re.search(r"itemprop='text'[^>]*>(.*?)</td>", raw, re.DOTALL)
    if not match:
        match = re.search(r'itemprop="text"[^>]*>(.*?)</td>', raw, re.DOTALL)
    if not match:
        print("  No data"); continue

    paragraphs = re.findall(r'<p>(.*?)</p>', match.group(1), re.DOTALL)
    count = 0
    skipped = 0
    for p_raw in paragraphs:
        p = clean_text(p_raw)
        question, options = parse_paragraph(p)
        if question and len(options) >= 2:
            if add_q(question, options, source_name, correct_idx=0):
                count += 1
        else:
            skipped += 1
    print(f"  -> {count} preguntas ({skipped} omitidas/sin opciones)")


# ======= EDUCAPLAY =======
for rid, slug, source_name in educaplay_urls:
    print_url = f'https://es.educaplay.com/vista-impresion/{rid}-{slug}'
    print(f"[Educaplay] {print_url}")
    try:
        raw = fetch(print_url)
    except Exception as e:
        print(f"  ERROR: {e}"); continue

    sections = re.findall(r'<section[^>]*gameboard__screen[^>]*>(.*?)</section>', raw, re.DOTALL)
    count = 0
    for sec in sections:
        qm = re.search(r'<h3[^>]*>(.*?)</h3>', sec, re.DOTALL)
        if not qm:
            continue
        question = clean_text(qm.group(1))
        answers = re.findall(r'<p class="gameboard__screen__answer__body">(.*?)</p>', sec, re.DOTALL)
        options = [clean_text(a) for a in answers if clean_text(a)]
        # For educaplay, we DON'T know correct answer index (no metadata)
        # Use index 0 as default (will be shuffled at display)
        if add_q(question, options[:4], source_name, correct_idx=0):
            count += 1
    print(f"  -> {count} preguntas")


# Save JSON
out_path = r'C:\Users\GHOST1D\.gemini\antigravity\brain\2f09f0ca-32d6-4b4a-b5bc-4e7e88f98711\scratch\questions_data.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(all_questions, f, ensure_ascii=False, indent=2)

print(f"\nTOTAL: {len(all_questions)} preguntas")
from collections import Counter
c = Counter(len(q['options']) for q in all_questions)
for n, cnt in sorted(c.items()):
    mark = " OK" if n >= 2 else f" <-- PROBLEMA"
    print(f"  {n} opts: {cnt}{mark}")

# Show still-bad ones
bad = [q for q in all_questions if len(q['options']) < 2 or (len(q['options']) == 1 and q['options'][0]=='(Ver enunciado)')]
if bad:
    print(f"\nPreguntas sin opciones validas: {len(bad)}")
    for q in bad[:5]:
        print(f"  - {q['question'][:80]} [{q['source']}]")
