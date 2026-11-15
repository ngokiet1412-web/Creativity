"""Opt-in neural voice audition, after owner requested a no-credit alternative.

No cloning and no changes to the approved ElevenLabs sources. Keep generated
stems local. Sentence audio is the timing authority; never time-stretch speech.
"""
import asyncio
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import wave

import edge_tts

DEMO = Path(__file__).resolve().parents[2]
ROOT = DEMO.parents[2]
OUT = DEMO / 'godot/local/voice'
RAW = OUT / 'cache_v7'
FF = os.environ.get('FFMPEG', 'ffmpeg')
PRON = {'PC200-8': 'pê xê hai trăm gạch tám', 'SAA6D107E-1': 'ét a a, sáu đê một không bảy e, gạch một',
        'CLSS': 'xê eo ét ét', 'HydrauMind': 'Hai đrô mai', 'LS/PC': 'eo ét, pê xê',
        'EPC': 'e pê xê', 'ECU': 'e xê u', 'LS': 'eo ét', 'PC': 'pê xê',
        'pilot': 'pai lợt', 'joystick': 'cần điều khiển', 'diesel': 'đi ê zen',
        'F': 'ép', 'Q': 'quy', 'A': 'a', 'p': 'pê'}

def spoken(text):
    for a, b in PRON.items():
        text = re.sub(r'(?<![\w-])' + re.escape(a) + r'(?![\w-])', b, text)
    return text.replace(' — ', ', ').replace(';', '.').replace(':', ',')

def parts(text):
    return [s.strip() for s in re.split(r'(?<=[.!?;])\s+', text) if s.strip()]

def run(cmd):
    subprocess.run(cmd, check=True, capture_output=True)

def readwav(path):
    with wave.open(str(path), 'rb') as w:
        assert w.getframerate() == 48000 and w.getnchannels() == 1
        return w.readframes(w.getnframes())

def writewav(path, data):
    with wave.open(str(path), 'wb') as w:
        w.setparams((1, 2, 48000, 0, 'NONE', 'not compressed'))
        w.writeframes(data)

async def generate(row):
    name, role = row['file_name'], row['speaker']
    dst = OUT / name
    if dst.exists() and dst.with_suffix('.json').exists():
        return
    text = row['text']
    pieces = parts(text)
    data, cues, offset = b'', [], 0.0
    for i, original in enumerate(pieces):
        if row['scene'] == 'SC01' and i == 0 and 'sưuuu' in original:
            signature = Path(os.environ.get('CAPY_SIGNATURE', ROOT.parent / 'Capy_Ki_Su_Oiii_v2_Nhe_Tu_Nhien.mp3'))
            wav = RAW / 'signature.wav'
            run([FF, '-v', 'error', '-y', '-ss', '1.276', '-t', '2.81', '-i', str(signature),
                 '-ac', '1', '-ar', '48000', '-af', 'afade=t=in:d=0.02,afade=t=out:st=2.73:d=0.08', str(wav)])
            original = 'Kĩ Sư Ơiiii!'
        else:
            phrase = spoken(original)
            pitch = '+3Hz' if role == 'CAPY' else '+0Hz'
            rate = '+0%' if role == 'CAPY' else '-3%'
            digest = hashlib.sha256((phrase + pitch + rate).encode()).hexdigest()[:20]
            mp3 = RAW / (digest + '.mp3')
            wav = RAW / (digest + '.wav')
            if not wav.exists():
                for attempt in range(3):
                    try:
                        tts = edge_tts.Communicate(phrase, 'vi-VN-NamMinhNeural', rate=rate, pitch=pitch)
                        await asyncio.wait_for(tts.save(str(mp3)), timeout=35)
                        break
                    except Exception as exc:
                        print(name, 'retry', attempt + 1, type(exc).__name__, flush=True)
                        if attempt == 2:
                            raise
                        await asyncio.sleep(2 + attempt)
                run([FF, '-v', 'error', '-y', '-i', str(mp3), '-ac', '1', '-ar', '48000',
                     '-af', 'highpass=f=65,loudnorm=I=-18:TP=-2:LRA=10', str(wav)])
        samples = readwav(wav)
        duration = len(samples) / 96000
        cues.append({'text': original, 't0': round(offset, 4), 't1': round(offset + duration, 4)})
        data += samples
        offset += duration
        if i < len(pieces) - 1:
            pause = 0.22 if original.endswith('?') else 0.12
            data += b'\0' * (int(pause * 48000) * 2)
            offset += pause
    writewav(dst, data)
    dst.with_suffix('.json').write_text(json.dumps({'voice': 'vi-VN-NamMinhNeural',
        'status': 'AUDITION, NOT OWNER-APPROVED CAST', 'role': role,
        'source_text': text, 'duration': offset, 'cues': cues}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(name, round(offset, 2), flush=True)

async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(exist_ok=True)
    rows = list(csv.DictReader((DEMO / 'full_v5/VOICE_SHEET.csv').open(encoding='utf-8')))
    # Two concurrent requests, cached and resumable. Never spend ElevenLabs credits.
    sem = asyncio.Semaphore(2)
    async def job(row):
        async with sem:
            await generate(row)
    await asyncio.gather(*(job(row) for row in rows))

if __name__ == '__main__':
    asyncio.run(main())
