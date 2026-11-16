"""Argon V2 fit correction, preserving pin axes and published cylinder dimensions."""

import csv
import os
import sys
from pathlib import Path

# Keep Argon's supplied journals beside this file, or set CAPY_ARGON_SOURCE.
source = Path(os.environ.get("CAPY_ARGON_SOURCE", str(Path(__file__).resolve().parent)))
sys.path.insert(0, str(source))
import nx_pilot_v2_argon as v2


g = v2.g
NXOpen = v2.NXOpen
BASE_TONGUE = 40.0
BASE_FORK_IN = 48.0
ROD_HALF = 38.0
LIFT_FORK_IN = 46.0
LIFT_FORK_OUT = 72.0
SIDE_LINK_IN = 158.0
SIDE_LINK_OUT = 192.0
H_LINK_IN = 46.0
H_LINK_OUT = 83.0
BOOM_TIP_COLLAR_IN = 160.0
BUCKET_EAR_COLLAR_IN = 158.0
RELOCATED_PINS = {"arm_cyl_A": (3565.7, 1191.4), "bucket_cyl_A": (500.0, 595.0)}
TORQUE_TUBE = (320.0, -285.0)


class FilteredModel:
    """Retain named NX features from the supplied journal except replaced detail."""
    def __init__(self, model, reject):
        self.model = model
        self.reject = reject

    def __getattr__(self, name):
        return getattr(self.model, name)

    def sketch(self, loops, start, end, name, **options):
        if not name.startswith(self.reject):
            if name in ("Stick_L_tapered_web_with_mounting_bores", "Stick_R_tapered_web_with_mounting_bores"):
                loops = [loop for loop in loops if loop != v2.circle(500., 400., 40.)]
            return self.model.sketch(loops, start, end, name, **options)

    def add_joint_axis(self, name, x, z, y1, y2):
        x, z = RELOCATED_PINS.get(name.lower(), (x, z))
        return self.model.add_joint_axis(name, x, z, y1, y2)


def band(sign, lo, hi, center=0.0):
    a, b = center+sign*lo, center+sign*hi
    return min(a,b), max(a,b)


def annulus(model, name, center, radius, bore, y0, y1):
    model.sketch([v2.circle(*center,radius),v2.circle(*center,bore)],y0,y1,name,color=31)


def upper_clevis_tongue(model, name, center, bore):
    x, z = center
    radius = bore + 32.0
    profile = [("arc", (x - radius, z), (x, z + radius)), (x + radius, z),
               (x + 36., z - 110.), (x + 33., z - 198.),
               (x - 73., z - 198.), (x - 63., z - 98.)]
    model.sketch([profile, v2.circle(x, z, bore)], -BASE_TONGUE, BASE_TONGUE, name, color=36)


def boom(model, native):
    original_boom(FilteredModel(model, ("Boom_twin_lift_mounting_saddle_", "Boom_lift_pin_boss_",
                                       "Boom_stick_barrel_lug_", "Boom_tip_boss_collar_",
                                       "Boom_shaped_top_cover", "Boom_shaped_bottom_cover")),native)
    roof = [(245., 261.), (820., 485.), (1660., 890.), (2480., 1080.), (3520., 1050.),
            (4780., 570.), (5230., 382.), (5230., 346.), (4754., 540.), (3507., 1018.),
            (2491., 1045.), (1678., 857.), (839., 455.), (252., 225.)]
    model.sketch([roof], -180., 180., "Boom_tip_swing_clearance_top_cover", color=32)
    cover = [(265., -264.), (1125., 130.), (2010., 540.), (3180., 640.),
             (4750., 270.), (5230., 88.), (5230., 123.), (4765., 305.),
             (3190., 674.), (2018., 574.), (1140., 162.), (278., -234.)]
    model.sketch([cover], -180., 180., "Boom_tip_swing_clearance_bottom_cover", color=36)
    for sign, tag in ((-1,"R"),(1,"L")):
        annulus(model,"Boom_tip_setback_collar_"+tag,(g.BOOM_LENGTH,0.),84.,60.,
                *band(sign,BOOM_TIP_COLLAR_IN,240.))
        y = sign*g.BOOM_HALF_Y
        center = g.JOINTS["boom_cyl_B"][2]
        x,z = center
        # Tapered transverse saddle stops above the rotating eye and exposed rod.
        web = [(x-100.,z+156.),(x+94.,z+156.),(x+132.,z+437.),
               (x+54.,z+480.),(x-131.,z+461.)]
        model.sketch([web],*band(sign,180.,g.BOOM_HALF_Y+LIFT_FORK_OUT),
                     "Boom_lift_tapered_bridge_"+tag,color=36)
        cheek = [(x-104.,z),(x-91.,z-47.),(x-55.,z-80.),(x+47.,z-81.),
                 (x+89.,z-46.),(x+101.,z),(x+81.,z+178.),(x-77.,z+178.)]
        for side,label in ((-1,"minus"),(1,"plus")):
            model.sketch([cheek,v2.circle(x,z,42.)],*band(side,LIFT_FORK_IN,LIFT_FORK_OUT,y),
                         "Boom_lift_fork_"+tag+"_"+label,color=36)
    upper_clevis_tongue(model, "Boom_arm_ram_center_tongue", RELOCATED_PINS["arm_cyl_A"], 44.)


def stick(model, native):
    original_stick(FilteredModel(model, ("Stick_bucket_cylinder_lug_",)),native)
    upper_clevis_tongue(model, "Stick_bucket_ram_center_tongue", RELOCATED_PINS["bucket_cyl_A"], 40.)


def bucket(model,native):
    original_bucket(FilteredModel(model,("Bucket_hinge_boss_collar_", "Bucket_link_boss_collar_",
                                         "Bucket_rear_torque_tube")),native)
    annulus(model, "Bucket_torque_tube_clear_of_H_link", TORQUE_TUBE, 62., 42., -535., 535.)
    for sign, tag in ((-1,"R"),(1,"L")):
        annulus(model,"Bucket_hinge_setback_collar_"+tag,(0.,0.),76.,54.,
                *band(sign,BUCKET_EAR_COLLAR_IN,236.))
        annulus(model,"Bucket_link_setback_collar_"+tag,g.JOINTS["bucket_boss"][2],58.,38.,
                *band(sign,BUCKET_EAR_COLLAR_IN,236.))


def cylinder(model,name,rod,native):
    if not rod:
        original_cylinder(model,name,False,native)
        return
    original_cylinder(FilteredModel(model,("Rod_end_bored_eye_","Rod_eye_grease_boss_")),name,True,native)
    eye = g.ACTUATORS[name]["eye"]
    profile,hole = v2.lug((0.,0.),eye+33.,eye)
    model.sketch([profile,hole],-ROD_HALF,ROD_HALF,"Rod_eye_centered_clearance",color=31)


def linkage(model, side, native=False):
    span = g.LINK_SIDE if side else g.LINK_H
    label = "Side_link_outer_strap" if side else "H_link_inner_strap"
    low,high = (SIDE_LINK_IN,SIDE_LINK_OUT) if side else (H_LINK_IN,H_LINK_OUT)
    for sign,tag in ((-1,"R"),(1,"L")):
        start,end = band(sign,low,high)
        strap = v2.flat_strap(span,66.,66.)
        model.sketch([strap,v2.circle(0.,0.,38.),v2.circle(span,0.,38.)],
                     start,end,label+"_"+tag,color=36)
    if not side:
        annulus(model, "H_link_cross_tube", (span * 0.42, 0.), 38., 25., -H_LINK_IN, H_LINK_IN)
    if native:
        model.add_joint_axis("LINK_A",0.,0.,-high,high)
        model.add_joint_axis("LINK_B",span,0.,-high,high)


def root_frame(model,native=False):
    original_root(FilteredModel(model,("Carrier_datum_lift_clevis_support_",)),native)
    x,z = g.JOINTS["boom_cyl_A"][2]
    for sign,tag in ((-1,"R"),(1,"L")):
        y=sign*g.BOOM_HALF_Y
        profile,hole = v2.lug((x,z),94.,42.,179.)
        model.sketch([profile,hole],y-BASE_TONGUE,y+BASE_TONGUE,"Carrier_lift_center_tongue_"+tag,color=31)
        gusset = [(120.,-875.),(240.,-875.),(318.,-895.),(336.,-871.),
                  (311.,-836.),(175.,-810.)]
        model.sketch([gusset],*band(sign,300.,g.BOOM_HALF_Y+BASE_TONGUE),
                     "Carrier_tapered_lift_gusset_"+tag,color=31)


def clean_fit(part):
    # Keep reference geometry and relationships, hide their visual overlays.
    for obj in list(part.Points)+list(part.Datums):
        if obj.Name.upper().startswith(("AXIS_","J_")):
            obj.Blank()
    original_fit(part)


def assumptions(out):
    rows = [
        ("Barrel base fork inner half-width",BASE_FORK_IN),
        ("Structural center tongue half-width",BASE_TONGUE),
        ("Clearance on each side at barrel base",BASE_FORK_IN-BASE_TONGUE),
        ("Rod eye half-width",ROD_HALF),
        ("Boom rod bracket inner half-width",LIFT_FORK_IN),
        ("Clearance on each side at boom rod eye",LIFT_FORK_IN-ROD_HALF),
        ("Clearance on each side at knee rod eye",H_LINK_IN-ROD_HALF),
        ("Four-bar strap gap",SIDE_LINK_IN-H_LINK_OUT),
        ("Boom tip collar setback from stick sleeve",BOOM_TIP_COLLAR_IN-152.),
        ("Bucket hinge collar setback from stick sleeve",BUCKET_EAR_COLLAR_IN-152.),
        ("Arm cylinder base pin Z in boom frame", RELOCATED_PINS["arm_cyl_A"][1]),
        ("Bucket cylinder base pin Z in stick frame", RELOCATED_PINS["bucket_cyl_A"][1]),
        ("Bucket torque tube X in bucket frame", TORQUE_TUBE[0]),
        ("Bucket torque tube Z in bucket frame", TORQUE_TUBE[1]),
    ]
    with (out/"fit_assumptions.csv").open("w",encoding="utf-8",newline="") as f:
        writer=csv.writer(f)
        writer.writerow(("parameter","mm","confidence"))
        writer.writerows((name,value,"ASSUMED-PARAM") for name,value in rows)


original_boom, original_stick, original_bucket = v2.boom,v2.stick,v2.bucket
original_cylinder, original_root, original_fit = v2.cylinder,v2.root_frame,v2.fit


def main():
    out=Path(os.environ["CAPY_FIT_OUT"]).resolve()
    if out.exists():
        raise FileExistsError("Choose a new CAPY_FIT_OUT directory.")
    out.mkdir(parents=True)
    for name, center in RELOCATED_PINS.items():
        g.JOINTS[name] = g.JOINTS[name][:2] + (center,)
    g.PIN_SPECS = [(pid,key,y,
                    202. if key in ("bucket_side","bucket_cyl_B") else half,
                    radius,parent,child,note)
                   for pid,key,y,half,radius,parent,child,note in g.PIN_SPECS]
    v2.boom,v2.stick,v2.bucket = boom,stick,bucket
    v2.cylinder,v2.linkage,v2.root_frame,v2.fit = cylinder,linkage,root_frame,clean_fit
    g.write_tables(out)
    assumptions(out)
    session=NXOpen.Session.GetSession()
    with (out/"nx_fit_run.log").open("w",encoding="utf-8") as handle:
        def log(msg):
            print(msg)
            handle.write(msg+"\n")
            handle.flush()
        models=v2.build_native_parts(session,out,log)
        for name,angles in g.POSES.items():
            v2.build_component_assembly(session,out,name,angles,models,log)
            stem="PC2008_"+name.upper()+"_PLACED_SOLIDS"
            pose=v2.new_part(session,out,stem)
            v2.pose_geometry(v2.Model(pose),angles)
            clean_fit(pose)
            v2.save(pose)
            if name=="reach":
                solids=v2.step_export(session,pose,out/"PC2008_REACH_AP214.step")
                log("STEP_REACH solids={}".format(solids))
        log("NX_FIT_V3_DONE")


if __name__=="__main__":
    main()
