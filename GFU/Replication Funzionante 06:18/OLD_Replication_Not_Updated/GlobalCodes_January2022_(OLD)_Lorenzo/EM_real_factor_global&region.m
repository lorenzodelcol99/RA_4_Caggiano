clear
clc

X = xlsread('global dataset new.xlsx','1986_EM_44countries');
X_NA = xlsread('global dataset new.xlsx','1986_EM_44countries','B1:J376');
X_EU = xlsread('global dataset new.xlsx','1986_EM_44countries','K1:CA376');
X_Oceania = xlsread('global dataset new.xlsx','1986_EM_44countries','CB1:CG376');
X_SA = xlsread('global dataset new.xlsx','1986_EM_44countries','CH1:CV376');
X_Africa = xlsread('global dataset new.xlsx','1986_EM_44countries','CW1:DE376');
X_Asia = xlsread('global dataset new.xlsx','1986_EM_44countries','DF1:EC376');
% X = X(:,2:5);
Par.r=1;
Par.p=1;
Par.max_iter=50000;
F_NA = EM_DFM_SS(X_NA,Par);
F_EU = EM_DFM_SS(X_EU,Par);
F_Oceania = EM_DFM_SS(X_Oceania,Par);
F_SA = EM_DFM_SS(X_SA,Par);
F_Africa = EM_DFM_SS(X_Africa,Par);
F_Asia = EM_DFM_SS(X_Asia,Par);
F = EM_DFM_SS(X,Par);

