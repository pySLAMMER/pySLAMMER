# This file is in the public domain.

import math
from decimal import Decimal

class RigidBlock(Analysis):
    def SlammerRigorous(self, data, d, disp, mult, dualSlope, ta, unitMult):
        a = n = q = r = s = t = u = v = y = 0.0

        # dual slope calculations
        l = math.radians(ta)
        g = math.sin(l) * Gcmss * unitMult

        t = disp[0][1] * Gcmss * unitMult
        if dualSlope:
            t += g

        pos = 0  # position in the displacement/ca table
        prop = 0.0

        try:
            self.setValueSize(d)  # init the graphing data

            for i in range(len(data)):
                a = data[i] * mult * unitMult

                if dualSlope:
                    a += g

                if a == 0.0 and mult > 0.0:
                    self.store(u)
                    continue

                if abs(v) < 1e-15:
                    if abs(a) > t:
                        n = math.copysign(1, a)
                    else:
                        n = a / t
                else:
                    n = math.copysign(1, v)

                y = a - n * t
                v = r + d / 2.0 * (y + s)

                if (not dualSlope and v <= 0.0) or (dualSlope and (not (abs(r) < 1e-15 or (v / r) > 0.0))):
                    v = 0
                    y = 0

                u = q + d / 2.0 * (v + r)

                q = u
                r = v
                s = y

                self.store(u)

                # if we are at the end of the disp/ca table, don't bother doing anything else
                if pos == len(disp) - 1:
                    continue

                # figure out the new pos based on current displacement
                while u > disp[pos + 1][0]:
                    pos += 1
                    if pos == len(disp) - 1:
                        break

                if pos == len(disp) - 1:
                    t = Gcmss * unitMult * disp[pos][1]
                    if dualSlope:
                        t += g
                else:
                    prop = (u - disp[pos][0]) / (disp[pos + 1][0] - disp[pos][0])
                    t = Gcmss * unitMult * (disp[pos][1] - (disp[pos][1] - disp[pos + 1][1]) * prop)
                    if dualSlope:
                        t += g

        except Exception:
            pass

        self.end(u)
        return u

