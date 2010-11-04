function [pts,seg] = HA_datacreate(p1,p2,p3,p4,n12,n23,n24)
%
% This function creates data for a simple bifurcation
%
%           /-> P3
%  P1 -> P2  
%           \-> P4
%
% Usage:  HA_datacreate();
%         HA_datacreate(p1,p2,p3,p4,n12,n23,n24)
%
% Input:  p1,p2,p3,p4 - [x y z r] 
%         n12,n23,n24 - number of points
%
% Output: pts   - points array
%         seg   - segments array
%

if (nargin<1)
  p1 = [0 0 0 .001];
  p2 = [0.5 0.5 0.5 .003];
  p3 = [0 1 1 .002];
  p4 = [1 1 0 .001];
  n12 = 3;
  n23 = 5;
  n24 = 6;
end

for i=1:4 
    pts(1:n12,i)= linspace (p1(i),p2(i),n12); 
end

for i=1:4 
    pts(n12:n12+n23-1,i)= linspace (p2(i),p3(i),n23); 
end

% This appends artery [p2,p4] to the end of the line segments array a
for i=1:4 
    pts(n12+n23:n12+n23-1+n24,i)= linspace (p2(i),p4(i),n24); 
end
pts(end-n24+1:end-1,:) = pts(end-n24+2:end,:);
pts = pts(1:end-1,:);

% This assigns the type for each artery
pts(:,end+1) = zeros (size(pts(:,end)));
pts(1,end) = 1;
pts(n12,end) = 3;
pts(n12+n23-1,end) = 2;
pts(end,end) = 2;

% This just adds in indexing
pts(:,1:end+1) = [(1:n12+n23+n24-2)' pts(:,1:end) ];

%
% This creates the seg array
%
seg (1:n12-1,:)= [ [1:n12-1]' [1:n12-1]' [2:n12]' ones(size([1:n12-1]')) ]; 

seg (n12:n12+n23-2,:) = [ [n12:n12+n23-2]' [n12:n12+n23-2]' [n12+1:n12+n23-1]' 2*ones(size([1:n23-1]')) ]; 

seg (n12+n23-1:n12+n23+n24-3,:) = [ [n12+n23-1:n12+n23+n24-3]' [n12+n23-1:n12+n23+n24-3]' [n12+n23:n12+n23+n24-2]' 3*ones(size([1:n24-1]')) ];
seg (n12+n23-1,2) = n12;