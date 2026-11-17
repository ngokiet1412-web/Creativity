"""Summarize native Ansys exports; never synthesize missing solver results."""
import csv
import json
import math
from pathlib import Path
import re
import sys


def field(path, unit):
    with path.open(encoding='utf-8-sig') as stream:
        reader = csv.reader(stream, delimiter='\t')
        assert unit in next(reader)[1], 'Unexpected units in ' + path.name
        return {int(row[0]): float(row[1]) for row in reader if row}


def evaluate(directory):
    data = json.loads((directory / 'case.json').read_text())
    log = (directory / 'solve.out').read_text(errors='replace')
    deck = (directory / 'ds.dat').read_text(errors='replace')
    assert data['solution_status'] == 'Done' and (directory / 'file.rst').stat().st_size > 0
    assert re.search(r'0\s+ERROR MESSAGES', log) or re.search(r'NUMBER OF ERROR\s+MESSAGES ENCOUNTERED=\s*0', log)
    assert 'SOLID187' in log and '/units,MKS' in deck
    assert 'MP,EX,1,200000000000' in deck and 'MP,NUXY,1,0.3' in deck
    values = re.findall(r'TOTAL VALUES\s+VALUE ([^\n]+)', log)
    # PRRSOL uses fixed-width columns with no separator before some negatives.
    rx, ry, rz = map(float, re.findall(r'[+-]?\d+\.\d+E[+-]\d+', values[-1]))
    force = data['load_N']
    stress = field(directory / 'von_mises.txt', '(Pa)')
    deform = field(directory / 'total_deformation.txt', '(m)')
    assert len(stress) == len(deform) == data['mesh_nodes']
    probe = data['probe_id']
    xyz = data.pop('probe_xyz_mm')
    with (directory / 'nodes_mm.csv').open() as stream:
        nodes = {int(row['node_id']): row for row in csv.DictReader(stream)}
    peak = nodes[max(stress, key=stress.get)]
    data.update(reaction_x_N=rx, reaction_y_N=ry, reaction_z_N=rz,
                balance_pct=100*math.sqrt((force+rx)**2+ry**2+rz**2)/force,
                probe_x_mm=xyz[0], probe_y_mm=xyz[1], probe_z_mm=xyz[2],
                probe_distance_mm=math.dist(xyz, (42,0,0)), probe_stress_MPa=stress[probe]/1e6,
                peak_stress_MPa=max(stress.values())/1e6, peak_stress_y_mm=float(peak['y_mm']),
                probe_deformation_mm=deform[probe]*1000, peak_deformation_mm=max(deform.values())*1000)
    assert data['balance_pct'] < 0.2 and data['probe_distance_mm'] < 4
    return data


def percent_difference(new, old, field):
    return 100 * (new[field]/old[field] - 1)


def main(path):
    cases = [evaluate(path / name) for name in ('coarse', 'medium', 'fine', 'sensitivity')]
    assert cases[0]['mesh_elements'] < cases[1]['mesh_elements'] < cases[2]['mesh_elements']
    with (path / 'mesh_convergence.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(cases[0]))
        writer.writeheader()
        writer.writerows(cases)
    fields = ('probe_stress_MPa', 'peak_stress_MPa', 'probe_deformation_mm', 'peak_deformation_mm')
    change = {f: percent_difference(cases[2], cases[1], f) for f in fields}
    sensitivity = {f: percent_difference(cases[3], cases[2], f) for f in fields}
    status = 'PASS' if max(abs(change[f]) for f in ('probe_stress_MPa','peak_deformation_mm')) < 5 else 'FAIL'
    summary = dict(status=status, criterion='Medium-to-fine probe stress and peak displacement change each <5%; reaction imbalance <0.2%. Edge peak reported separately.',
                   fine_vs_medium_percent=change, sensitivity_vs_fine_percent=sensitivity,
                   maximum_reaction_imbalance_pct=max(r['balance_pct'] for r in cases))
    (path/'mesh_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__ == '__main__':
    main(Path(sys.argv[1]))
