%This function will return a single velocity value for a given time based
%upon a semi-sinosoidal pulse with a definable frequency (default=1)

function[Q]=inflow(Q0,tau,t)
Q=[];
i=1;
while i<=length(t)
if t(i)>=0 && t(i)<=1
    if t(i)<tau
    Q(i)=Q0*sin(3.14*t(i)/tau);
    else
    Q(i)=0;
    end
else
    t1=fix(t(i));
    t2=t(i)-t1;
    if t2<tau
    Q(i)=Q0*sin(3.14*t2/tau);
    else
    Q(i)=0;
    end
end
i=i+1;
end
end