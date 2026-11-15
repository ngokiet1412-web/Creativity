"""Retiming authored segment keys to recorded phrases, without altering audio.
The V6 scene is recovered from Git so repeated runs cannot accumulate offsets.
"""
import json
from pathlib import Path
import re
import subprocess
import numpy as np

BASE = '95d7f591e84276c0773402f9dadf55b0e306a677'

def retime_segment(tag, lines, demo, voice_file, media_len):
    demo = Path(demo).resolve()
    root = demo.parents[2]
    def get(rel):
        return subprocess.check_output(['git', 'show', f'{BASE}:{rel}'], cwd=root).decode('utf-8')
    rel = f'episodes/EP02/demo_v4/segments_sc03_sc05/EP02_{tag}_vi.srt'
    source = get(rel)
    def tm(s):
        h, m, sec = s.replace(',', '.').split(':')
        return int(h)*3600 + int(m)*60 + float(sec)
    old = []
    for block in source.strip().split('\n\n'):
        ln = block.splitlines()
        a, b = ln[1].split(' --> ')
        role, text = ' '.join(ln[2:]).split(': ', 1)
        old.append({'who': 'CAPY' if role == 'CAPY' else 'KS', 'text': text, 't0': tm(a), 't1': tm(b)})
    sn = tag.lower() + ('_v42' if tag == 'SC05' else '')
    path = f'episodes/EP02/demo_v4/godot/segments/{sn}.tscn'
    scene = get(path)
    old_length = float(re.search(r'^length = ([\d.]+)', scene, re.M)[1])
    t, ci, cues, voices, knots = old[0]['t0'], 0, [], [], [(0., 0.)]
    for idx, (who, text) in enumerate(lines):
        group = []
        while ci < len(old) and old[ci]['who'] == who and old[ci]['text'] in text:
            group.append(old[ci]); ci += 1
        assert group, (tag, idx, text)
        vf = voice_file(tag, idx, who)
        if not vf:
            raise FileNotFoundError(f'Voice missing: {tag}_{idx+1:02d}_{who}')
        meta = json.loads(Path(vf).with_suffix('.json').read_text(encoding='utf-8'))
        voices.append({'file': vf, 't0': round(t, 3), 'who': who, 'line': idx})
        # Locate original cue snippets in the matching recorded sentence.
        def locate(snippet, end=False):
            pos = text.find(snippet)
            assert pos >= 0, (tag, snippet)
            pos += len(snippet) if end else 0
            cursor = 0
            for c in meta['cues']:
                begin = text.find(c['text'], cursor)
                assert begin >= 0, (tag, c)
                finish = begin + len(c['text'])
                if begin <= pos <= finish:
                    u = (pos - begin) / len(c['text'])
                    return t + c['t0'] + u * (c['t1'] - c['t0'])
                cursor = finish
            raise ValueError((tag, snippet))
        for c in group:
            knots += [(c['t0'], locate(c['text'])), (c['t1'], locate(c['text'], True))]
        for c in meta['cues']:
            cues.append({'who': who, 'line': idx, 'text': c['text'], 't0': round(t+c['t0'], 3), 't1': round(t+c['t1'], 3)})
        t += media_len(vf) + 0.65
    length = t + 1.1
    knots.append((old_length, length))
    knots.sort()
    assert all(b[0] > a[0] and b[1] >= a[1] for a, b in zip(knots, knots[1:])), (tag, knots)
    def warp(x):
        return float(np.interp(x, [k[0] for k in knots], [k[1] for k in knots]))
    def times(match):
        return '"times": PackedFloat32Array(' + ', '.join(f'{warp(float(x)):.5f}' for x in match[1].split(',')) + ')'
    scene = re.sub(r'"times": PackedFloat32Array\(([^)]*)\)', times, scene)
    scene = re.sub(r'^length = [\d.]+', f'length = {length:.5f}', scene, flags=re.M)
    scene = scene.replace(f'scene_tag = "{tag}"', f'scene_tag = "{tag}"\nretime_keys = PackedVector2Array(' + ', '.join(f'{x:.5f}, {y:.5f}' for x, y in knots) + ')')
    (root / path).write_text(scene, encoding='utf-8')
    return {'length': round(length, 3), 'marks': {}, 'cues': cues, 'voices': voices, 'retime_keys': knots}
