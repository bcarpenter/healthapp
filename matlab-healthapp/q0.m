%A Functional Definition of an Initial Concentration

function q = q0(x,dx,amp)

x=x:dx:x+pi;

y=0:dx:pi;
a = @(y,amp) amp*sin(y);
q=a(y,amp);

plot(x,q);
axis([0 20 0 2])
pause(.1)

end