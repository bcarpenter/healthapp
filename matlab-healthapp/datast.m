function [U]=datast(domain)

%Pre-allocate U array
U=zeros(length(domain),3);

%Fill in initial U array

%Initial velocity and pressure taken to be zero
U(:,1)=domain(:,3);
     
end