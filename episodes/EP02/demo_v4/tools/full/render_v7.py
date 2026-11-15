"""Render and mix an editable voiced V7 DRAFT; explicit audio mapping is essential.

Environment: GODOT, FFMPEG, FFPROBE. No uploads. Unapproved voice auditions stay
in godot/local and are included only in the local owner-review package.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import textwrap
import wave

import numpy as np
from PIL import Image, ImageDraw

DEMO = Path(__file__).resolve().parents[2]
ROOT = DEMO.parents[2]
PROJECT = DEMO / 'godot'
FF = os.environ.get('FFMPEG', 'ffmpeg')
PROBE = os.environ.get('FFPROBE', 'ffprobe')
GODOT = os.environ.get('GODOT', 'godot')
TIMING = json.loads((PROJECT / 'full/timing.json').read_text(encoding='utf-8'))['scenes']
from assemble import bed

ORDER = [f'SC{i:02}' for i in range(1, 15)]
MIX_VERSIONS = ('V8', 'V9', 'V10')
BUMPER_VERSIONS = ('V9', 'V10')

def run(cmd, log=None, cwd=None):
    kw = {'cwd': cwd}
    if os.name == 'nt':
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0
        kw.update(startupinfo=si, creationflags=subprocess.CREATE_NO_WINDOW)
    if log:
        with open(log, 'w', encoding='utf-8') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, **kw)
        if result.returncode:
            raise RuntimeError(Path(log).read_text(encoding='utf-8', errors='replace')[-5000:])
    else:
        subprocess.run(cmd, check=True, **kw)

def scene_path(sc):
    if sc in ('SC03', 'SC04', 'SC05'):
        return f'res://segments/{sc.lower()}' + ('_v42' if sc == 'SC05' else '') + '.tscn'
    return f'res://full/{sc.lower()}.tscn'

def stamps(s):
    n = int(round(s * 1000))
    return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'

def subtitle_cues(sc, version='V7'):
    out = []
    for c in TIMING[sc]['cues']:
        if version in BUMPER_VERSIONS and sc == 'SC01' and c['text'] == 'Kĩ Sư Ơiiii!':
            continue
        # Caption cue max 2x42 characters, without re-reading speaker prefixes.
        def wrap(text):
            return textwrap.wrap(text, 42, break_long_words=False, break_on_hyphens=False)
        lines = wrap(c['text'])
        groups = ['\n'.join(lines[i:i+2]) for i in range(0, len(lines), 2)]
        if len(groups) > 1 and len(groups[-1].split()) <= 2:
            words = ' '.join(groups[-2:]).split()
            middle = len(words) // 2
            left = wrap(' '.join(words[:middle]))
            right = wrap(' '.join(words[middle:]))
            if len(left) <= 2 and len(right) <= 2:
                groups[-2:] = ['\n'.join(left), '\n'.join(right)]
        total = sum(len(g.split()) for g in groups)
        t = c['t0']
        for g in groups:
            d = (c['t1'] - c['t0']) * len(g.split()) / total
            out.append((t, t + d, g))
            t += d
    return out

def subtitle_file(path, cues):
    path.write_text(''.join(f'{i}\n{stamps(a)} --> {stamps(b)}\n{txt}\n\n' for i, (a,b,txt) in enumerate(cues, 1)), encoding='utf-8')

def probe(path):
    return json.loads(subprocess.check_output([PROBE, '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)]))

def mix(sc, folder, length, version):
    ambient = folder / f'{sc}_ambience.wav'
    if version in MIX_VERSIONS:
        from foley_v8 import soundscape
        soundscape(sc, TIMING[sc], length, ambient, bumper=version in BUMPER_VERSIONS)
    else:
        bed(sc, length, str(ambient))
    voices = TIMING[sc]['voices']
    assert voices, f'{sc} is missing spoken audio'
    cmd = [FF, '-v', 'error', '-y', '-i', str(ambient)]
    filters = [f'[0:a]volume={0.84 if version in MIX_VERSIONS else 0.22}[bed]']
    previous_end = 0
    for i, v in enumerate(voices):
        voice = PROJECT / v['file']
        with wave.open(str(voice), 'rb') as f:
            d = f.getnframes() / f.getframerate()
            samples = np.frombuffer(f.readframes(f.getnframes()), '<i2')
            assert samples.max() > 100, f'Empty voice {v["file"]}'
        assert v['t0'] >= previous_end - 0.002, (sc, 'overlapping speakers')
        previous_end = v['t0'] + d
        assert previous_end <= length + 0.04, (sc, 'voice cut off')
        cmd += ['-i', str(voice)]
        gain = 'volume=3dB,' if version in MIX_VERSIONS else ''
        # Let the new instrumental bumper take the slot of the old voice tag.
        # Delay the trimmed WAV by the same duration to keep the hook in sync.
        intro_trim = 2.81 if version in BUMPER_VERSIONS and sc == 'SC01' and i == 0 and TIMING[sc]['cues'][0]['text'] == 'Kĩ Sư Ơiiii!' else 0.0
        trim = f'atrim=start={intro_trim},asetpts=PTS-STARTPTS,' if intro_trim else ''
        delay = round((v['t0'] + intro_trim) * 1000)
        filters.append(f'[{i+1}:a]{trim}aresample=48000,aformat=channel_layouts=stereo,{gain}adelay={delay}:all=1[v{i}]')
    filters.append('[bed]' + ''.join(f'[v{i}]' for i in range(len(voices))) +
                   f'amix=inputs={len(voices)+1}:normalize=0:duration=first,alimiter=limit=0.891:level=false[m]')
    wav = folder / f'{sc}_mix.wav'
    run(cmd + ['-filter_complex', ';'.join(filters), '-map', '[m]', '-c:a', 'pcm_s16le', str(wav)])
    return wav

def render(sc, out, logs, resume, version):
    frames = math.ceil(TIMING[sc]['length'] * 30)
    length = frames / 30
    avi = out / f'{sc}.avi'
    mp4 = out / f'{sc}.mp4'
    if resume and mp4.is_file() and mp4.stat().st_size > 0:
        return
    log = logs / f'{sc}_render.log'
    if not (resume and avi.is_file() and log.is_file() and 'errors=0' in log.read_text(errors='replace')):
        run([GODOT, '--path', str(PROJECT), '--resolution', '1920x1080', '--audio-driver', 'Dummy',
             '--write-movie', str(avi), '--fixed-fps', '30', '--quit-after', str(frames), scene_path(sc),
             '--', '--qa'], logs / f'{sc}_render.log')
    render_log = log.read_text(errors='replace')
    if 'SCRIPT ERROR:' in render_log or 'errors=0' not in render_log:
        raise RuntimeError(f'The Godot render did not pass QA. Check {log}')
    wav = mix(sc, out, length, version)
    video_filter = 'scale=1920:1080:force_original_aspect_ratio=decrease:force_divisible_by=2:flags=lanczos,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1'
    run([FF, '-v', 'error', '-y', '-i', str(avi), '-i', str(wav),
         '-map', '0:v:0', '-map', '1:a:0', '-vf',
         video_filter,
         '-c:v', 'libx264', '-threads', '4', '-preset', 'veryfast', '-crf', '19',
         '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
         '-movflags', '+faststart', '-t', str(length), str(mp4)], logs / f'{sc}_encode.log')
    assert avi.resolve().parent == out and avi.suffix == '.avi'
    avi.unlink()
    print(sc, 'video + audio ready', flush=True)

def remix(sc, out, logs, version):
    source = out / f'{sc}.mp4'
    video = next(s for s in probe(source)['streams'] if s['codec_type'] == 'video')
    length = float(video['duration'])
    audio = mix(sc, out, length, version)
    replacement = out / f'{sc}_remixed.mp4'
    run([FF, '-v', 'error', '-y', '-i', str(source), '-i', str(audio),
         '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac',
         '-b:a', '192k', '-ar', '48000', '-disposition:a:0', 'default',
         '-movflags', '+faststart', '-t', str(length), str(replacement)], logs / f'{sc}_remix.log')
    replacement.replace(source)

def write_stems(out, timeline, duration, version):
    # All three WAVs begin at master zero for direct timeline import.
    folder = out / 'stems'
    folder.mkdir(exist_ok=True)
    tracks = {name: np.zeros(math.ceil(duration * 48000), dtype='<i2')
              for name in ('CAPY', 'ENGINEER', 'SIGNATURE')}
    for segment in timeline:
        sc = segment['scene']
        for v in TIMING[sc]['voices']:
            with wave.open(str(PROJECT / v['file']), 'rb') as f:
                assert (f.getnchannels(), f.getsampwidth(), f.getframerate()) == (1, 2, 48000)
                pcm = np.frombuffer(f.readframes(f.getnframes()), '<i2')
            start = round((segment['start'] + v['t0']) * 48000)
            role = 'CAPY' if v['who'] == 'CAPY' else 'ENGINEER'
            if sc == 'SC01' and v.get('line') == 0 and TIMING[sc]['cues'][0]['text'] == 'Kĩ Sư Ơiiii!':
                tag = TIMING[sc]['cues'][0]
                end_tag = round((tag['t1'] - tag['t0']) * 48000)
                tracks['SIGNATURE'][start:start + end_tag] = pcm[:end_tag]
                pcm = pcm[end_tag:]
                start += end_tag
            tracks[role][start:start + len(pcm)] = pcm
    for name, pcm in tracks.items():
        if version in BUMPER_VERSIONS and name == 'SIGNATURE':
            continue
        with wave.open(str(folder / f'EP02_{version}_{name}.wav'), 'wb') as f:
            f.setparams((1, 2, 48000, 0, 'NONE', 'not compressed'))
            f.writeframes(pcm.tobytes())
    if version in MIX_VERSIONS:
        with wave.open(str(folder / f'EP02_{version}_HIEU_UNG.wav'), 'wb') as f:
            f.setparams((2, 2, 48000, 0, 'NONE', 'not compressed'))
            for segment in timeline:
                with wave.open(str(out / f'{segment["scene"]}_ambience.wav'), 'rb') as source:
                    length = round(segment['duration'] * 48000)
                    data = source.readframes(length)
                    f.writeframes(data.ljust(length * 4, b'\0'))

def styled_captions(path, cues):
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Voice,Segoe UI Semibold,39,&H00F6FAFF,&H000000FF,&H00131C2B,&H000D1420,0,0,0,0,100,100,0,0,1,1.1,0,2,150,150,45,1
Style: Shade,Segoe UI,35,&H35101A2A,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    def timestamp(value):
        stamp = stamps(value).replace(',', '.')[:-1]
        return f'{int(stamp[:2])}{stamp[2:]}'
    events = []
    for start, end, text in cues:
        line_count = text.count('\n') + 1
        text = text.replace('\n', r'\N')
        a, b = timestamp(start), timestamp(end)
        height = 61 if line_count == 1 else 110
        width = min(1120, max(320, 23 * max(len(line) for line in text.split(r'\N')) + 26))
        shade = r'{\an7\pos(' + str(960-width//2) + ',' + str(1049-height) + r')\p1}'
        shade += f'm 13 0 l {width-13} 0 b {width-6} 0 {width} 6 {width} 13 l {width} {height-13} b {width} {height-6} {width-6} {height} {width-13} {height} l 13 {height} b 6 {height} 0 {height-6} 0 {height-13} l 0 13 b 0 6 6 0 13 0'
        events.append(f'Dialogue: 0,{a},{b},Shade,,0,0,0,,{shade}')
        events.append(f'Dialogue: 1,{a},{b},Voice,,0,0,0,,{text}')
    path.write_text(header + '\n'.join(events) + '\n', encoding='utf-8')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=Path, default=ROOT / 'build/EP02_v7_polish')
    p.add_argument('--shots', default=','.join(ORDER))
    p.add_argument('--snapshots', action='store_true')
    p.add_argument('--assemble-only', action='store_true')
    p.add_argument('--remix-only', action='store_true')
    p.add_argument('--parts-only', action='store_true')
    p.add_argument('--resume', action='store_true')
    p.add_argument('--jobs', type=int, default=1)
    p.add_argument('--version', choices=['V7', *MIX_VERSIONS], default='V7')
    p.add_argument('--review', action='store_true', help='encode a copy with styled captions')
    args = p.parse_args()
    out = args.out.resolve(); out.mkdir(parents=True, exist_ok=True)
    shots = args.shots.split(',')
    logs = out / 'logs'; logs.mkdir(exist_ok=True)
    run([GODOT, '--headless', '--path', str(PROJECT), '--editor', '--import', '--quit'], logs / 'import.log')
    if args.remix_only:
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            list(pool.map(lambda sc: remix(sc, out, logs, args.version), shots))
    elif not args.snapshots and not args.assemble_only:
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            list(pool.map(lambda sc: render(sc, out, logs, args.resume, args.version), shots))
    screenshots = []
    summary, cues, offset = [], [], 0.
    timing_rows = []
    for sc in shots:
        frames = math.ceil(TIMING[sc]['length'] * 30)
        length = frames / 30
        if args.snapshots:
            folder = out / 'qa'; folder.mkdir(exist_ok=True)
            start = TIMING[sc]['length'] * 0.52
            dest = folder / f'{sc}.png'
            run([GODOT, '--path', str(PROJECT), '--resolution', '1920x1080', '--audio-driver', 'Dummy',
                 '--write-movie', str(dest), '--fixed-fps', '30', '--quit-after', '2', scene_path(sc), '--', f'--start={start}'], logs / f'{sc}_snapshot.log')
            screenshots.append(folder / f'{sc}00000001.png')
            print(sc, 'snapshot', flush=True)
            continue
        mp4 = out / f'{sc}.mp4'
        data = probe(mp4)
        length = float(data['format']['duration'])
        summary.append({'scene': sc, 'start': offset, 'duration': length, 'voices': len(TIMING[sc]['voices'])})
        for a,b,txt in subtitle_cues(sc, args.version):
            cues.append((offset+a, offset+b, txt))
        subtitle_file(out / f'{sc}.srt', subtitle_cues(sc, args.version))
        for v in TIMING[sc]['voices']:
            timing_rows.append([sc,v['who'],offset+v['t0'],Path(v['file']).name])
        offset += length
        print(sc, 'rendered', round(length, 2), 'total', round(offset, 2), flush=True)
    if args.snapshots:
        contact = Image.new('RGB', (1920, math.ceil(len(screenshots)/3)*390), '#132130')
        draw = ImageDraw.Draw(contact)
        for i, path in enumerate(screenshots):
            im = Image.open(path).convert('RGB'); im.thumbnail((640,360))
            x,y=(i%3)*640,(i//3)*390
            contact.paste(im,(x,y+26)); draw.text((x+12,y+6),shots[i],fill='white')
        contact.save(out / 'V7_contact.jpg')
        return
    if args.parts_only:
        return
    concat = out / 'concat_v7.txt'
    concat.write_text(''.join(f"file '{(out / (sc+'.mp4')).as_posix()}'\n" for sc in shots), encoding='utf-8')
    master = out / f'EP02_FULL_{args.version}_VOICED_DRAFT.mp4'
    run([FF,'-v','error','-y','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(master)])
    subtitle_file(out / f'EP02_FULL_{args.version}_vi.srt', cues)
    if shots == ORDER:
        write_stems(out, summary, offset, args.version)
    if args.version in MIX_VERSIONS:
        captions = out / f'EP02_FULL_{args.version}_vi.ass'
        styled_captions(captions, cues)
        if args.review:
            review = out / f'EP02_FULL_{args.version}_CO_PHU_DE.mp4'
            run([FF, '-v', 'error', '-y', '-i', str(master), '-vf', f'ass={captions.name}',
                 '-map', '0:v:0', '-map', '0:a:0', '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '20',
                 '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-movflags', '+faststart', str(review)],
                logs / 'review_encode.log', cwd=out)
    (out / 'render_manifest.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    with (out / 'audio_timing.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['scene','role','master_start_s','local_voice_file']);w.writerows(timing_rows)
    assert all(b > a for a,b,_ in cues)
    assert all(b <= c+0.004 for (_,b,_),(c,_,_) in zip(cues,cues[1:]))
    print('COMPLETE', master, round(offset,2), flush=True)

if __name__ == '__main__':
    main()
