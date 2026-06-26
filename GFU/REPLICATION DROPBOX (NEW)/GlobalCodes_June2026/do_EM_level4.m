% function do_EM_level4 extracts EM factors at various levels of the hierarchy

% get bigXmat, bigGmat and bigHmat from bigX data %

function [F,G,H,FH,FX,GX,K_F,K_G,K_H,C,bigXmat,bigGmat,bigHmat]=do_EM_level4(bigX,Bsub);
B = length(Bsub);
bigXmat = []; bigGmat = []; bigHmat = [];bigCmat = [];
Par.r=1;
Par.p=1;
Par.max_iter=50000;
K_F=1;

for b=1:B,
    Xb = bigX{b};
    K_G(b)=1;
    if iscell(Xb), 
        Xb=cell2mat(Xb);
    end;
     bigXmat=[bigXmat Xb];
     F_Xb = EM_DFM_SS(Xb,Par);
     GX{b}=F_Xb.F;
     
     for s = 1:Bsub(b), 
        Zbs = bigX{b}{s};
        F_Xbs = EM_DFM_SS(Zbs,Par);
        H{b}{s}=F_Xbs.F;
        bigHmat=[bigHmat H{b}{s}];      
        C{b}{s}{1}=F_Xbs.C;
%         bigCmat=[bigCmat C{b}{s}{l}];
        K_H{b}(s)=1;
          end;
     
      if Bsub(b) > 0,
          F_Gb= EM_DFM_SS(cell2mat(H{b}),Par);
          G{b}=F_Gb.F;
      else;
           G{b} = F_Xb.F;
      end;
      bigGmat=[bigGmat G{b}];
      
end;

      
      % Extract F from H's
F_H=EM_DFM_SS(bigHmat,Par);
FH = F_H.F;

% Extract F from X's
F_X=EM_DFM_SS(bigXmat,Par);
FX = F_X.F;

% Extract F from G's
F_G=EM_DFM_SS(bigGmat,Par);
F = F_G.F;
        
