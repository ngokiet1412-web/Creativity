function solve_ep02_v3_motion(wsRoot)
% SOLVE_EP02_V3_MOTION  Continuous 18s (540 frames @ 30fps) kinematics & cutaway hydraulic trace
% Matches Siemens NX V2 (NX_NATIVE_V2_ARGON_20261116) geometry identically (mm, X-forward, Y-left, Z-up).
% Flow Q = A * v uses NX V2 brochure bore/rod dimensions; pressure values are illustrative concept curves only.

if nargin < 1 || isempty(wsRoot)
    here = fileparts(mfilename('fullpath'));
    wsRoot = fileparts(here);
end

sourceDir = fullfile(wsRoot, 'source_nx_v2');
animDir   = fullfile(wsRoot, 'animation');
qaDir     = fullfile(wsRoot, 'qa');
if ~isfolder(animDir), mkdir(animDir); end
if ~isfolder(qaDir),   mkdir(qaDir);   end

% --- Geometry constants matching geometry_v2_argon.py exactly (mm) ---
P.boom_len   = 5700.0;
P.stick_len  = 2925.0;
P.ground_z   = -1584.9;
P.boom_half_y = 520.0;
P.link_side  = 650.0;
P.link_h     = 750.0;

P.joints.boom_cyl_A   = [450.0,  -850.0];
P.joints.boom_cyl_B   = [2600.0,  220.0];
P.joints.arm_cyl_A    = [3565.7,  961.4];
P.joints.arm_cyl_B    = [-600.0,    0.0];
P.joints.bucket_cyl_A = [500.0,   400.0];
P.joints.bucket_side  = [2700.0,  150.0];
P.joints.bucket_boss  = [188.6,  -207.5];

P.act.boom   = struct('bore',120.0,'stroke',1334.0,'rod',85.0,'closed',2200.0);
P.act.arm    = struct('bore',135.0,'stroke',1490.0,'rod',95.0,'closed',1850.0);
P.act.bucket = struct('bore',115.0,'stroke',1120.0,'rod',80.0,'closed',1700.0);

P.bucket_hull = [ ...
    -1400.0, -830.0; -1400.0, -690.0; -850.0, -1015.0;
     -250.0,-1080.0;   300.0, -850.0;  510.0,  -535.0;
      560.0, -290.0;   370.0,  140.0;   90.0,   260.0; -120.0, 230.0];

% --- Step 1: Verify exact agreement with NX V2 pose_check.csv & joint_map.csv ---
nxPoseRef = readtable(fullfile(sourceDir, 'pose_check.csv'), 'TextType', 'string');
nxJointRef = readtable(fullfile(sourceDir, 'joint_map.csv'), 'TextType', 'string');

posesDef = { ...
    'low',   [22.5, 101.0, 56.0]; ...
    'reach', [29.0,  86.0, 62.0]; ...
    'high',  [42.0, 105.0, 76.0]};

maxPoseDistErr = 0.0;
maxJointCoordErr = 0.0;
poseVerifyRows = cell(0, 7);

for k = 1:size(posesDef, 1)
    pname = posesDef{k, 1};
    ang   = posesDef{k, 2};
    res   = evaluate_pose(P, ang);

    % Check distances against NX V2 pose_check.csv
    actNames = {'boom', 'arm', 'bucket'};
    dists    = [res.boom_len_mm, res.arm_len_mm, res.bucket_len_mm];
    for a = 1:3
        mask = (nxPoseRef.pose == string(pname)) & (nxPoseRef.actuator == string(actNames{a}));
        refDist = nxPoseRef.pin_distance_mm(mask);
        errMm = abs(dists(a) - refDist);
        maxPoseDistErr = max(maxPoseDistErr, errMm);
        poseVerifyRows(end+1, :) = {pname, actNames{a}, refDist, dists(a), errMm, res.four_bar_err_mm, res.clearance_mm}; %#ok<AGROW>
    end

    % Check all joint X/Z coordinates against NX V2 joint_map.csv
    jmask = (nxJointRef.pose == string(pname));
    subJ = nxJointRef(jmask, :);
    for rIdx = 1:height(subJ)
        jid = char(subJ.joint_id(rIdx));
        xz  = res.points.(jid);
        cerr = hypot(xz(1) - subJ.x_mm(rIdx), xz(2) - subJ.z_mm(rIdx));
        maxJointCoordErr = max(maxJointCoordErr, cerr);
    end
end

poseVerifyTable = cell2table(poseVerifyRows, 'VariableNames', ...
    {'pose','actuator','nx_v2_pin_distance_mm','matlab_pin_distance_mm','abs_diff_mm','four_bar_closure_mm','clearance_mm'});
writetable(poseVerifyTable, fullfile(qaDir, 'nx_v2_vs_matlab_three_poses.csv'));
assert(maxPoseDistErr < 1e-5 && maxJointCoordErr < 1e-5, 'Mismatch between MATLAB model and NX V2 CSV!');

% --- Step 2: Continuous 18.0s trajectory (C2 clamped cubic spline through LOW -> REACH -> HIGH) ---
% [t_s, boom_deg, arm_rel_deg, bucket_rel_deg]
% 0-4s:   Start heavy lift from LOW; slight bucket curl to retain soil load
% 4-8s:   Fluid lift passing exactly through NX REACH at t=5.8s as camera pushes in
% 8-14s:  Cutaway open - steady non-zero boom extension + fluid transfer while arm/bucket track
% 14-18s: Smooth deceleration settling cleanly onto NX HIGH at t=16.8..18.0s
keys = [ ...
    0.0,   22.5, 101.0, 56.0; ...   % Exact NX V2 LOW
    2.2,   24.2,  95.5, 52.0; ...   % Loaded curl & lift initiation
    5.8,   29.0,  86.0, 62.0; ...   % Exact NX V2 REACH
   10.5,   35.8,  94.5, 69.2; ...   % Mid cutaway steady lift
   14.2,   40.5, 102.8, 74.2; ...   % Late cutaway smooth approach
   16.8,   42.0, 105.0, 76.0];      % Exact NX V2 HIGH (hold 16.8..18.0s)

fps = 30;
nFrames = 540;
t30 = (0:(nFrames - 1))' / fps;
t120 = (0:(4 * nFrames))' / 120.0;

[T30, summary30]   = simulate_trajectory(P, keys, t30);
[~,   summary120]  = simulate_trajectory(P, keys, t120);

assert(summary120.min_clearance_mm > 20.0, 'Bucket too close to ground at 120Hz!');
assert(summary120.max_four_bar_err_mm < 1e-8, 'Four-bar closure error exceeded tolerance!');
assert(summary120.min_overlap_mm > 250.0, 'Cylinder rod-gland overlap violated!');
assert(summary120.all_strokes_valid, 'Cylinder stroke out of brochure limits!');

writetable(T30, fullfile(animDir, 'motion_trace_v3.csv'));

% Export unified joint map referencing frame 1 (LOW) and pose table
jNames = {'boom_base','boom_tip','stick_tip','bucket_side','bucket_boss','bucket_cyl_B', ...
          'boom_cyl_A','boom_cyl_B','arm_cyl_A','arm_cyl_B','bucket_cyl_A'};
jParents = {'carrier','boom','stick','stick','bucket','four_bar', ...
            'carrier','boom','boom','stick','stick'};
jRows = cell(0, 8);
for k = 1:size(posesDef, 1)
    pname = posesDef{k, 1};
    res = evaluate_pose(P, posesDef{k, 2});
    for j = 1:numel(jNames)
        jn = jNames{j};
        xz = res.points.(jn);
        if startsWith(jn, 'boom_cyl_')
            ys = [-P.boom_half_y, P.boom_half_y];
        else
            ys = 0.0;
        end
        for yv = ys
            jRows(end+1, :) = {pname, jn, jParents{j}, xz(1), yv, xz(2), ...
                P.act.boom.closed, 'NX_V2_SYNCHRONIZED'}; %#ok<AGROW>
        end
    end
end
jTable = cell2table(jRows, 'VariableNames', ...
    {'pose','joint_id','parent_link','x_mm','y_mm','z_mm','boom_closed_mm','provenance'});
writetable(jTable, fullfile(animDir, 'joint_map_v3.csv'));

% --- Step 3: Write JSON summary & high-res validation plots ---
qaStruct = struct( ...
    'matlab_version', version(), ...
    'fps', fps, ...
    'frame_count', nFrames, ...
    'duration_s', T30.t_s(end), ...
    'samples_120hz', numel(t120), ...
    'nx_v2_max_pin_distance_diff_mm', maxPoseDistErr, ...
    'nx_v2_max_joint_coord_diff_mm', maxJointCoordErr, ...
    'trajectory_summary_30fps', summary30, ...
    'trajectory_summary_120hz', summary120, ...
    'hydraulic_note', ['Piston cap/rod flow rates computed from NX V2 brochure bore/rod area * piston velocity (Q = A*v). ' ...
                       'Pressure trace is an illustrative boom-lift load curve, NOT field-measured Komatsu PC200-8 telemetry.'] ...
);
jsonStr = jsonencode(qaStruct, 'PrettyPrint', true);
fid = fopen(fullfile(qaDir, 'matlab_kinematics_qa_summary.json'), 'w', 'n', 'UTF-8');
fwrite(fid, jsonStr, 'char');
fclose(fid);

% Plot validation diagnostics
fig = figure('Visible', 'off', 'Color', [0.09 0.11 0.14], 'Position', [80 80 1440 900]);
tiledlayout(2, 2, 'TileSpacing', 'compact', 'Padding', 'compact');

% Panel 1: Joint angles
nexttile;
plot(T30.t_s, T30.boom_deg, 'Color', [0.98 0.72 0.15], 'LineWidth', 2.2); hold on;
plot(T30.t_s, T30.arm_rel_deg, 'Color', [0.28 0.78 0.96], 'LineWidth', 2.0);
plot(T30.t_s, T30.bucket_rel_deg, 'Color', [0.55 0.92 0.45], 'LineWidth', 2.0);
xline(4.0,'--w','Alpha',0.35); xline(8.0,'--w','Alpha',0.35); xline(14.0,'--w','Alpha',0.35);
grid on; set(gca, 'Color', [0.13 0.15 0.19], 'XColor', 'w', 'YColor', 'w');
title('Linkage Joint Angles (0-18s Continuous Trajectory)', 'Color', 'w');
xlabel('Time (s)', 'Color', 'w'); ylabel('Angle (deg)', 'Color', 'w');
legend('Boom Abs (deg)','Stick Rel (deg)','Bucket Rel (deg)','Location','best','TextColor','w','Color',[0.16 0.18 0.22]);

% Panel 2: Actuator strokes vs limits
nexttile;
plot(T30.t_s, T30.boom_stroke_mm, 'Color', [0.98 0.72 0.15], 'LineWidth', 2.2); hold on;
plot(T30.t_s, T30.arm_stroke_mm, 'Color', [0.28 0.78 0.96], 'LineWidth', 2.0);
plot(T30.t_s, T30.bucket_stroke_mm, 'Color', [0.55 0.92 0.45], 'LineWidth', 2.0);
yline(P.act.boom.stroke, ':', 'Boom Max 1334', 'Color', [0.98 0.72 0.15]);
yline(P.act.arm.stroke,  ':', 'Arm Max 1490',  'Color', [0.28 0.78 0.96]);
yline(P.act.bucket.stroke,':','Bucket Max 1120','Color', [0.55 0.92 0.45]);
grid on; set(gca, 'Color', [0.13 0.15 0.19], 'XColor', 'w', 'YColor', 'w');
title('Hydraulic Cylinder Strokes vs Brochure Limits', 'Color', 'w');
xlabel('Time (s)', 'Color', 'w'); ylabel('Extension (mm)', 'Color', 'w');
ylim([0 1600]);
legend('Boom (x2)','Arm','Bucket','Location','northwest','TextColor','w','Color',[0.16 0.18 0.22]);

% Panel 3: Boom piston speed & illustrative flow rates
nexttile;
yyaxis left
plot(T30.t_s, T30.boom_vel_mms, 'Color', [0.98 0.72 0.15], 'LineWidth', 2.2);
ylabel('Boom Piston Speed (mm/s)');
ax = gca; ax.YAxis(1).Color = [0.98 0.72 0.15];
yyaxis right
plot(T30.t_s, T30.q_boom_supply_Lpm, 'Color', [0.95 0.35 0.25], 'LineWidth', 1.8); hold on;
plot(T30.t_s, T30.q_boom_return_Lpm, 'Color', [0.25 0.70 0.98], 'LineWidth', 1.8);
ylabel('Single-Cylinder Q = A*v (L/min)');
ax.YAxis(2).Color = 'w';
xline(8.0,'--r','Cutaway Open','LabelVerticalAlignment','bottom');
xline(14.0,'--c','Cutaway Close','LabelVerticalAlignment','bottom');
grid on; set(gca, 'Color', [0.13 0.15 0.19], 'XColor', 'w');
title('Boom Cylinder Smooth Velocity & Continuity Q = A*v', 'Color', 'w');
xlabel('Time (s)', 'Color', 'w');

% Panel 4: Clearance & Four-Bar closure error
nexttile;
yyaxis left
plot(T30.t_s, T30.bucket_clearance_mm, 'Color', [0.45 0.92 0.55], 'LineWidth', 2.2);
yline(0, '--r', 'Grade');
ylabel('Bucket Clearance Above Grade (mm)');
ax2 = gca; ax2.YAxis(1).Color = [0.45 0.92 0.55];
yyaxis right
semilogy(T30.t_s, max(T30.four_bar_error_mm, 1e-13), 'Color', [0.95 0.65 0.25], 'LineWidth', 1.5);
ylabel('Four-Bar Closure Error (mm)');
ax2.YAxis(2).Color = [0.95 0.65 0.25];
grid on; set(gca, 'Color', [0.13 0.15 0.19], 'XColor', 'w');
title('Geometric Invariants (Ground Clearance & Four-Bar Closure)', 'Color', 'w');
xlabel('Time (s)', 'Color', 'w');

exportgraphics(fig, fullfile(qaDir, 'matlab_kinematics_plots_v3.png'), 'Resolution', 150);
close(fig);

fprintf('MATLAB_V3_DONE | maxPoseErr=%.3e mm | maxJointErr=%.3e mm | minClear=%.2f mm | maxFourBarErr=%.3e mm\n', ...
    maxPoseDistErr, maxJointCoordErr, summary120.min_clearance_mm, summary120.max_four_bar_err_mm);
end


function res = evaluate_pose(P, ang)
boomDeg      = ang(1);
armRelDeg    = ang(2);
bucketRelDeg = ang(3);

armDeg    = boomDeg - armRelDeg;
bucketDeg = armDeg - bucketRelDeg + 90.0;

rot = @(v, d) [cosd(d)*v(1) - sind(d)*v(2), sind(d)*v(1) + cosd(d)*v(2)];

foot = [0.0, 0.0];
b    = rot([P.boom_len, 0.0], boomDeg);
c    = b + rot([P.stick_len, 0.0], armDeg);

side = b + rot(P.joints.bucket_side, armDeg);
boss = c + rot(P.joints.bucket_boss, bucketDeg);

lineVec = boss - side;
d = norm(lineVec);
assert(abs(P.link_side - P.link_h) < d && d < (P.link_side + P.link_h), 'Four-bar unreachable');
u = lineVec / d;
x = (P.link_side^2 - P.link_h^2 + d^2) / (2 * d);
h = sqrt(max(0.0, P.link_side^2 - x^2));
j = side + x * u + h * [-u(2), u(1)];

pts = struct();
pts.boom_base    = foot;
pts.boom_tip     = b;
pts.stick_tip    = c;
pts.bucket_side  = side;
pts.bucket_boss  = boss;
pts.bucket_cyl_B = j;
pts.boom_cyl_A   = P.joints.boom_cyl_A;
pts.boom_cyl_B   = foot + rot(P.joints.boom_cyl_B, boomDeg);
pts.arm_cyl_A    = foot + rot(P.joints.arm_cyl_A, boomDeg);
pts.arm_cyl_B    = b + rot(P.joints.arm_cyl_B, armDeg);
pts.bucket_cyl_A = b + rot(P.joints.bucket_cyl_A, armDeg);

res.points = pts;
res.boom_abs_deg   = boomDeg;
res.arm_abs_deg    = armDeg;
res.bucket_abs_deg = bucketDeg;

res.boom_len_mm   = norm(pts.boom_cyl_B - pts.boom_cyl_A);
res.arm_len_mm    = norm(pts.arm_cyl_B - pts.arm_cyl_A);
res.bucket_len_mm = norm(pts.bucket_cyl_B - pts.bucket_cyl_A);

res.boom_ext_mm   = res.boom_len_mm   - P.act.boom.closed;
res.arm_ext_mm    = res.arm_len_mm    - P.act.arm.closed;
res.bucket_ext_mm = res.bucket_len_mm - P.act.bucket.closed;

res.boom_overlap_mm   = (P.act.boom.closed - 120.0)   + (P.act.boom.closed - 200.0)   - res.boom_len_mm;
res.arm_overlap_mm    = (P.act.arm.closed - 120.0)    + (P.act.arm.closed - 200.0)    - res.arm_len_mm;
res.bucket_overlap_mm = (P.act.bucket.closed - 120.0) + (P.act.bucket.closed - 200.0) - res.bucket_len_mm;

res.four_bar_err_mm = max(abs(norm(j - side) - P.link_side), abs(norm(j - boss) - P.link_h));

hullRot = zeros(size(P.bucket_hull, 1), 2);
for hi = 1:size(P.bucket_hull, 1)
    hullRot(hi, :) = c + rot(P.bucket_hull(hi, :), bucketDeg);
end
res.clearance_mm = min(hullRot(:, 2)) - P.ground_z;
end


function [T, summary] = simulate_trajectory(P, keys, t)
N = numel(t);
data = zeros(N, 35);

% Evaluate C2 clamped cubic splines (zero endpoint slope at t=0 and t=keys(end,1))
tk = keys(:, 1);
tEndMove = tk(end);
tClamped = min(t, tEndMove);
angInterp = zeros(N, 3);
for col = 1:3
    pp = spline(tk, [0.0; keys(:, col + 1); 0.0]);
    angInterp(:, col) = ppval(pp, tClamped);
end

% Hydraulic piston areas (m^2) for Boom cylinder from V2 brochure specs (120 mm bore, 85 mm rod)
A_cap_m2 = pi * (P.act.boom.bore * 1e-3)^2 / 4.0;
A_rod_m2 = pi * ((P.act.boom.bore * 1e-3)^2 - (P.act.boom.rod * 1e-3)^2) / 4.0;

minClear = inf;
maxErr = 0.0;
minOverlap = inf;
strokesOK = true;

for i = 1:N
    ti = t(i);
    ang = angInterp(i, :);

    r = evaluate_pose(P, ang);

    minClear = min(minClear, r.clearance_mm);
    maxErr = max(maxErr, r.four_bar_err_mm);
    minOverlap = min([minOverlap, r.boom_overlap_mm, r.arm_overlap_mm, r.bucket_overlap_mm]);
    if r.boom_ext_mm < 0 || r.boom_ext_mm > P.act.boom.stroke || ...
       r.arm_ext_mm < 0  || r.arm_ext_mm > P.act.arm.stroke   || ...
       r.bucket_ext_mm < 0 || r.bucket_ext_mm > P.act.bucket.stroke
        strokesOK = false;
    end

    data(i, 1:14) = [ti, ang(1), ang(2), ang(3), ...
        r.boom_abs_deg, r.arm_abs_deg, r.bucket_abs_deg, ...
        r.boom_len_mm, r.arm_len_mm, r.bucket_len_mm, ...
        r.boom_ext_mm, r.arm_ext_mm, r.bucket_ext_mm, r.clearance_mm];

    data(i, 15) = r.four_bar_err_mm;
    data(i, 16:33) = [ ...
        r.points.boom_tip, r.points.stick_tip, ...
        r.points.boom_cyl_A, r.points.boom_cyl_B, ...
        r.points.arm_cyl_A, r.points.arm_cyl_B, ...
        r.points.bucket_cyl_A, r.points.bucket_cyl_B, ...
        r.points.bucket_side];
    data(i, 34:35) = r.points.bucket_boss;
end

% Numerical velocity & illustrative Q = A * v, cap/rod chamber volumes in Liters
vel_mms = gradient(data(:, 8), t);
q_cap_Lpm = (A_cap_m2 * (vel_mms * 1e-3)) * 60000.0; % m^3/s -> L/min
q_rod_Lpm = (A_rod_m2 * (vel_mms * 1e-3)) * 60000.0;

% Effective fluid column lengths inside closed cylinder (closed = 2200 -> bore bottom ~ 220mm, gland ~ 2080mm -> 1860mm active)
cap_len_mm = 300.0 + data(:, 11);
rod_len_mm = max(80.0, 1560.0 - data(:, 11));
cap_vol_L = A_cap_m2 * (cap_len_mm * 1e-3) * 1000.0;
rod_vol_L = A_rod_m2 * (rod_len_mm * 1e-3) * 1000.0;
% Illustrative lifting pressure curve (bar) correlated with positive lift rate + loaded bucket weight
p_bar = 145.0 + 48.0 * cosd(data(:, 2)) + 1.15 * max(0.0, vel_mms);

fullMat = [data(:, 1:35), vel_mms, q_cap_Lpm, q_rod_Lpm, cap_vol_L, rod_vol_L, p_bar];

colNames = { ...
    't_s', 'boom_deg', 'arm_rel_deg', 'bucket_rel_deg', ...
    'boom_abs_deg', 'arm_abs_deg', 'bucket_abs_deg', ...
    'boom_cyl_length_mm', 'arm_cyl_length_mm', 'bucket_cyl_length_mm', ...
    'boom_stroke_mm', 'arm_stroke_mm', 'bucket_stroke_mm', 'bucket_clearance_mm', 'four_bar_error_mm', ...
    'boom_tip_x_mm', 'boom_tip_z_mm', 'stick_tip_x_mm', 'stick_tip_z_mm', ...
    'boom_cyl_A_x_mm', 'boom_cyl_A_z_mm', 'boom_cyl_B_x_mm', 'boom_cyl_B_z_mm', ...
    'arm_cyl_A_x_mm', 'arm_cyl_A_z_mm', 'arm_cyl_B_x_mm', 'arm_cyl_B_z_mm', ...
    'bucket_cyl_A_x_mm', 'bucket_cyl_A_z_mm', 'bucket_cyl_B_x_mm', 'bucket_cyl_B_z_mm', ...
    'bucket_side_x_mm', 'bucket_side_z_mm', 'bucket_boss_x_mm', 'bucket_boss_z_mm', ...
    'boom_vel_mms', 'q_boom_supply_Lpm', 'q_boom_return_Lpm', 'boom_cap_vol_L', 'boom_rod_vol_L', 'p_boom_illustrative_bar'};

T = array2table(fullMat, 'VariableNames', colNames);

summary = struct( ...
    'min_clearance_mm', minClear, ...
    'max_four_bar_err_mm', maxErr, ...
    'min_overlap_mm', minOverlap, ...
    'all_strokes_valid', strokesOK, ...
    'boom_stroke_range_mm', [min(T.boom_stroke_mm), max(T.boom_stroke_mm)], ...
    'arm_stroke_range_mm',  [min(T.arm_stroke_mm),  max(T.arm_stroke_mm)], ...
    'bucket_stroke_range_mm', [min(T.bucket_stroke_mm), max(T.bucket_stroke_mm)], ...
    'boom_max_speed_mms', max(abs(T.boom_vel_mms)) ...
);
end
