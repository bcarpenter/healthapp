from stencil_grid import StencilGrid
from stencil_kernel import StencilKernel

class LineKernel(StencilKernel):
    """A line stencil that runs over a line of nodes."""
    def kernel(self, inline, outline):
		# lambda1=U(:,2)+c;
		# lambda2=U(:,2)-c;
	    
	    # %Calculate Interface values
	    for i=1:length(k)-1 # -- k(i) is where the junction ends
		# eg. k = 0,2999,5998,8997
	        # %Equations PER ARTERY
	        for n=1:3 # %A,u,p -- HAVE TO CALCULATE all 3 (A,u,p)
				uL(k(i)+i+1:k(i+1)+i,n)= # uL(k(1)+2:k(2)+1,n)= # uL(0+2:2999+1,n) # uL(2:3000,n)
					U(k(i)+1:k(i+1),n)+ # U_j # U(k(1)+1:k(2),n)+ # U(1:2999,n)
					B(k(i)+1:k(i+1),k(i)+1:k(i+1))* # WHERE TO GET THIS? # B(1:2999,1:2999)
					U(k(i)+1:k(i+1),n).* # U_j # U(1:2999,n)
					 (.5*(1-lambda1(k(i)+1:k(i+1))*delt./delx(k(i)+1:k(i+1)))); # (1/2)*(1 - (u+c)_j * dt/dx)
					#(.5*(1-lambda1(1:2999)*delt./delx(1:2999)))
					#(.5*(1-(U(1:2999,2)+c)*delt./delx(1:2999)))
				# uL(2:3000,n) = U(1:2999,n) + B(1:2999,1:2999)*U(1:2999,n).*(.5*(1-(U(1:2999,2)+c)*delt./delx(1:2999)))
				# uL(2,n) = U(1,n) + B(1,1)*U(1,n).*(.5*(1-(U(1,2)+c)*delt./delx(1)))
				
				uR(k(i)+i:k(i+1)-1+i,n)= # uR(1:2999,n)
					U(k(i)+1:k(i+1),n)- # U_(j+1) # U(1:2999,n)
					B(k(i)+1:k(i+1),k(i)+1:k(i+1))* # B(1:2999,1:2999)
					U(k(i)+1:k(i+1),n).* # U_(j+1) # U(1:2999,n).
					 (.5*(1+lambda2(k(i)+1:k(i+1))*delt./delx(k(i)+1:k(i+1)))); # (1/2)*(1 - (u-c)_j+1 * dt/dx)
					#(.5*(1+lambda2(1:2999)*delt./delx(1:2999)))
					#(.5*(1+(U(1:2999,2)-c)*delt./delx(1:2999)))
				# uR(1:2999,n) = U(1:2999,n) - B(1:2999,1:2999)*U(1:2999,n).*(.5*(1+(U(1:2999,2)-c)*delt./delx(1:2999)))
				# uR(1,n) = U(1,n) - B(1,1)*U(1,n).*(.5*(1+(U(1,2)-c)*delt./delx(1)))
			end
	    end	
		

from stencil_kernel import *
from stencil_grid import *
from numpy import pi	

class MyKernel(StencilKernel):
	def kernel(self, node_tuple_ingrid, edge_interface_outgrid):
		for x in edge_interface_outgrid.interior_points():
			for y in node_tuple_ingrid.neighbors(x, -1):
					edge_interface_outgrid[x] = node_tuple_ingrid[y]



if __name__ == '__main__':
	# %This is the main blood-flow function
	# 
	# 
	# %MAIN - Calculates Blood Flow properties in Time for a Circle of Willis 
	# 
	# %Inputs: Skeleton Point Array (index,x-y-z position,type of cell)
	# %        Line Segment Array   (segment index,point indices,artery index) 
	# 
	# %Output: U is an array containing the flow variables for the system
	# 
	# function [U,Ainit] = bloodmain (Q0)
	# 
	# 
	# 
	# %NEWGRIDGEN - Takes output from image processing and creates cells for
	# %          numerical usage
	# 
	# %Output: domain (jx4 array containing local index,artery index, length of 
	# %                cell, & radii)
	# 
	# %        boundary (cell array containing connected nodes and an element
	# %                  that describes the type of boundary to be applied)
	# 
	# %        k (array containing the numbers of the global cells at the end of 
	# %           each artery)
	# 
	# %TEST FUNCTION
	# p1=[0 0 0 0.001];
	# p2=[1500 1500 1500 0.003];
	# p3=[0 3000 3000 0.002];
	# p4=[3000 3000 0 0.001];
	# n12=3000;
	# n23=3000;
	# n24=3000;
	# [skel,seg]=HA_datacreate();
	# % [skel,seg]=HA_datacreate(p1,p2,p3,p4,n12,n23,n24);

	# 
	# [domain,k] = newgridgen(skel,seg);
	# boundary = dataconv(skel,seg);
	# bond=size(boundary);


	# %INITIALIZE CONSTANTS
	u0 = 0             # %Initial Inflow Velocity [M/s]
	p0 = 0             # %Initial Internal Pressure [Pa]
	pout = 666.4       # %Venous Pressure [Pa]
	tmax = 5           # %Total time of virtual simulation [s]
	rho = 1050         # %Blood Density [kg/m^3]
	mu = 0.0045        # %Blood Viscosity [kg/M*s]
	E = 1200000        # %Blood Vessel Elastic Modulus [Pa]

	# %INITIALIZE FLOW-VARIABLES
	# %U=area,velocity,pressire
	U=datast(domain);
	U=pi*U.*U;
	# %f=zeros(length(U),1);

	# %Initial Frictional Drag (check equation)
	f=-22*mu*pi*U(:,2);

	# %c=wave speed
	c=zeros(length(U),1);

	# %t=thickness (assume to be 25% R)
	h=0.25*(1/pi)*sqrt(U(:,1));

	# %betas=stiffness measure
	betas=(4/3)*sqrt(pi)*E*h;

	# %Ainit=initial cross-sectional areas
	Ainit=U(:,1);

	# %B=Finite Difference Matrix
	B=sparse(fdiff(domain));



	# %INITIALIZE INTERFACE VALUES
	# %Left-state
	uL=zeros(length(domain)+length(k)-1,3);

	# %Right-state
	uR=zeros(length(domain)+length(k)-1,3);

	# %Intermediate-state
	uI=zeros(length(domain)+length(k)-1,3);

	# %cstar=wave-speeds
	cstar=zeros(length(domain)+length(k)-1,length(domain)+length(k)-1);

	# %hstar=thickness
	hstar=zeros(length(domain)+length(k)-1,1);

	# %betastar=stiffness measures
	betastar=zeros(length(domain)+length(k)-1,1);

	# %Ainitstar=initial areas
	Ainitstar=zeros(length(domain)+length(k)-1,1);


	# %CALCULATE SOME INITIAL INTERFACE VALUES
	# %Ainitstar
	[radstar]=areainitial(skel,seg);

	Ainitstar=pi*radstar.*radstar;
	A=Ainitstar;

	hstar=0.25*(1/pi)*Ainitstar.^.5;

	betastar=(4/3)*sqrt(pi)*E*hstar;

	# %STEP-SIZES
	delx=domain(:,4);

	delt=max(delx./(2*sqrt(E*h./(2*rho*Ainit)).*U(:,1).^.25));

	t=delt;

	
	
	
######	
	
	kernel = MyKernel()
	domain_length = 10
	# using 1D grids
	uL = StencilGrid([domain_length])
	uR = StencilGrid([domain_length])
	uI = StencilGrid([domain_length])
	
	
	# fill in_grid interior points with ones	
	for x in in_grid.interior_points():
		print x
		in_grid[x] = in_grid[x] + 1
		

	
	kernel.pure_python = True
	
	print in_grid.data
	for i in range(10):
		kernel.kernel(in_grid, out_grid)
		print out_grid.data