from webkernel import LineKernel
from asp import _asp_declare

class InterfaceLineKernel(LineKernel):
    """A line stencil that runs over a line of nodes."""

    def kernel(self, in_grid, out_grid):
        # must declare the variables before using them.
        #should eventually analyze code statically and automatically do this.
        _asp_declare('double', 'delt')
        _asp_declare('double', 'delx')
        _asp_declare('double', 'Ainitstar')
        _asp_declare('double', 'betastar')
        _asp_declare('double', 'rho')
        _asp_declare('double', 'c')
        _asp_declare('double', 'cstar')
        delt = 1.0
        delx = 2.0
        Ainitstar = 3.0
        betastar = 4.0
        rho = 5.0
        c = 6.0
        cstar = 7.0
        
        
        # declare the temporary uL/uR values
        _asp_declare('double', 'uL_A')
        _asp_declare('double', 'uL_u')
        _asp_declare('double', 'uL_p')
        _asp_declare('double', 'uR_A')
        _asp_declare('double', 'uR_u')
        _asp_declare('double', 'uR_p')
        # lambda1=U(:,2)+c;
        # lambda2=U(:,2)-c;
        for x in out_grid.interior_points():
            for y in in_grid.neighbors(x, 1):
                # Strategy: calculate all uL,uR values, and use them to
                # calculate the uI output values

                # uL(2,n) = U(1,n) + B(1,1)*U(1,n).*(.5*(1-(U(1,2)+c)*delt./delx(1)))
                # Shift the point over by 1 since the output interface line has
                # a ghost depth of 2.
                # FIXME: ASP doesn't like this...yet.
                # y = tuple(i - 1 for i in y)

                uL_A = (in_grid[y].A + in_grid[y].A *
                        (0.5 * (1 - in_grid[y].A + c) * delt / delx))
                uL_u = (in_grid[y].u + in_grid[y].u *
                        (0.5 * (1 - in_grid[y].u + c) * delt / delx))
                uL_p = (in_grid[y].p + in_grid[y].p *
                        (0.5 * (1 - in_grid[y].p + c) * delt / delx))

                # uR(1,n) = U(1,n) - B(1,1)*U(1,n).*(.5*(1+(U(1,2)-c)*delt./delx(1)))
                uR_A = (in_grid[y].A + in_grid[y].A *
                        (0.5 * (1 + in_grid[y].A - c) * delt / delx))
                uR_u = (in_grid[y].u + in_grid[y].u *
                        (0.5 * (1 + in_grid[y].u - c) * delt / delx))
                uR_p = (in_grid[y].p + in_grid[y].p *
                        (0.5 * (1 + in_grid[y].p - c) * delt / delx))

                # uI(:,1)=(uI(:,3).*Ainitstar./betastar+Ainitstar.^.5).^2;
                out_grid[x].A = pow(out_grid[x].p * Ainitstar / betastar +
                                    sqrt(Ainitstar), 2)
                
                # uI(:,2)=(1./(2*rho*cstar)).*(uL(:,3)-uR(:,3))+0.5*(uL(:,2)+uR(:,2));
                out_grid[x].u = (1.0 / (2 * rho * cstar) *
                                 (uL_p - uR_p) + 0.5 * (uL_u + uR_p))

                # uI(:,3)=.5*(uL(:,3)+uR(:,3))+.5*rho*cstar.*(uL(:,2)-uR(:,2));
                out_grid[x].p = (0.5 * (uL_p + uR_p) +
                                 0.5 * rho * cstar * (uL_u - uR_u))

