function bndr = dataconv(pts,seg)
%
% This functions converts from input I to output format O
%
% Usage: O = dataconv(I)
%
% Input: 
%
%




%start of bifurcation

nrbif = 0;
ls = length(seg);

for is = 1:ls
    switch  pts(seg(is,2),6)
        case 1
          nrbif = nrbif+1;
          bndr(nrbif,1)=1;
          bndr(nrbif,2)=is;
          bndr(nrbif,3:5) = [0 0 0];
        case 2
          nrbif = nrbif+1;
          bndr(nrbif,1)=2;
          bndr(nrbif,2)=is;
          bndr(nrbif,3:5) = [0 0 0];
        case 3
          fnd=0;
          for i=1:nrbif
              if bndr(i,5)==seg(is,2)
                  if bndr(i,3)==0
                      bndr(i,3)=is;
                  else
                      bndr(i,4)=is;
                  end
                  fnd=1;
              end
          end
          if fnd==0
            nrbif = nrbif+1;
            bndr(nrbif,1)=3;
            bndr(nrbif,2)=is;
            bndr(nrbif,3:4) = [0 0];
            bndr(nrbif,5)=seg(is,2);
          end
        otherwise
    end
        
    switch  pts(seg(is,3),6)
        case 1
          nrbif = nrbif+1;
          bndr(nrbif,1)=1;
          bndr(nrbif,2)=is;
          bndr(nrbif,3:5) = [0 0 0];
        case 2
          nrbif = nrbif+1;
          bndr(nrbif,1)=2;
          bndr(nrbif,2)=is;
          bndr(nrbif,3:5) = [0 0 0];
        case 3
          fnd=0;
          for i=1:nrbif
              if bndr(i,5)==seg(is,3)
                  if bndr(i,3)==0
                      bndr(i,3)=is;
                  else
                      bndr(i,4)=is;
                  end
                  fnd=1;
              end
          end
          if fnd==0
            nrbif = nrbif+1;
            bndr(nrbif,1)=3;
            bndr(nrbif,2)=is;
            bndr(nrbif,3:4) = [0 0];
            bndr(nrbif,5)=seg(is,3);
          end
        otherwise
    end
end
bndr = bndr(:,1:4);

%end of bifurcation