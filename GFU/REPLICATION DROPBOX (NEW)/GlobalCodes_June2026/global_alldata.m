clear
clc

X = xlsread('data_exr.xlsx');
X = X(2:end,2:end);
Par.r=1;
Par.p=1;
Par.max_iter=500;
F = EM_DFM_SS_GC(X,Par);

