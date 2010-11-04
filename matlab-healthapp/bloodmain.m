%This is the main blood-flow function


%MAIN - Calculates Blood Flow properties in Time for a Circle of Willis 

%Inputs: Skeleton Point Array (index,x-y-z position,type of cell)
%        Line Segment Array   (segment index,point indices,artery index) 

%Output: U is an array containing the flow variables for the system

function [U,Ainit] = bloodmain (Q0)



%NEWGRIDGEN - Takes output from image processing and creates cells for
%          numerical usage

%Output: domain (jx4 array containing local index,artery index, length of 
%                cell, & radii)

%        boundary (cell array containing connected nodes and an element
%                  that describes the type of boundary to be applied)

%        k (array containing the numbers of the global cells at the end of 
%           each artery)

%TEST FUNCTION
p1=[0 0 0 0.001];
p2=[1500 1500 1500 0.003];
p3=[0 3000 3000 0.002];
p4=[3000 3000 0 0.001];
n12=3000;
n23=3000;
n24=3000;
[skel,seg]=HA_datacreate(p1,p2,p3,p4,n12,n23,n24);


[domain,k] = newgridgen(skel,seg);
boundary = dataconv(skel,seg);
bond=size(boundary);


%INITIALIZE CONSTANTS
u0=0;             %Initial Inflow Velocity [M/s]

p0=0;             %Initial Internal Pressure [Pa]

pout=666.4;       %Venous Pressure [Pa]

tmax=5;          %Total time of virtual simulation [s]

rho=1050;         %Blood Density [kg/m^3]

%rho=1000;

mu=0.0045;        %Blood Viscosity [kg/M*s]

%mu=0.001;
         
%E=1000000;

E=1200000;         %Blood Vessel Elastic Modulus [Pa]


%INITIALIZE FLOW-VARIABLES
%U=area,velocity,pressire
U=datast(domain);
U=pi*U.*U;
%f=zeros(length(U),1);

%Initial Frictional Drag (check equation)
f=-22*mu*pi*U(:,2);

%c=wave speed
c=zeros(length(U),1);

%t=thickness (assume to be 25% R)
h=0.25*(1/pi)*sqrt(U(:,1));

%betas=stiffness measure
betas=(4/3)*sqrt(pi)*E*h;

%Ainit=initial cross-sectional areas
Ainit=U(:,1);

%B=Finite Difference Matrix
B=sparse(fdiff(domain));



%INITIALIZE INTERFACE VALUES
%Left-state
uL=zeros(length(domain)+length(k)-1,3);

%Right-state
uR=zeros(length(domain)+length(k)-1,3);

%Intermediate-state
uI=zeros(length(domain)+length(k)-1,3);

%cstar=wave-speeds
cstar=zeros(length(domain)+length(k)-1,length(domain)+length(k)-1);

%hstar=thickness
hstar=zeros(length(domain)+length(k)-1,1);

%betastar=stiffness measures
betastar=zeros(length(domain)+length(k)-1,1);

%Ainitstar=initial areas
Ainitstar=zeros(length(domain)+length(k)-1,1);


%CALCULATE SOME INITIAL INTERFACE VALUES
%Ainitstar
[radstar]=areainitial(skel,seg);



Ainitstar=pi*radstar.*radstar;
A=Ainitstar;

hstar=0.25*(1/pi)*Ainitstar.^.5;


betastar=(4/3)*sqrt(pi)*E*hstar;
    
    



%STEP-SIZES
delx=domain(:,4);

delt=max(delx./(2*sqrt(E*h./(2*rho*Ainit)).*U(:,1).^.25));

t=delt;

tic
%Iterate
while t<tmax

    
    %Define Values for use in Algorithm
    
    c=sqrt(E*h./(2*rho*Ainit)).*U(:,1).^.25;
    cstar=(sqrt(E*hstar./(2*rho*Ainitstar)).*A.^.25);
    
    lambda1=U(:,2)+c;
    lambda2=U(:,2)-c;
    
    
    %Calculate Interface values
    for i=1:length(k)-1
        
        
        %Equations PER ARTERY
        
        uL(k(i)+i+1:k(i+1)+i,1)=U(k(i)+1:k(i+1),1)+B(k(i)+1:k(i+1),k(i)+1:k(i+1))*U(k(i)+1:k(i+1),1).*(.5*(1-lambda1(k(i)+1:k(i+1))*delt./delx(k(i)+1:k(i+1))));
        uL(k(i)+i+1:k(i+1)+i,2)=U(k(i)+1:k(i+1),2)+B(k(i)+1:k(i+1),k(i)+1:k(i+1))*U(k(i)+1:k(i+1),2).*(.5*(1-lambda1(k(i)+1:k(i+1))*delt./delx(k(i)+1:k(i+1))));%+(delt/(2*rho))*f(k(i)+1:k(i+1),:)./U(k(i)+1:k(i+1),1);
        uL(k(i)+i+1:k(i+1)+i,3)=U(k(i)+1:k(i+1),3)+B(k(i)+1:k(i+1),k(i)+1:k(i+1))*U(k(i)+1:k(i+1),3).*(.5*(1-lambda1(k(i)+1:k(i+1))*delt./delx(k(i)+1:k(i+1))));
        
        
        uR(k(i)+i:k(i+1)-1+i,1)=U(k(i)+1:k(i+1),1)-B(k(i)+1:k(i+1),k(i)+1:k(i+1))*U(k(i)+1:k(i+1),1).*(.5*(1+lambda2(k(i)+1:k(i+1))*delt./delx(k(i)+1:k(i+1))));
        uR(k(i)+i:k(i+1)-1+i,2)=U(k(i)+1:k(i+1),2)-B(k(i)+1:k(i+1),k(i)+1:k(i+1))*U(k(i)+1:k(i+1),2).*(.5*(1+lambda2(k(i)+1:k(i+1))*delt./delx(k(i)+1:k(i+1))));%+(delt/(2*rho))*f(k(i)+1:k(i+1),:)./U(k(i)+1:k(i+1),1);
        uR(k(i)+i:k(i+1)-1+i,3)=U(k(i)+1:k(i+1),3)-B(k(i)+1:k(i+1),k(i)+1:k(i+1))*U(k(i)+1:k(i+1),3).*(.5*(1+lambda2(k(i)+1:k(i+1))*delt./delx(k(i)+1:k(i+1))));
        
        
    end
    
    %FILL IN INCORRECT VALUES
    for n=1:bond(1)
        
        if boundary(n,3)==0
            refer=boundary(n,2); 
            utype=boundary(n,1);
        else
            refer=boundary(n,2:4); 
            utype=boundary(n,1);
        end
        w=length(refer);
        u=zeros(w,3);
        A_0=zeros(w,1);
        b1=zeros(w,1);
        c1=zeros(w,1);
        p=zeros(w,1);
        ustar=zeros(3*w,1);
        z=length(ustar);
        
        
        for x=1:w
            u(x,:)=U(refer(x),:);
            A_0(x)=Ainit(refer(x));
            b1(x)=betas(refer(x));
            c1(x)=c(refer(x));
        end
        
        refer=refer';
        marker=domain(refer,:);
        marker=marker(:,2);
        
        if utype==1
            
            uLRtemp=uR(refer(1)+marker(1)-1,:);
            A_0star=Ainitstar(refer(1)+marker(1)-1);
            c1star=cstar(refer(1)+marker(1)-1);
            b1star=betastar(refer(1)+marker(1)-1);
            
        elseif utype==2
            
            uLRtemp=uL(refer(1)+marker(1),:);
            A_0star=Ainitstar(refer(1)+marker(1));
            c1star=cstar(refer(1)+marker(1));
            b1star=betastar(refer(1)+marker(1));
            
        else
            
        end
            
        [u,F,r,refer,marker,A_0,b1,uout]=Fdef(u,utype,A_0,b1,c1,A_0star,b1star,c1star,uLRtemp,refer,marker,rho,mu,pout,Q0,t);
        
        
        %NEED TO PLACE PROPER VALUES INTO uR AND uL MATRICES
        
        if utype==1
            
            ustar(1:3*w,1)=NewtonM(u,F,r);
        
            
            ustar=[ustar(1:w),ustar(w+1:2*w),ustar(2*w+1:3*w)];
            
           
            uL(refer+marker-1,:)=ustar;
            
            %LINE ADDED
            %uR(refer+marker-1,:)=ustar;
        
        
        elseif utype==3
            
            ustar(1:2*w,1)=NewtonM(u,F,r);
            p=(b1./A_0).*(sqrt(ustar(1:3))-sqrt(A_0));
            ustar(2*w+1:3*w,1)=p;
        
            
            ustar=[ustar(1:w),ustar(w+1:2*w),ustar(2*w+1:3*w)];
           
           %EMAIL RAZ TO WORK OUT DIRECTIONALITY CONCERN
           if uout==1
                uR(refer(1)+marker(1),:)=ustar(1,:);
                uL(refer(2)+marker(2)-1,:)=ustar(2,:);
                uL(refer(3)+marker(3)-1,:)=ustar(3,:);
            elseif uout==2
                ustar=[ustar(2,:);ustar(1,:);ustar(3,:)];
                refer=[refer(2,:);refer(1,:);refer(3,:)];
                marker=[marker(2,:);marker(1,:);marker(3,:)];
                uR(refer(1)+marker(1),:)=ustar(1,:);
                uL(refer(2)+marker(2)-1,:)=ustar(2,:);
                uL(refer(3)+marker(3)-1,:)=ustar(3,:);
            else
                ustar=[ustar(3,:);ustar(1,:);ustar(2,:)];
                refer=[refer(3,:);refer(1,:);refer(2,:)];
                marker=[marker(3,:);marker(1,:);marker(2,:)];
                uR(refer(1)+marker(1),:)=ustar(1,:);
                uL(refer(2)+marker(2)-1,:)=ustar(2,:);
                uL(refer(3)+marker(3)-1,:)=ustar(3,:);
            end
                
        
        elseif utype==2
            
            ustar(1:3*w,1)=NewtonM(u,F,r);
        
            
            ustar=[ustar(1:w),ustar(w+1:2*w),ustar(2*w+1:3*w)];
        
    
            uR(refer+marker,:)=ustar;
            
            
        end
        
        
    end
    
    
    
    %Use Euler Equations to coalesce twin edge values
    
    %cstar=sparse(diag((sqrt(E*hstar./(2*rho*Ainitstar)).*uL(:,1).^.25+sqrt(E*hstar./(2*rho*Ainitstar)).*uR(:,1).^.25)/2));
    %ORIGINALS
    uI(:,2)=(1./(2*rho*cstar)).*(uL(:,3)-uR(:,3))+0.5*(uL(:,2)+uR(:,2));
    
    uI(:,3)=.5*(uL(:,3)+uR(:,3))+.5*rho*cstar.*(uL(:,2)-uR(:,2));
    
    uI(:,1)=(uI(:,3).*Ainitstar./betastar+Ainitstar.^.5).^2;
    
    %EDITED
    %uI(:,2)=(1./(2*rho*cstar)).*(uR(:,3)-uL(:,3))+0.5*(uL(:,2)+uR(:,2));
    
    %uI(:,3)=.5*(uL(:,3)+uR(:,3))+.5*rho*cstar.*(uR(:,2)-uL(:,2));
    
    %uI(:,1)=(uI(:,3).*Ainitstar./betastar+Ainitstar.^.5).^2;
    
    %Finite Volume Updates
    
    
    for m=1:length(k)-1
        
        %AUtilda=U(k(m)+1:k(m+1),1).*U(k(m)+1:k(m+1),2)+(delt./delx(k(m)+1:k(m+1))).*(uI(k(m)+m:k(m+1)+m-1,1).*uI(k(m)+m:k(m+1)+m-1,2).*uI(k(m)+m:k(m+1)+m-1,2)-uI(k(m)+m+1:k(m+1)+m,1).*uI(k(m)+m+1:k(m+1)+m,2).*uI(k(m)+m+1:k(m+1)+m,2))+(delt./delx(k(m)+1:k(m+1))).*((uI(k(m)+m:k(m+1)+m-1,1)+uI(k(m)+m+1:k(m+1)+m,1))/(2*rho)).*(uI(k(m)+m+1:k(m+1)+m,3)-uI(k(m)+m:k(m+1)+m-1,3));%+(delt/rho)*f(k(m)+1:k(m+1));
        
        U(k(m)+1:k(m+1),1)=U(k(m)+1:k(m+1),1)+(delt./delx(k(m)+1:k(m+1))).*(uI(k(m)+m:k(m+1)+m-1,1).*uI(k(m)+m:k(m+1)+m-1,2)-uI(k(m)+m+1:k(m+1)+m,1).*uI(k(m)+m+1:k(m+1)+m,2));
    
        U(k(m)+1:k(m+1),2)=U(k(m)+1:k(m+1),2)+(delt./delx(k(m)+1:k(m+1))).*(0.5*uI(k(m)+m:k(m+1)+m-1,2).*uI(k(m)+m:k(m+1)+m-1,2)-0.5*uI(k(m)+m+1:k(m+1)+m,2).*uI(k(m)+m+1:k(m+1)+m,2)+uI(k(m)+m:k(m+1)+m-1,3)/rho-uI(k(m)+m+1:k(m+1)+m,3)/rho);
        
        %Utilda=AUtilda./U(k(m)+1:k(m+1),1);
    
        %ftilda=-22*pi*mu*Utilda
        
        %ftilda=0*Utilda;
    
        %U(k(m)+1:k(m+1),2)=Utilda;%(AUtilda+(delt/2)*((ftilda-f(k(m)+1:k(m+1)))/rho))./U(k(m)+1:k(m+1),1);
    
        %f(k(m)+1:k(m+1))=-22*pi*mu*U(k(m)+1:k(m+1),2);
        
        %f(k(m)+1:k(m+1))=0*U(k(m)+1:k(m+1),2);
    
        U(k(m)+1:k(m+1),3)=betas(k(m)+1:k(m+1))./Ainit(k(m)+1:k(m+1)).*(sqrt(U(k(m)+1:k(m+1),1))-sqrt(Ainit(k(m)+1:k(m+1))));
    
    end

    
    %Step forward in time
    
    if max(abs(max(lambda1)),abs(min(lambda2)))*delt/(delx)<0.5
        
        delt=delt*0.1;
        
    elseif max(abs(max(lambda1)),abs(min(lambda2)))*delt/(delx)>5
        
        delt=delt*10;
        
    end
       
    A=uI(:,1);
    
    uL=zeros(length(domain)+length(k)-1,3);
    uR=zeros(length(domain)+length(k)-1,3);
    uI=zeros(length(domain)+length(k)-1,3);
    
    t=t+delt;
    
    
    
end

toc

end