%This function uses the Newton Method to solve a set of equations with a
%given vector of unknowns,jacobian, and loading conditions

function u = NewtonM (u,F,r)

epsilon=10^-8;

u_old=u;
err=1;
i=0;
while err>epsilon
    [jaco]=NumDer(u_old,F);
    u_it=jaco\(F(u_old)-r);
    u=u-u_it;
    err=norm(u-u_old)/norm(u);
    u_old=u;
    i=i+1;
end
u=u_old;
end