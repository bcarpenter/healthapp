function [bareas] = areainitial(skel,seg)

a=max(seg);
numart=a(4);
bareas=[];
x=[];
y=[];

for j=1:numart
    
    d{:,j}=seg(seg(:,4)==j);
    f=d{j};

    for k=1:length(f)
        
        if k==1 
            temparea=[skel(seg(f(k),2),5) skel(seg(f(k),3),5)];
            tempx=[skel(seg(f(k),2),2) skel(seg(f(k),3),2)];
            tempy=[skel(seg(f(k),2),3) skel(seg(f(k),3),3)];
        else
            temparea=[temparea,skel(seg(f(k),3),5)];
            tempx=[tempx,skel(seg(f(k),3),2)];
            tempy=[tempy,skel(seg(f(k),3),3)];
        end
  
    end
        
    bareas=[bareas,temparea];
    x=[x,tempx];
    y=[y,tempy];
end

bareas=bareas';
x=x';
y=y';
end