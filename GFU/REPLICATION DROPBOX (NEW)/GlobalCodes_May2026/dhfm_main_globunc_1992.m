      
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% Replication code for the paper "Dynamic Hierarchical Factor Models"                                         %%%
%%%                                                                                                             %%%
%%% Copyright: Emanuel Moench (emanuel.moench@ny.frb.org), Serena Ng(serena.ng@columbia.edu, and                %%%
%%%            Simon Potter (simon.potter@ny.frb.org                                                            %%% 
%%%                                                                                                             %%%
%%% Implements a Gibbs sampler to estimate the following factor model:                                          %%%
%%%                                                                                                             %%%
%%%     Z_bsnt = Lambda_Hbsn(L)'*H_bst + e_Zbsnt                                                                %%%             
%%%      H_bst = Lambda_Gbs(L)'*G_bt + e_Hbst                                                                   %%%
%%%       G_bt = Lambda_Fb(L)'*F_t + e_Gbt                                                                      %%%
%%%    e_Zbsnt = psi_Zbsn(L)*e_Zbsn_{t-1} + epsilon_Zbsnt                                                       %%% 
%%%     e_Hbst = psi_Hbs(L)*e_Hbs_{t-1} + epsilon_Hbst                                                          %%% 
%%%      e_Gbt = psi_Gb(L)*e_Gb_{t-1} + epsilon_Gbt                                                             %%% 
%%%        F_t = psi_F*F_{t-1} + epsilon_Ft                                                                     %%%
%%%                                                                                                             %%% 
%%% B is the number of blocks, Bsub(b) is the number of subblocks in block b,                                   %%%  
%%% Nsub is the number of series in subblock s of block b,                                                      %%%
%%%                                                                                                             %%%
%%% K_F is the number of common factors                                                                         %%%
%%% K_G(b) is the number of block-specific factors in block b,                                                  %%%
%%% K_H{b}(s) is the number of subblock-specific factors in subblock s of block b                               %%%
%%%                                                                                                             %%%
%%% Note that if for some b, K_H{b} is zero, then the observation equation becomes                              %%%
%%% Z_bsnt = Lambda_Gbn(L)'*G_bt + e_Zbnt                                                                       %%%
%%%                                                                                                             %%%
%%% q_F is the lag order of the transition equation F_t = psi_F*F_{t-1} + epsilon_Ft                            %%%
%%% q_G(b) is the lag order of the AR model for e_Gbt,                                                          %%%
%%% q_H(b) is the lag order of the AR model for all subblock-specific components e_Hbst                         %%%
%%% q_Z(b) is the lag order of the AR model for all idiosyncratic components e_Zbsnt                            %%%
%%%                                                                                                             %%%
%%% l_F(b) is the lag order of the factor loading polynomial Lambda_Fb(L)                                       %%%
%%% l_G(b) is the lag order of the factor loading polynomials Lambda_Gbs(L)                                     %%%
%%% l_H(b) is the lag order of the factor loading polynomials Lambda_Hbsn(L)                                    %%%
%%%                                                                                                             %%%
%%% Note that we set these to zero and restrict loading matrices to be lower-triangular with ones on the        %%% 
%%% diagonal in order to identify the factors; In principle, the loadings can be dynamic but then other         %%%
%%% restrictions need to be imposed in order to identify the factors and loadings                               %%%
%%%       
%%% Last modified by Efrem: July 21, 2020
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
clear all;

% n_burn=15000; n_keep=15000; n_skip=15; n_gibbs=n_burn+n_keep; % Giovanni's 10k
 n_burn=100; n_keep=100; n_skip=5; n_gibbs=n_burn+n_keep;
%% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Define model parameters
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% B=5;  % number of blocks -- 5 for the sample starting in 1986Q3 No African countries
% K_F=1; % common factor -- global uncertainty
% K_G=[1; 1; 1; 1; 1;]; % regional factors
% K_H{1}=[1 1 1]; % 3 countries in block 1 -- North America
% K_H{2}=[1 1 1 1 1 1 1 1 1 1 1 1]; % 12 countries block 2 -- Europe
% K_H{3}=[1 1]; % 2 countries Oceania
% K_H{4}=[1 1 1]; % K_H{4}=[1 1]; 3 countries Latin America
%%%%% K_H{5}=[1 1 1 1]; % K_H{5}=[1 1 1];
% K_H{5}=[1 1 1 1 1 1 1 1]; % 8 countries Asia

K_F=1; % common factor -- global uncertainty

% regional factors when B=5
K_G=[1; 1; 1; 1; 1]; 

% B=6;  % number of blocks -- 6 regions for new countries 1986
% % Country Specific factors for data starting from 1986 (whole sample:44 countries 3 series for each country)
% %Block 1 -- North America
% K_H{1}=[1 1 1]; % 3 countries in block 1 
% %Block 2 -- Europe
% K_H{2}=[1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1]; % 23 countries in block 2
% %Block 3 -- Oceania
% K_H{3}=[1 1]; % 2 countries in block 3
% %Block 4 -- South America
% K_H{4}=[1 1 1 1 1]; %5 countries in block 4
% %Block 5 -- Afica
% K_H{5}=[1 1 1]; %3 countries in block 5
% %Block 6 -- Asia
% K_H{6}=[1 1 1 1 1 1 1 1]; % 8 countries in block 6

B=5;  % number of blocks -- 5 regions for new countries 1987
% Country Specific factors for data starting from 1987 (whole sample:33 countries)
%Block 1 -- North America
K_H{1}=[1 1 1]; % 3 countries in block 1 
%Block 2 -- Europe
K_H{2}=[1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1]; % 20 countries in block 2
%Block 3 -- Oceania
K_H{3}=[1 1]; % 2 countries in block 3
%Block 4 -- South America
K_H{4}=[1 1 1 1 1]; %5 countries in block 4
%Block 5 -- Asia
K_H{5}=[1 1 1 1 1 1 1 1 1 1 1 1]; %12 countries in block 5

q_F=1;                 
q_G=[1 1 1 1 1 1 1];
q_H=[1 1 1 1 1 1 1];
q_Z=[1 1 1 1 1 1 1];

l_F=[0 0 0 0 0 0 0];            
l_G=[0 0 0 0 0 0 0];
l_H=[0 0 0 0 0 0 0];

sig_fix = .1;
noise_var = .2;
% LORENZO Line 107: OLD: gl .... 2020 ... ries --> NEW: gl ... 026_ ...ries
matname=['globunc_factors_1992_2026_42countries'];

%% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Load data 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%LORENZO Line 113: OLD: load 'Te_ ... 2M720M5' : --> NEW: load 'Te_ ... 26M5'
load 'Test2_42countries_92M726M5'
% ZNB: specify number of series in each block 

% bigZ_ns = {data_glob[3]  [20]  [2]  [5]  [12]}
% Bsub(b) is the number of sub-blocks in block b
% Nsub(b,s) is the size of subblock-j of block b
% K_H{b}(s) is the number of factors in sub-block s of block b
NB=[]; 
for b = 1:B,
    Bsub(b) = length(K_H{b}); 
    if K_H{b} == 0, Bsub(b) = 0; end;        
    for s=1:Bsub(b);
        Nsub(b,s)=ZNB{b}(s);  
    end;
    NB=[NB; sum(K_H{b})]; 
end;

%% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Initialize sampler
%% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
dhfm_initialize_sampler;

%% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Run sampler
%% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
dhfm_run_sampler;



