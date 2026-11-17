"""Geometry adapter for Blender in a future integration. Input lengths in mm."""
import json
import math
from pathlib import Path


def chamber_geometry(model, actuator, pin_distance_mm):
    """Return axial intervals measured from the barrel base eye, in metres."""
    dimensions = model['act'][actuator]
    fluid = model['fluid']
    closed = dimensions['closed']
    head = fluid['head_inner_mm']
    piston_cap = pin_distance_mm - (closed - fluid['piston_cap_from_rod_eye_from_closed_mm'])
    piston_rod = pin_distance_mm - (closed - fluid['piston_rod_from_rod_eye_from_closed_mm'])
    gland = closed - fluid['gland_inner_from_closed_mm']
    if not head < piston_cap < piston_rod < gland:
        raise ValueError('Nonpositive fluid chamber or piston extent')
    return {
        'cap_x_m': (head / 1000, piston_cap / 1000),
        'rod_x_m': (piston_rod / 1000, gland / 1000),
        'bore_radius_m': dimensions['bore'] / 2000,
        'rod_radius_m': dimensions['rod'] / 2000,
        'quantity': dimensions['qty'],
    }


def compare_matlab(path):
    import csv
    model = json.loads((path / 'shared_model.json').read_text())
    differences = []
    with (path / 'motion_540_frames.csv').open() as stream:
        for row in csv.DictReader(stream):
            for actuator in model['act']:
                g = chamber_geometry(model, actuator, float(row[actuator+'_length_mm']))
                for chamber in ('cap', 'rod'):
                    start, end = g[chamber+'_x_m']
                    area_m2 = math.pi * g['bore_radius_m']**2
                    if chamber == 'rod':
                        area_m2 -= math.pi * g['rod_radius_m']**2
                    differences.append(abs((end-start)*area_m2*1000 - float(row[actuator+'_'+chamber+'_volume_L'])))
    assert len(differences) == 540 * 3 * 2 and max(differences) < 1e-9
    print('CHAMBER_PASS {} volumes, max difference {:.3g} L'.format(len(differences), max(differences)))


if __name__ == '__main__':
    import sys
    compare_matlab(Path(sys.argv[1]))
