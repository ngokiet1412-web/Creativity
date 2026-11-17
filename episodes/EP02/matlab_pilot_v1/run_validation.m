function run_validation(out, cad)
% Isolated Issue17 pilot. Requires only base MATLAB. No source CAD or Argon edits.
here=fileparts(mfilename('fullpath'));
P=jsondecode(fileread(fullfile(here,'shared_model.json')));
if ~isfolder(out), mkdir(out); end
Q=fullfile(out,'matlab'); if ~isfolder(Q), mkdir(Q); end
copyfile(fullfile(here,'shared_model.json'),fullfile(Q,'shared_model.json'));
base=readtable(fullfile(out,'baseline','animation','motion_trace_v3.csv'));
% Baseline pinned replay must agree with the original public CSV, independently archived.
ref=readtable(fullfile(out,'baseline_reference.csv'));
baselineError=max(abs(base{:,:}-ref{:,:}),[],'all');
assert(baselineError<1e-8,'Pinned baseline did not reproduce');
t=(0:2160)'/120; [q,v,a,j]=trajectory(P.keys,t,true);
[qo,vo,ao,jo]=trajectory(P.keys,t,false);
[L,clearance,closure,margin,pointFrames]=poses(P,q);
oldP=P; oldP.joints.arm_cyl_A=[3565.7;961.4]; oldP.joints.bucket_cyl_A=[500;400];
[Lo,~,~,~,~]=poses(oldP,qo);
% Differentiate FK at a finer step; no toolbox, derivative of geometry not animation speed tricks.
h=.001; [qm,~,~,~]=trajectory(P.keys,t-h,true); [qp,~,~,~]=trajectory(P.keys,t+h,true);
[Lminus,~,~,~,~]=poses(P,qm); [Lplus,~,~,~,~]=poses(P,qp);
pvel=(Lplus-Lminus)/(2*h); pacc=(Lplus-2*L+Lminus)/(h*h);
pvel(t==0 | t>=16.8,:)=0; pacc(t>=16.8,:)=0;
% At t=0 use forward second derivative: pre-start history is deliberately outside this pilot.
[q2,~,~,~]=trajectory(P.keys,2*h,true); [L2,~,~,~,~]=poses(P,q2);
pacc(1,:)=(L2-2*Lplus(1,:)+L(1,:))/(h*h);
pj=zeros(size(pacc)); for k=1:3, pj(:,k)=gradient(pacc(:,k),t); end
names={'boom','arm','bucket'}; closed=zeros(1,3); strokeMax=closed; count=closed;
Ac=closed; Ar=closed;
for k=1:3
    s=P.act.(names{k}); closed(k)=s.closed; strokeMax(k)=s.stroke; count(k)=s.qty;
    Ac(k)=pi*(s.bore/1000)^2/4; Ar(k)=pi*((s.bore/1000)^2-(s.rod/1000)^2)/4;
end
stroke=L-closed; overlap=2*closed-320-L;
f=P.fluid;
capColumn=L-(closed-f.piston_cap_from_rod_eye_from_closed_mm)-f.head_inner_mm;
rodColumn=(closed-f.gland_inner_from_closed_mm)-(L-(closed-f.piston_rod_from_rod_eye_from_closed_mm));
assert(all(capColumn>0,'all') && all(rodColumn>0,'all'),'Fluid column nonpositive');
capVol=capColumn.*Ac; rodVol=rodColumn.*Ar; % mm*m^2 = L
pc=P.pressure_case.cap_bar; pr=P.pressure_case.rod_bar;
force=(pc*Ac-pr*Ar)*1e5;
qcap=pvel.*Ac*60; qrod=-pvel.*Ar*60; % Signed flow INTO each chamber; negative is outflow.
qsupply=max(qcap,0)+max(qrod,0); qreturn=max(-qcap,0)+max(-qrod,0);
assert(abs(Ac(1)*100e5-113097.3355292326)<1e-7);
assert(abs(Ac(1)*.01*60000-6.785840131753954)<1e-10);
assert(max(abs(qcap+qrod-pvel.*(Ac-Ar)*60),[],'all')<1e-10);
hydraulicPower=(pc*qcap+pr*qrod)*1e5/60000;
assert(max(abs(hydraulicPower-pvel/1000.*force),[],'all')<1e-7);
% Reversed velocity test ensures supply and return swap cap/annular roles.
assert(all((-Ac*.01*60000)<0) && all((Ar*.01*60000)>0));
assert(all(stroke>=0,'all') && all(stroke<=strokeMax,'all'));
assert(min(overlap,[],'all')>250 && max(closure)<1e-8 && min(clearance)>20 && min(margin)>0);
% All recorded NX joints and lengths at the exact three approved concept poses.
J=readtable(fullfile(cad,'joint_map.csv'),'TextType','string');
N=readtable(fullfile(cad,'pose_check.csv'),'TextType','string');
poseNames={'low','reach','high'}; keyTimes=[0,5.8,16.8]; rows={}; maxJ=0;
for i=1:3
    [qq,~,~,~]=trajectory(P.keys,keyTimes(i),true); [ll,~,cc,~,pts]=poses(P,qq);
    subset=J(J.pose==poseNames{i},:);
    for k=1:height(subset)
        xy=pts{1}.(char(subset.joint_id(k))); maxJ=max(maxJ,norm(xy-[subset.x_mm(k),subset.z_mm(k)]));
    end
    for k=1:3
        nn=N.pin_distance_mm(N.pose==poseNames{i} & N.actuator==names{k});
        rows(end+1,:)={poseNames{i},names{k},nn,ll(k),abs(nn-ll(k)),cc}; %#ok<AGROW>
    end
end
C=cell2table(rows,'VariableNames',{'pose','actuator','nx_mm','matlab_mm','error_mm','closure_mm'});
writetable(C,fullfile(Q,'nx_fit_pose_comparison.csv'));
assert(maxJ<1e-5 && max(C.error_mm)<1e-5);
% Analytic one-sided endpoint and splice derivative checks (not a finite-rate estimate).
edges=[14.2,16.8]; edgeRows={};
for e=edges
    [~,vl,al,~]=trajectory(P.keys,e-1e-8,true); [~,vr,ar,~]=trajectory(P.keys,e+1e-8,true);
    edgeRows(end+1,:)={e,max(abs(vl-vr)),max(abs(al-ar))}; %#ok<AGROW>
end
E=cell2table(edgeRows,'VariableNames',{'time_s','velocity_jump_deg_s','acceleration_jump_deg_s2'});
writetable(E,fullfile(Q,'endpoint_continuity.csv'));
assert(max(E.velocity_jump_deg_s)<1e-6 && max(E.acceleration_jump_deg_s2)<1e-6);
% Original final acceleration approached from the moving side.
[~,~,originalStopA,~]=trajectory(P.keys,16.8-1e-10,false);
T=table(t); T.Properties.VariableNames={'t_s'};
for k=1:3
    n=names{k};
    fields={'angle_deg','angular_velocity_deg_s','angular_acceleration_deg_s2','angular_jerk_deg_s3','length_mm','stroke_mm','velocity_mm_s','acceleration_mm_s2','jerk_mm_s3','overlap_mm','cap_column_mm','rod_column_mm','cap_volume_L','rod_volume_L','force_single_N','force_group_N','cap_in_L_min','rod_in_L_min','supply_single_L_min','return_single_L_min','supply_group_L_min','return_group_L_min'};
    vals={q(:,k),v(:,k),a(:,k),j(:,k),L(:,k),stroke(:,k),pvel(:,k),pacc(:,k),pj(:,k),overlap(:,k),capColumn(:,k),rodColumn(:,k),capVol(:,k),rodVol(:,k),repmat(force(k),numel(t),1),repmat(force(k)*count(k),numel(t),1),qcap(:,k),qrod(:,k),qsupply(:,k),qreturn(:,k),qsupply(:,k)*count(k),qreturn(:,k)*count(k)};
    for z=1:numel(fields), T.([n '_' fields{z}])=vals{z}; end
end
T.clearance_hull_mm=clearance; T.four_bar_error_mm=closure;
T.cap_pressure_HYPOTHETICAL_bar=repmat(pc,numel(t),1); T.rod_pressure_HYPOTHETICAL_bar=repmat(pr,numel(t),1);
writetable(T,fullfile(Q,'validation_120hz.csv')); writetable(T(1:4:2160,:),fullfile(Q,'motion_540_frames.csv'));
% Export real pin locations for future Blender integration, no Blender source changes.
pinRows={};
for ii=1:4:2160
    pp=pointFrames{ii}; fn=fieldnames(pp);
    for k=1:numel(fn)
        xz=pp.(fn{k}); ys=0; if startsWith(fn{k},'boom_cyl_'), ys=[-P.boom_half_y,P.boom_half_y]; end
        for yy=ys, pinRows(end+1,:)={t(ii),fn{k},xz(1),yy,xz(2)}; end %#ok<AGROW>
    end
end
writetable(cell2table(pinRows,'VariableNames',{'t_s','joint_id','x_mm','y_mm','z_mm'}),fullfile(Q,'pins_540_frames.csv'));
summary=struct('status','PASS for analytic concept checks; continuous CAD collision NOT VERIFIED', ...
    'matlab_version',version,'baseline_replay_max_error',baselineError,'samples',numel(t),'frames',540, ...
    'nx_max_joint_error_mm',maxJ,'nx_max_length_error_mm',max(C.error_mm), ...
    'min_hull_clearance_mm',min(clearance),'max_four_bar_error_mm',max(closure),'min_toggle_margin_mm',min(margin), ...
    'stroke_min_mm',min(stroke),'stroke_max_mm',max(stroke),'min_overlap_mm',min(overlap,[],'all'), ...
    'original_stop_acceleration_deg_s2',originalStopA,'new_stop_acceleration_deg_s2',a(end,:), ...
    'max_angle_change_deg',max(abs(q-qo)), 'max_old_geometry_length_delta_mm',max(abs(L-Lo)), ...
    'force_single_N',force,'force_group_N',force.*count,'max_supply_group_L_min',max(qsupply.*count), ...
    'pressure_assumption',P.pressure_case,'initial_acceleration_note','Initial acceleration is inherited; only final stop is repaired. Jerk is bounded but not C3 at splice.', ...
    'scope','Kinematic consistency, not inverse dynamics, hydraulic transient, ground mesh contact, structural safety or OEM certification');
fid=fopen(fullfile(Q,'summary.json'),'w'); fwrite(fid,jsonencode(summary,'PrettyPrint',true)); fclose(fid);
% Neutral publication plots with explicit units and assumptions.
fig=figure('Visible','off','Position',[50 50 1500 1200],'Color','w'); tiledlayout(4,2);
draw(t,q,'Link angles','deg',names); draw(t,stroke,'Cylinder extension','mm',names);
draw(t,pvel,'Piston velocity','mm/s',names); draw(t,pacc,'Piston acceleration','mm/s^2',names);
draw(t,repmat(force,numel(t),1),'HYPOTHETICAL pressure force per cylinder','N',names);
draw(t,qsupply.*count,'Group supply flow (boom x2)','L/min',names);
draw(t,qreturn.*count,'Group return flow (boom x2)','L/min',names);
draw(t,repmat([pc,pr],numel(t),1),'HYPOTHETICAL chamber pressures','bar',{'cap','rod'});
savefig(fig,fullfile(Q,'engineering_plots.fig')); exportgraphics(fig,fullfile(Q,'engineering_plots.png'),'Resolution',150); close(fig);
fig=figure('Visible','off','Position',[50 50 1500 900],'Color','w'); tiledlayout(2,2);
draw(t,[qo(:,1),q(:,1)],'Boom angle: baseline vs repaired','deg',{'baseline','repaired'});
draw(t,[vo(:,1),v(:,1)],'Boom angular velocity','deg/s',{'baseline','repaired'});
draw(t,[ao(:,1),a(:,1)],'Boom angular acceleration (old discontinuity at 16.8 s)','deg/s^2',{'baseline','repaired'});
draw(t,[jo(:,1),j(:,1)],'Regular jerk pieces (old stop has an impulse)','deg/s^3',{'baseline','repaired'});
savefig(fig,fullfile(Q,'stop_comparison.fig')); exportgraphics(fig,fullfile(Q,'stop_comparison.png'),'Resolution',150); close(fig);
fprintf('VALIDATION_PASS: %d samples; NX error %.3g mm; boom single force %.3f N\n',numel(t),maxJ,force(1));
end

function draw(t,x,ttl,y,names)
ax=nexttile;
colororder(ax,[.08,.36,.67; .72,.27,.08; .08,.49,.32]);
plot(ax,t,x,'LineWidth',1.6); grid(ax,'on');
set(ax,'Color','w','XColor',[.15,.18,.23],'YColor',[.15,.18,.23],'GridColor',[.5,.57,.65]);
title(ax,ttl,'Color',[.10,.16,.24]); xlabel(ax,'Time [s]'); ylabel(ax,y);
legend(ax,names,'Location','best','Color','w','TextColor',[.1,.16,.24]);
end

function [q,v,a,j]=trajectory(keys,t,repair)
t=t(:); q=zeros(numel(t),3); v=q; a=q; j=q;
for k=1:3
    pp=spline(keys(:,1),[0;keys(:,k+1);0]);
    pp1=deriv(pp); pp2=deriv(pp1); pp3=deriv(pp2);
    tc=max(0,min(t,16.8)); q(:,k)=ppval(pp,tc); v(:,k)=ppval(pp1,tc); a(:,k)=ppval(pp2,tc); j(:,k)=ppval(pp3,tc);
    if repair
        T=2.6; x0=ppval(pp,14.2); v0=ppval(pp1,14.2); a0=ppval(pp2,14.2);
        c0=x0; c1=v0*T; c2=a0*T*T/2;
        c345=[1 1 1;3 4 5;6 12 20]\[keys(end,k+1)-c0-c1-c2;-c1-2*c2;-2*c2];
        c=[flipud(c345);c2;c1;c0]'; mask=t>=14.2 & t<=16.8; u=(t(mask)-14.2)/T;
        q(mask,k)=polyval(c,u); v(mask,k)=polyval(polyder(c),u)/T;
        a(mask,k)=polyval(polyder(polyder(c)),u)/T^2; j(mask,k)=polyval(polyder(polyder(polyder(c))),u)/T^3;
    end
end
v(t<0 | t>16.8,:)=0; a(t<0 | t>16.8,:)=0; j(t<0 | t>16.8,:)=0;
end

function d=deriv(p)
[b,c,~,o,dim]=unmkpp(p); d=mkpp(b,c(:,1:o-1).*(o-1:-1:1),dim);
end

function [L,clearance,closure,margin,points]=poses(P,q)
% FK adapted from Argon PR15 evaluate_pose; corrected V3-fit joints supplied only by JSON.
L=zeros(size(q)); clearance=zeros(size(q,1),1); closure=clearance; margin=clearance; points=cell(size(q,1),1);
rot=@(v,d) [cosd(d)*v(1)-sind(d)*v(2),sind(d)*v(1)+cosd(d)*v(2)];
for i=1:size(q,1)
    ba=q(i,1); sa=ba-q(i,2); ga=sa-q(i,3)+90;
    b=rot([P.boom_len,0],ba); c=b+rot([P.stick_len,0],sa);
    side=b+rot(P.joints.bucket_side,sa); boss=c+rot(P.joints.bucket_boss,ga);
    d=norm(boss-side); margin(i)=min(d-abs(P.link_side-P.link_h),P.link_side+P.link_h-d);
    assert(margin(i)>0,'Four-bar unreachable/toggle'); u=(boss-side)/d;
    x=(P.link_side^2-P.link_h^2+d*d)/(2*d); h=sqrt(P.link_side^2-x*x);
    knee=side+x*u+h*[-u(2),u(1)];
    p=struct('boom_base',[0,0],'boom_tip',b,'stick_tip',c,'bucket_side',side,'bucket_boss',boss,'bucket_cyl_B',knee, ...
        'boom_cyl_A',P.joints.boom_cyl_A(:)','boom_cyl_B',rot(P.joints.boom_cyl_B,ba), ...
        'arm_cyl_A',rot(P.joints.arm_cyl_A,ba),'arm_cyl_B',b+rot(P.joints.arm_cyl_B,sa),'bucket_cyl_A',b+rot(P.joints.bucket_cyl_A,sa));
    L(i,:)=[norm(p.boom_cyl_B-p.boom_cyl_A),norm(p.arm_cyl_B-p.arm_cyl_A),norm(knee-p.bucket_cyl_A)];
    closure(i)=max(abs([norm(knee-side)-P.link_side,norm(knee-boss)-P.link_h]));
    hull=P.bucket_hull; z=zeros(size(hull,1),1); for k=1:size(hull,1), hh=c+rot(hull(k,:),ga); z(k)=hh(2); end
    clearance(i)=min(z)-P.ground_z; points{i}=p;
end
end
