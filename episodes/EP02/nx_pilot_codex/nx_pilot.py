"""NX 12 interactive journal: native PC200-8-style work equipment concept."""

import math
import os
import re
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import geometry as g

import NXOpen
import NXOpen.Features
import NXOpen.GeometricUtilities


def length_text(value):
    return "{:.9f}".format(value) if isinstance(value, (int, float)) else value


def point(values):
    return NXOpen.Point3d(*map(float, values))


def vector(values):
    return NXOpen.Vector3d(*map(float, values))


class Placement:
    def __init__(self, xz=(0., 0.), y=0., angle=0.):
        self.xz, self.y, self.angle = xz, y, angle

    def xyz(self, x, y, z):
        x, z = g.add(self.xz, g.rotate((x,z),self.angle))
        return (x,self.y+y,z)

    def direction(self, x,y,z):
        x,z = g.rotate((x,z),self.angle)
        return vector((x,y,z))


class Model:
    def __init__(self, part, frame=None):
        self.part = part
        self.frame = frame or Placement()
        self.features = []

    def sketch(self, loops, start, end, name, axis="Y", color=6):
        """Native extrude with exact arcs and optional nested circular loops."""
        part = self.part
        if axis == "Y":
            def from_uv(u,v):
                return point(self.frame.xyz(u,0.,v))
            udir, vdir = self.frame.direction(1,0,0), self.frame.direction(0,0,1)
            pull = self.frame.direction(0,1,0)
        else:
            def from_uv(u,v):
                return point(self.frame.xyz(0.,u,v))
            udir, vdir = self.frame.direction(0,1,0), self.frame.direction(0,0,1)
            pull = self.frame.direction(1,0,0)

        section = part.Sections.CreateSection(0.01,0.02,0.5)
        curves = []
        for loop in loops:
            guide = None
            if isinstance(loop, tuple) and len(loop) == 3 and loop[0] == "circle":
                _,center,radius = loop
                guide = from_uv(center[0]+radius,center[1])
                items = [part.Curves.CreateArc(from_uv(*center),udir,vdir,float(radius),0.0,2*math.pi)]
            else:
                items = []
                for i,start_uv in enumerate(loop):
                    end_uv = loop[(i+1) % len(loop)]
                    if len(start_uv)==3 and start_uv[0]=="arc":
                        curve = part.Curves.CreateArc(from_uv(*start_uv[1]),from_uv(*start_uv[2]),
                                                    from_uv(*end_uv),False)
                        items.append(curve[0] if isinstance(curve,tuple) else curve)
                        guide = guide or from_uv(*start_uv[1])
                    else:
                        dest = end_uv[1] if len(end_uv)==3 and end_uv[0]=="arc" else end_uv
                        items.append(part.Curves.CreateLine(from_uv(*start_uv),from_uv(*dest)))
                        guide = guide or from_uv(*start_uv)
            rule = part.ScRuleFactory.CreateRuleCurveDumb(items)
            section.AddToSection([rule],items[0],NXOpen.NXObject.Null,NXOpen.NXObject.Null,
                                 guide,NXOpen.Section.Mode.Create,False)
            curves.extend(items)

        builder = part.Features.CreateExtrudeBuilder(NXOpen.Features.Feature.Null)
        try:
            builder.Section = section
            builder.Direction = part.Directions.CreateDirection(
                point(self.frame.xyz(0.,0.,0.)),pull,NXOpen.SmartObject.UpdateOption.WithinModeling)
            builder.Limits.StartExtend.Value.RightHandSide = length_text(start)
            builder.Limits.EndExtend.Value.RightHandSide = length_text(end)
            feature = builder.CommitFeature()
        finally:
            builder.Destroy()
        feature.SetName(re.sub(r"[^A-Za-z0-9_]+","_",name).strip("_"))
        for body in feature.GetBodies():
            body.Color = color
        for curve in curves:
            curve.Blank()
        self.features.append(feature)


def circle(x,z,radius):
    return ("circle",(x,z),radius)


def lug(center,radius,bore,angle=0.):
    """Round bored eye with a flared weld pad rather than a disk-only connection."""
    # The circular cap blends into a short stock with a flared shoulder.
    pts = [(0.,-radius),(-radius,0.),(0.,radius),
           (radius*1.43,radius*0.74),(radius*1.78,radius*0.40),
           (radius*1.78,-radius*0.40),(radius*1.43,-radius*0.74)]
    pts = [g.add(center,g.rotate(p,angle)) for p in pts]
    return (("arc",pts[0],pts[1]),)+tuple(pts[2:]), circle(center[0],center[1],bore)


def flat_strap(distance,width,end_radius):
    return (("arc",(0.,-width),(-end_radius,0.)),(0.,width),
            ("arc",(distance,width),(distance+end_radius,0.)),(distance,-width))


def boom(m, native):
    # Tapered depth and kinked backbone. The web and flange plates remain named
    # native features, reflecting a welded steel box made from separate plates.
    web = g.BOOM_PROFILE
    holes = [circle(0.,0.,64.),circle(g.BOOM_LENGTH,0.,60.)]
    for side, start,end in (("L","BOOM_WEB_IN","BOOM_WEB_OUT"),("R","-BOOM_WEB_OUT","-BOOM_WEB_IN")):
        if not native:
            start,end = (180.,209.) if side=="L" else (-209.,-180.)
        m.sketch([web]+holes,start,end,"Boom "+side+" | tapered web and hinge bores",color=36)
    top=[(245.,261.),(820.,485.),(1660.,890.),(2480.,1080.),(3520.,1050.),
         (4780.,570.),(5480.,278.),(5471.,242.),(4754.,540.),(3507.,1018.),
         (2491.,1045.),(1678.,857.),(839.,455.),(252.,225.)]
    bottom=[(265.,-264.),(1125.,130.),(2010.,540.),(3180.,640.),(4750.,270.),
            (5515.,-21.),(5516.,17.),(4765.,305.),(3190.,674.),(2018.,574.),
            (1140.,162.),(278.,-234.)]
    m.sketch([top],-180.,180.,"Boom | shaped top cover",color=32)
    m.sketch([bottom],-180.,180.,"Boom | shaped bottom cover",color=36)
    for x,z,label,bore,width in ((2600.,220.,"lift rod lug",42.,g.BOOM_HALF_Y),
                                 (3565.7,961.4,"stick barrel lug",44.,92.)):
        # Two outer lift ears share the same X/Z anchors and sit at +/- Y.
        if label.startswith("lift"):
            for sign in (-1,1):
                y=sign*width
                m.sketch([[(x-150.,z-66.),(x-118.,z-135.),(x+108.,z-135.),
                          (x+159.,z-58.),(x+148.,z+445.),(x-133.,z+445.)],
                          circle(x,z,bore)],min(sign*180.,y),max(sign*180.,y),
                         "Boom | twin lift mounting saddle "+str(sign),color=36)
        else:
            for y in (-width,width):
                profile,hole=lug((x,z),111.,bore,-69.)
                m.sketch([profile,hole],y-23.,y+23.,"Boom | "+label,color=36)


def stick(m,native):
    holes=[circle(0.,0.,60.),circle(g.STICK_LENGTH,0.,54.),circle(-600.,0.,44.),
           circle(500.,400.,40.),circle(2700.,150.,38.)]
    for side,start,end in (("L",126.,152.),("R",-152.,-126.)):
        if native:
            start,end=("STICK_WEB_IN","STICK_WEB_OUT") if side=="L" else ("-STICK_WEB_OUT","-STICK_WEB_IN")
        m.sketch([g.STICK_PROFILE]+holes,start,end,"Stick "+side+" | tapered web with mounting bores",color=36)
    top=[(90.,292.),(420.,461.),(575.,476.),(1570.,268.),(2340.,220.),
         (2550.,208.),(2550.,175.),(2340.,189.),(1567.,237.),(569.,445.),
         (433.,430.),(99.,262.)]
    bottom=[(109.,-227.),(650.,-234.),(1630.,-210.),(2510.,-128.),
            (2510.,-98.),(1627.,-180.),(650.,-204.),(110.,-197.)]
    m.sketch([top],-126.,126.,"Stick | top cover",color=32)
    m.sketch([bottom],-126.,126.,"Stick | lower cover",color=36)
    for y in (-126.,126.):
        profile,hole=lug((2700.,150.),69.,38.,-32.)
        m.sketch([profile,hole],y-22.,y+22.,"Stick | four-bar anchor cheek",color=36)


def bucket(m,native):
    outer = ("arc",g.BUCKET_ARC[0],g.BUCKET_ARC[1])
    inner = ("arc",g.BUCKET_ARC_INNER[0],g.BUCKET_ARC_INNER[1])
    shell=(outer,g.BUCKET_ARC[2],inner,g.BUCKET_ARC_INNER[2])
    m.sketch([shell],"-BUCKET_IN_HALF" if native else -535.,
             "BUCKET_IN_HALF" if native else 535.,"Bucket | curved rolled floor with wall thickness",color=31)
    cheek=(outer,g.BUCKET_ARC[2],(557.,-310.),(478.,-190.),(116.,-35.),
           (-202.,-410.),(-954.,-628.))
    for side in (-1,1):
        m.sketch([cheek],min(side*535.,side*563.),max(side*535.,side*563.),
                 "Bucket | side plate "+str(side),color=31)
    for y in (-190.,190.):
        profile=((-91.,-43.),(-61.,92.),(39.,118.),(235.,45.),(300.,-116.),
                 (316.,-270.),(243.,-320.),(57.,-263.),(-88.,-183.))
        m.sketch([profile,circle(0.,0.,54.),circle(188.6,-207.5,38.)],y-35.,y+35.,
                 "Bucket | double-bore hinge and linkage ear",color=36)
    edge=[(-1172.,-688.),(-1100.,-716.),(-1141.,-775.),(-1249.,-778.),(-1254.,-733.)]
    m.sketch([edge],-558.,558.,"Bucket | cutting edge",color=30)
    tooth=[(-1105.,-718.),(-1186.,-715.),(-1322.,-723.),(-1398.,-765.),
           (-1397.,-794.),(-1310.,-799.),(-1174.,-777.),(-1105.,-769.)]
    for idx,y in enumerate((-420.,-210.,0.,210.,420.),1):
        m.sketch([tooth],y-64.,y+64.,"Bucket | replaceable tooth "+str(idx),color=30)


def cylinder(m, name, rod, native):
    spec=g.ACTUATORS[name]
    radius, eye = spec["bore"]/2, spec["eye"]
    if rod:
        span = spec["closed"]-200.
        m.sketch([circle(0.,0.,spec["rod"]/2)],104.,
                 "ROD_SPAN" if native else span,"Chrome | rigid piston rod",axis="X",color=186)
        m.sketch([circle(0.,0.,radius-2.)],span-41.,span,"Piston land",axis="X",color=186)
        profile,hole=lug((0.,0.),eye+33.,eye)
        m.sketch([profile,hole],-40.,40.,"Rod end | bored eye and shoulder",color=31)
    else:
        gland=spec["closed"]-120.
        m.sketch([circle(0.,0.,radius+19.),circle(0.,0.,radius)],140.,
                 "GLAND_STATION" if native else gland,"Barrel | annular tube with brochure bore",axis="X",color=31)
        m.sketch([circle(0.,0.,radius+23.),circle(0.,0.,spec["rod"]/2+1.4)],
                 gland-42.,gland+12.,"Gland collar and rod guide",axis="X",color=186)
        m.sketch([circle(0.,0.,radius+25.)],113.,172.,"Barrel | closed head",axis="X",color=31)
        profile,hole=lug((0.,0.),eye+40.,eye)
        for y in (-66.,66.):
            m.sketch([profile,hole],y-18.,y+18.,"Barrel | clevis eye",color=36)


def linkage(m, side):
    span = g.LINK_SIDE if side else g.LINK_H
    width = 72. if side else 78.
    for y in (-65.,65.):
        m.sketch([flat_strap(span,width,width),circle(0.,0.,38.),circle(span,0.,38.)],
                 y-18.,y+18.,"Link | bored strap",color=36)
    m.sketch([circle(span*0.51,0.,51.)],-47.,47.,"Link | cross stiffener",color=31)


def pin(m):
    m.sketch([circle(0.,0.,38.)],-132.,132.,"Pin | shank",color=186)
    for y in (-132.,132.):
        m.sketch([circle(0.,0.,57.)],y-8.,y+8.,"Pin | retainer flange",color=31)


def root_frame(m):
    for y in (-300.,300.):
        profile,hole=lug((0.,0.),141.,64.,-133.)
        m.sketch([profile,hole],y-37.,y+37.,"Carrier datum | boom foot ear",color=31)
    for y in (-g.BOOM_HALF_Y,g.BOOM_HALF_Y):
        profile,hole=lug((450.,-850.),97.,42.,157.)
        m.sketch([profile,hole],y-45.,y+45.,"Carrier datum | lift clevis support",color=31)


def parameters(part, values):
    for name,value in values.items():
        part.Expressions.CreateExpression("Number",name+"="+length_text(value))


def new_part(session, directory, name, values=None):
    part=session.Parts.NewBaseDisplay(str(directory/(name+".prt")),NXOpen.BasePart.Units.Millimeters)
    part.SetUserAttribute("PROVENANCE",-1,"ASSUMED-PARAM | PC200-8 concept | not OEM design",NXOpen.Update.Option.Now)
    if values:
        parameters(part,values)
    return part


def save(part):
    status=part.Save(NXOpen.BasePart.SaveComponents.FalseValue,NXOpen.BasePart.CloseAfterSave.FalseValue)
    status.Dispose()


def fit(part):
    view=part.ModelingViews.WorkView
    view.Orient(NXOpen.View.Canned.Isometric,NXOpen.View.ScaleAdjustment.Fit)
    view.RenderingStyle=NXOpen.View.RenderingStyleType.ShadedWithEdges


def screenshot(part,path,orientation="ISO"):
    import NXOpen.UF
    view=part.ModelingViews.WorkView
    view.Orient(orientation,NXOpen.View.ScaleAdjustment.Fit)
    uf=NXOpen.UF.UFSession.GetUFSession()
    uf.Disp.CreateImage(str(path),NXOpen.UF.UFDisp.ImageFormat.Png,NXOpen.UF.UFDisp.BackgroundColor.White)
    if not path.is_file() or path.stat().st_size<200:
        raise RuntimeError("NX viewport export did not write an image")


def step_export(session,part,target):
    builder=session.DexManager.CreateStep214Creator()
    try:
        settings=Path(os.environ["UGII_BASE_DIR"])/"STEP214UG"/"ugstep214.def"
        builder.SettingsFile=str(settings)
        builder.InputFile=part.FullPath
        builder.OutputFile=str(target)
        builder.FileSaveFlag=False
        builder.ExportFrom=NXOpen.Step214Creator.ExportFromOption.ExistingPart
        builder.ExportSelectionBlock.SelectionScope=NXOpen.ObjectSelector.Scope.EntirePart
        builder.LayerMask="1-256"
        builder.ObjectTypes.Solids=True
        builder.Commit()
    finally:
        builder.Destroy()
    deadline=time.monotonic()+18
    while time.monotonic()<deadline:
        if target.is_file():
            data=target.read_bytes()
            if b"END-ISO-10303-21;" in data:
                solids=data.count(b"MANIFOLD_SOLID_BREP(")
                if solids!=sum(1 for body in part.Bodies if body.IsSolidBody):
                    raise RuntimeError("NX STEP body count differs: {}".format(solids))
                if not re.search(rb"SI_UNIT\s*\(\s*\.MILLI\.\s*,\s*\.METRE\.\s*\)",data):
                    raise RuntimeError("NX STEP does not declare mm")
                return
        time.sleep(0.2)
    raise RuntimeError("NX STEP translator did not produce a complete file")


def native_parts(session,directory,log):
    items = [
        ("boom",boom,dict(BOOM_WEB_IN=180.,BOOM_WEB_OUT=209.,PILOT_PIN_SPACING=g.BOOM_LENGTH)),
        ("stick",stick,dict(STICK_WEB_IN=126.,STICK_WEB_OUT=152.,PILOT_PIN_SPACING=g.STICK_LENGTH)),
        ("bucket",bucket,dict(BUCKET_IN_HALF=535.)),
        ("side_link",lambda m,_:linkage(m,True),{}),
        ("h_link",lambda m,_:linkage(m,False),{}),
        ("pivot_pin",lambda m,_:pin(m),{}),
        ("carrier_mount_reference",lambda m,_:root_frame(m),{}),
    ]
    for name,spec in g.ACTUATORS.items():
        for rod in (False,True):
            fname=name + ("_rod" if rod else "_cylinder_barrel")
            items.append((fname,lambda m,n,name=name,rod=rod:cylinder(m,name,rod,n),
                          dict(ROD_SPAN=spec["closed"]-200.,GLAND_STATION=spec["closed"]-120.,
                               BROCHURE_BORE=spec["bore"],BROCHURE_STROKE=spec["stroke"],
                               BROCHURE_ROD=spec["rod"],ASSUMED_CLOSED=spec["closed"])))
    for name,make,values in items:
        part=new_part(session,directory,name,values)
        m=Model(part)
        make(m,True)
        fit(part)
        save(part)
        log("NATIVE_PART {} | {} features | {} bodies".format(name,len(m.features),len(list(part.Bodies))))
        if name=="bucket":
            optional(log,"bucket viewport",screenshot,part,directory/"01_bucket_detail.png")


def pose_geometry(model,angles,explode=False):
    part=model.part
    points, rot, rams, _, _=g.evaluate(angles)
    root_frame(model)
    for key,angle,make in zip(("boom_base","boom_tip","stick_tip"),rot,(boom,stick,bucket)):
        frame=Placement(points[key],0.,angle)
        make(Model(part,frame),False)
    for key,data in rams.items():
        a,b=data[:2]
        for y in (-g.BOOM_HALF_Y,g.BOOM_HALF_Y) if key=="boom" else (0.,):
            offset=1250. if explode and key=="boom" and y<0 else 0.
            cylinder(Model(part,Placement(a,y-offset,g.direction(a,b))),key,False,False)
            cylinder(Model(part,Placement(b,y-offset*1.24,g.direction(b,a))),key,True,False)
    j=points["bucket_cyl_B"]
    for key,side in (("bucket_side",True),("bucket_boss",False)):
        first=points[key]
        linkage(Model(part,Placement(first,0.,g.direction(first,j))),side)
    for x,z in (points[name] for name in ("bucket_side","bucket_cyl_B","bucket_boss")):
        pin(Model(part,Placement((x,z))))
    if not explode:
        for name,(x,z) in points.items():
            twin=name.startswith("boom_cyl")
            for y,suffix in ((-g.BOOM_HALF_Y,"_R"),(g.BOOM_HALF_Y,"_L")) if twin else ((0.,""),):
                datum=part.Points.CreatePoint(point((x,y,z)))
                builder=part.BaseFeatures.CreatePointFeatureBuilder(NXOpen.Features.Feature.Null)
                try:
                    builder.Point=datum
                    feature=builder.CommitFeature()
                finally:
                    builder.Destroy()
                feature.SetName("J_"+name+suffix)
                datum.Blank()


def optional(log,label,call,*args):
    try:
        call(*args)
    except Exception:
        log("OPTIONAL FAILED {}\n{}".format(label,traceback.format_exc()))
    else:
        log("OPTIONAL OK "+label)


def main():
    root=Path(__file__).resolve().parent
    directory=root/("NX_NATIVE_"+datetime.now().strftime("%Y%m%d_%H%M%S"))
    directory.mkdir()
    with (directory/"nx_run.log").open("w",encoding="utf-8") as stream:
        def log(msg):
            print(msg)
            stream.write(msg+"\n")
            stream.flush()
        try:
            g.write_tables(directory)
            session=NXOpen.Session.GetSession()
            log("NXOPEN_RUNNING | Python {} | concept millimeters".format(sys.version.split()[0]))
            native_parts(session,directory,log)
            for name,angles in g.POSES.items():
                part=new_part(session,directory,"PC2008_"+name.upper()+"_PLACED_SOLIDS")
                pose_geometry(Model(part),angles)
                fit(part)
                save(part)
                log("NATIVE_POSE {} | {} bodies | multibody part".format(name,len(list(part.Bodies))))
                optional(log,name+" viewport",screenshot,part,directory/("pose_"+name+".png"))
                if name=="reach":
                    optional(log,"STEP AP214",step_export,session,part,directory/"PC2008_REACH_PLACED_SOLIDS.step")
            part=new_part(session,directory,"PC2008_REACH_EXPLODED_VIEW")
            pose_geometry(Model(part),g.POSES["reach"],explode=True)
            fit(part)
            save(part)
            log("NATIVE_VIEW exploded | separated right boom barrel and rod for inspection")
            log("NX_PILOT_PARTS_DONE")
        except Exception:
            log(traceback.format_exc())
            raise


if __name__=="__main__":
    main()
