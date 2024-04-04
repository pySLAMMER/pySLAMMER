clear;clc;

%% Set up the Import Options and import the data
opts = delimitedTextImportOptions("NumVariables", 2);
opts.DataLines = [3, Inf];
opts.Delimiter = ",";
opts.VariableNames = ["Times", "Accelerationgs"];
opts.VariableTypes = ["double", "double"];
opts.ExtraColumnsRule = "ignore";
opts.EmptyLineRule = "read";
% Replace file string below with desired SLAMMER time history file path.
data = readtable("C:\Users\donal\OneDrive\Documents\Python\SlidingBlock\Northridge 1994 - TAR-090 - 0.02s - 1.779g.csv", opts);
clear opts

time = table2array(data(:,'Times'));
a_dollar = table2array(data(:,'Accelerationgs')); % a$
a_crit = 0.1; % Critical acceleration (a_c) LINE 6
dt = time(2)-time(1); % Digitization interval LINE 7
z = time(end); % Duration of record LINE 8
k = length(a_dollar); % Number of entries in thf LINE 9
pos_prev = 0; % x(i-1) LINE 10
vel_prev = 0; % v(i-1) LINE 11
s = 0; % LINE 12
y = 0; % LINE 13
vel_curr = 0; % v(i) LINE 14
pos_curr = 0; % x(i) LINE 15
U = [];
for i = 1:k % LINE 16
    loop_accel = a_dollar(i); % a(i)
    if vel_curr < 0.00001 % LINE 18
        if abs(loop_accel) > a_crit % LINE 20
            n = loop_accel/abs(loop_accel); % LINE 22
        else % LINE 21
            n = loop_accel/a_crit; % LINE 24
        end % LINE 23
    else % LINE 19
        n = 1; % LINE 26
    end
    y = loop_accel - n*a_crit; % LINE 27
    vel_curr = vel_prev + (dt/2)*(y+s); % LINE 28
    if vel_curr > 0 % LINE 29
        pos_curr = pos_prev + (dt/2)*(vel_curr+vel_prev); % LINE 32
    else
        vel_curr = 0; % LINE 30
        y = 0; % LINE 31
    end
    pos_prev = pos_curr; % LINE 33
    vel_prev = vel_curr; % LINE 34
    s = y; % LINE 35
    U = [U,pos_curr];
end

disp(pos_curr*980.665)
plot(time,U);
