% This function outputs an initial guess, Function, and boundary conditions
% that are going to be 


function [u,F,r,refer,marker,A_0,b1,uout] = Fdef(u,utype,A_0,b1,c1,A_0star,b1star,c1star,uLRtemp,refer,marker,rho,mu,pout,Q0,t)
%Inflow
if utype==1
    
    F=@(u) [u(2);u(3)-u(2)*rho*c1star;u(3)-(b1star/A_0star)*u(1)^.5];
    
    %inflow(Q0,0.3,t)
    r=[inflow(Q0,0.3,t);uLRtemp(3)-uLRtemp(2)*rho*c1star;-(b1star/A_0star)*sqrt(A_0star)];
    
    %Womersley
    %COMING   
    u=u';
    uout=1;
end    

%Bifurcation
if utype==3
    
    q1=u(1,1)*u(1,2);
    q2=u(2,1)*u(2,2);
    q3=u(3,1)*u(3,2);
    
    tempmax=abs(max([q1 q2 q3]));
    
    if abs(q1)==tempmax
        uout=1;
        us=sign(q1);
        
    elseif abs(q2)==tempmax
        uout=2;
        us=sign(q2);
        u=[u(2,:);u(1,:);u(3,:)];
        refer=[refer(2);refer(1);refer(3)];
        marker=[marker(2);marker(1);marker(3)];
        A_0=[A_0(2);A_0(1);A_0(3)];
        b1=[b1(2);b1(1);b1(3)];
        c1=[c1(2);c1(1);c1(3)];
        
        
    else
        uout=3;
        us=sign(q3);
        u=[u(3,:);u(1,:);u(2,:)];
        refer=[refer(3);refer(1);refer(2)];
        marker=[marker(3);marker(1);marker(2)];
        A_0=[A_0(3);A_0(1);A_0(2)];
        b1=[b1(3);b1(1);b1(2)];
        c1=[c1(3);c1(1);c1(2)];
        
        
    end
    
     u=[u(:,1);u(:,2);u(:,3)];
     u=u(1:6);
     u_init=u;
    
    
    if or(us==0,us==1)
    
        F=@(u) [u(1)*u(4)-u(2)*u(5)-u(3)*u(6);b1(1)/(A_0(1))*sqrt(u(1))-b1(2)/(A_0(2))*sqrt(u(2))+.5*rho*(u(4)^2-u(5)^2);b1(1)/(A_0(1))*sqrt(u(1))-b1(3)/(A_0(3))*sqrt(u(3))+.5*rho*(u(4)^2-u(6)^2);u(4)+4*u(1)^.25*sqrt(b1(1)/(2*rho*A_0(1)));u(5)-4*u(2)^.25*sqrt(b1(2)/(2*rho*A_0(2)));u(6)-4*u(3)^.25*sqrt(b1(3)/(2*rho*A_0(3)))];
        r=[0;b1(1)/(A_0(1))*sqrt(A_0(1))-b1(2)/(A_0(2))*sqrt(A_0(2));b1(1)/(A_0(1))*sqrt(A_0(1))-b1(3)/(A_0(3))*sqrt(A_0(3));u_init(4)+4*u_init(1)^.25*sqrt(b1(1)/(2*rho*A_0(1)));u_init(5)-4*u_init(2)^.25*sqrt(b1(2)/(2*rho*A_0(2)));u_init(6)-4*u_init(3)^.25*sqrt(b1(3)/(2*rho*A_0(3)))];
        
    else
        
        F=@(u) [u(1)*u(4)-u(2)*u(5)-u(3)*u(6);b1(1)/(A_0(1))*sqrt(u(1))-b1(2)/(A_0(2))*sqrt(u(2))+.5*rho*(u(4)^2-u(5)^2);b1(1)/(A_0(1))*sqrt(u(1))-b1(3)/(A_0(3))*sqrt(u(3))+.5*rho*(u(4)^2-u(6)^2);u(4)-4*u(1)^.25*sqrt(b1(1)/(2*rho*A_0(1)));u(5)+4*u(2)^.25*sqrt(b1(2)/(2*rho*A_0(2)));u(6)+4*u(3)^.25*sqrt(b1(3)/(2*rho*A_0(3)))];
        r=[0;b1(1)/(A_0(1))*sqrt(A_0(1))-b1(2)/(A_0(2))*sqrt(A_0(2));b1(1)/(A_0(1))*sqrt(A_0(1))-b1(3)/(A_0(3))*sqrt(A_0(3));u_init(4)-4*u_init(1)^.25*sqrt(b1(1)/(2*rho*A_0(1)));u_init(5)+4*u_init(2)^.25*sqrt(b1(2)/(2*rho*A_0(2)));u_init(6)+4*u_init(3)^.25*sqrt(b1(3)/(2*rho*A_0(3)))];
        
    end
    
        
end



%Outflow
if utype==2
    
    %Ru=8*pi*mu/((A_0)^2);
    Ru=0;
    W=uLRtemp(2)+4*sqrt(b1/(2*rho*uLRtemp(1)))*uLRtemp(1)^.25;
    %Calculate electrical analog parameters and solve equations iter.
    
    %pout eliminated from the first equation
    F=@(u) [Ru*W*u(1)-4*Ru*sqrt(b1/(2*rho*A_0))*u(1)^(5/4)-(b1star/A_0star)*(sqrt(u(1))-sqrt(A_0star));u(3)-(b1star/A_0star)*(sqrt(u(1))-sqrt(A_0star));u(2)-uLRtemp(2)-(u(3)-uLRtemp(3))/(rho*c1star)];
    
    %u(3)+b1/(A_0)*(sqrt(u(1))-sqrt(A_0));u(2)+(pout-u(3))/(Ru*u(1))];
    
    r=[0;0;0];
    %r=0;
    
    uout=1;
    u=u';
    
end


end