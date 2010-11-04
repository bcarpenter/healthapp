function [nodes,k] = newgridgen(skel,seg)

nodes=zeros(length(seg),4);
k=0;
s=1;

for i=1:length(seg)
    
    if i<length(seg)
        if seg(i,4)==seg(i+1,4)
            nodes(i,1)=s;
            nodes(i,2)=seg(i,4);
        else
            nodes(i,1)=s;
            nodes(i,2)=seg(i,4);
            k=[k;i];
            s=0;
        end
    else
        nodes(i,1)=s;
        nodes(i,2)=seg(i,4);
        k=[k;i];
    end
    
    %Length of Cell
    nodes(i,4)=norm(.0004297*skel(seg(i,3),2:4)-.0004297*skel(seg(i,2),2:4));
    
    %Initial Area of Cell
    nodes(i,3)=(skel(seg(i,3),5)+skel(seg(i,2),5))/2;
    
    s=s+1;
end