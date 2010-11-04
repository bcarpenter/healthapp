%This function makes a finite difference matrix for the entirety of the
%domain input. The method is central difference except at the initial and
%final nodes of each vessel; it is a simple upwind there.


function [B] = fdiff(domain)
B=zeros(length(domain),length(domain));

i=1;
k=0;

while k<1
    
    if or(domain(i,1)==1,not(eq(domain(i,2),domain(i+1,2))))
        
        if domain(i,1)==1
            
            B(i,i)=-1;
            B(i,i+1)=1;
            
        end
        
        if not(eq(domain(i,2),domain(i+1,2)))
            
            B(i,i)=1;
            B(i,i-1)=-1;
            
        end
        
    else
        
        B(i,i-1)=-1/2;
        B(i,i+1)=1/2;
    end
    
    i=i+1;
    if i==length(domain)
        B(i,i)=1;
        B(i,i-1)=-1;
        k=1;
    end 
    
end

end