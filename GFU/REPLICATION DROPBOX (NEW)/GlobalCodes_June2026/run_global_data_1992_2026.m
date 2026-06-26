
clear all

%data=xlsread('globa_data_estimation_June2019.xlsx','2019');% dataset 1992-2019
%data=xlsread('cc_globalfactor_1992M72020M5.xlsx');% dataset 1992-2020
%LORENZO: new line to upload the new dataset
data=xlsread('cc_globalfactor_1992M72026M6.xlsx');% dataset 1992M7-2026M6
[T,N] = size(data);  
Mx = nanmean(data);
Wx = nanstd(data);
dataNaN = (data-repmat(Mx,T,1))./repmat(Wx,T,1);
data=dataNaN;
% to count for the number of values which are not nan: nnz(~isnan(data))
% North America
bigZ_ns{1}{1}=data(:,1:3); % US
bigZ_ns{1}{2}=data(:,4:6); % Canada
bigZ_ns{1}{3}=data(:,7:9); % Mexico
% Europe
bigZ_ns{2}{1}=data(:,10:12); % Germany
bigZ_ns{2}{2}=data(:,13:15); % Austria
bigZ_ns{2}{3}=data(:,16:18); % Belgium
bigZ_ns{2}{4}=data(:,19:21); % Czech Republic 
bigZ_ns{2}{5}=data(:,22:24); % Denmark
bigZ_ns{2}{6}=data(:,25:27); % Finland 
bigZ_ns{2}{7}=data(:,28:30); % France
bigZ_ns{2}{8}=data(:,31:33); % Great Britain
bigZ_ns{2}{9}=data(:,34:36); % Greece
bigZ_ns{2}{10}=data(:,37:39); % Hungary
bigZ_ns{2}{11}=data(:,40:42); % Ireland
bigZ_ns{2}{12}=data(:,43:45); % Italy
bigZ_ns{2}{13}=data(:,46:48); % Netherlands
bigZ_ns{2}{14}=data(:,49:51); % Norway
bigZ_ns{2}{15}=data(:,52:54); % Poland
bigZ_ns{2}{16}=data(:,55:57); % Russia
bigZ_ns{2}{17}=data(:,58:60); % Spain
bigZ_ns{2}{18}=data(:,61:63); % Sweden
bigZ_ns{2}{19}=data(:,64:66); % Switzerland
bigZ_ns{2}{20}=data(:,67:69); % Turkey
% Oceania
bigZ_ns{3}{1}=data(:,70:72); % Australia
bigZ_ns{3}{2}=data(:,73:75); % New Zealand
% Latin America
bigZ_ns{4}{1}=data(:,76:77); % Argentina % no BY 
bigZ_ns{4}{2}=data(:,79:81); % Brazil
bigZ_ns{4}{3}=data(:,82:84); % Chile
bigZ_ns{4}{4}=data(:,85:87); % Colombia
bigZ_ns{4}{5}=data(:,88:90); % Peru
% Asia
bigZ_ns{5}{1}=data(:,91:93); % Japan
bigZ_ns{5}{2}=data(:,94:96); % China
bigZ_ns{5}{3}=data(:,97:98); % Hong Kong % no BY
bigZ_ns{5}{4}=data(:,100:102); % India
bigZ_ns{5}{5}=data(:,103:105); % Indonesia
bigZ_ns{5}{6}=data(:,106:108); % Korea
bigZ_ns{5}{7}=data(:,109:111); % Malaysia
bigZ_ns{5}{8}=data(:,112:113); % Pakistan % no BY
bigZ_ns{5}{9}=data(:,115:116); % Philippines % no BY
bigZ_ns{5}{10}=data(:,118:120); % Singapore
bigZ_ns{5}{11}=data(:,121:123); % Taiwan
bigZ_ns{5}{12}=data(:,124:126); % Thailand
% LORENZO: OLD: save('T ..... 20 .... bigZ_ns') --> NEW: save('T ..... 26 .... bigZ_ns');
save('Test2_42countries_92M726M5','bigZ_ns');
% LORENZO: OLD:  m = mat ... 20M5 ... ue); --> NEW:  m = mat ... 26M5 ... ue);
m = matfile('Test2_42countries_92M726M5','Writable',true);
ZNB = {[3 3 3]  [3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3]  [3 3] [3 3 3 3 3] [3 3 3 3 3 3 3 3 3 3 3 3]};
m.ZNB=ZNB;
run dhfm_main_globunc_1992
