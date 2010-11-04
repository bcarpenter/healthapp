function [jaco] = NumDer (u,F)
epsilon=10^-8;
u1=u;
jaco=zeros(length(u),length(u));
for i=1:length(u)
    u1(i)=u1(i)+epsilon;
    jaco(:,i)=(F(u1)-F(u))/epsilon;
    u1(i)=u(i);
end
end