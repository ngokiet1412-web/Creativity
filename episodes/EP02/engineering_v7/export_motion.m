function export_motion(outDir)
% Illustrative PC200-8-like linkage. No measured or predicted pressure/flow.
here = fileparts(mfilename('fullpath'));
r = jsondecode(fileread(fullfile(here,'..','demo_v4','godot','art','rig.json')));
if ~isfolder(outDir)
    mkdir(outDir);
end
assert(r.px_per_m == 100, 'Update the coordinate conversion for this rig.');
t = (0:509)'/30;
keys = [0,    22, 101, 73;
        2.90, 31, 106, 79;
        3.72, 31, 106, 79;
        11.80,44, 108, 77;
        13.55,43, 108, 78;
        17.00,43, 108, 78];
[poses, points, extensions, clearance, closure] = solve(t,r,keys);
[~,~,~,subClearance,subClosure] = solve((0:2036)'/120,r,keys);
assert(min(subClearance)>=0 && max(subClosure)<1e-8);
names = {'boom_pivot','stick_pivot','bucket_pivot','tooth','boom_a','boom_b','stick_a','stick_b', ...
    'bucket_a','bucket_b','bucket_side','bucket_boss'};
T = array2table([t, -poses(:,1), poses(:,2), poses(:,3)-90, ...
    (extensions+[r.boom_cyl.closed r.arm_cyl.closed r.bucket_cyl.closed])*10, ...
    extensions*10, clearance*10, closure*10], ...
    'VariableNames',{'t_s','boom_deg','stick_deg','bucket_deg','boom_cyl_length_mm', ...
    'arm_cyl_length_mm','bucket_cyl_length_mm','boom_stroke_mm','stick_stroke_mm', ...
    'bucket_stroke_mm','ground_clearance_mm','four_bar_error_mm'});
% NX and Blender share x-forward, y-left, z-up. Coordinates are mm at grade.
for j = 1:numel(names)
    T.([names{j} '_x_mm']) = points(:,j,1)*10;
    T.([names{j} '_z_mm']) = (r.ground_y-points(:,j,2))*10;
end
writetable(T,fullfile(outDir,'motion_trace.csv'));
joint = string(names(:));
x_mm = reshape(points(1,:,1),[],1)*10;
y_mm = zeros(size(x_mm));
z_mm = (r.ground_y-reshape(points(1,:,2),[],1))*10;
parent = ["upper";"boom";"stick";"bucket";"upper";"boom";"boom";"stick"; ...
          "stick";"four_bar";"stick";"bucket"];
writetable(table(joint,parent,x_mm,y_mm,z_mm),fullfile(outDir,'joint_map.csv'));
f = figure('Visible','off','Color','white','Position',[100 100 1060 460]);
plot(t,extensions*10,'LineWidth',2);
grid on
xlabel('Time (s)'); ylabel('Extension from closed (mm)');
legend('Boom (both)','Stick','Bucket','Location','best');
title('Hydraulic Reveal | illustrative kinematics, 30 fps');
exportgraphics(f,fullfile(outDir,'actuator_strokes.png'),'Resolution',140);
close(f);
fprintf('MATLAB_MOTION_OK rows=%d sample120Hz=%d minClearMm=%.3f maxClosureMm=%g\n', ...
    height(T), numel(subClearance), min(subClearance)*10, max(subClosure)*10);
end

function [poses, points, extension, clearance, closure] = solve(t,r,keys)
poses = zeros(numel(t),3);
points = zeros(numel(t),12,2);
extension = zeros(numel(t),3);
clearance = zeros(numel(t),1);
closure = zeros(numel(t),1);
spec = [r.boom_cyl.closed, r.arm_cyl.closed, r.bucket_cyl.closed];
stroke = [r.boom_cyl.stroke, r.arm_cyl.stroke, r.bucket_cyl.stroke];
bks = r.bucket_sprite;
tip = bks.tip(:)-bks.hinge(:);
scale = r.bucket_tip_len/norm(tip);
rot = @(q) [cosd(q) -sind(q); sind(q) cosd(q)];
for i=1:numel(t)
    j = find(keys(:,1)<=t(i),1,'last');
    j = min(j,size(keys,1)-1);
    u = (t(i)-keys(j,1))/(keys(j+1,1)-keys(j,1));
    s = u^3*(10-15*u+6*u^2);
    p = keys(j,2:4)+(keys(j+1,2:4)-keys(j,2:4))*s;
    poses(i,:) = p;
    boom = rot(-p(1)); arm = rot(-p(1)+p(2)); bucket = rot(-p(1)+p(2)+p(3)-90);
    w1 = boom*[r.boom_len;0];
    w2 = w1+arm*[r.arm_len;0];
    boomA = r.boom_cyl.base_upper(:); boomB = boom*r.boom_cyl.eye_boom(:);
    armA = boom*r.arm_cyl.base_boom(:); armB = w1+arm*r.arm_cyl.eye_arm(:);
    bucketA = w1+arm*r.bucket_cyl.base_arm(:);
    side = w1+arm*r.bucket_cyl.side_pivot_arm(:);
    boss = w2+bucket*bks.link_boss_offset_px(:)*scale;
    a = r.bucket_cyl.side_len; b = r.bucket_cyl.h_len;
    d = norm(boss-side);
    assert(abs(a-b)<d && d<a+b, 'Four-bar joint out of reach at %.3f s.',t(i));
    along = (boss-side)/d;
    x = (a*a-b*b+d*d)/(2*d);
    bucketB = side + along*x - [-along(2);along(1)]*sqrt(a*a-x*x);
    closure(i) = max(abs([norm(bucketB-side)-a,norm(bucketB-boss)-b]));
    pts = [[0;0],w1,w2,w2+bucket*tip*scale,boomA,boomB,armA,armB,bucketA,bucketB,side,boss];
    points(i,:,1)=pts(1,:); points(i,:,2)=pts(2,:);
    extension(i,:) = [norm(boomB-boomA),norm(armB-armA),norm(bucketB-bucketA)]-spec;
    assert(all(extension(i,:)>=0 & extension(i,:)<=stroke), 'Cylinder stroke at %.3f s.',t(i));
    hull = w2+bucket*(r.bucket_hull_px'*scale);
    clearance(i) = r.ground_y-max(hull(2,:));
    assert(clearance(i)>=0, 'Bucket penetrates grade at %.3f s.',t(i));
end
end
