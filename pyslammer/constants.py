# Constants for use in pyslammer

# Unit conversions
CMtoFT = 0.032808399
FTtoIN = 12.0
CMtoIN = CMtoFT * FTtoIN  # 0.393700787
PCFtoKNM3 = 6.3659  # lb/ft^3 to kN/m^3
KNM3toPCF = 6. # 6.3659
FTtoM = 0.3048
MtoFT = 3.2808399
FT3toIN3 = FTtoIN * FTtoIN * FTtoIN
MtoCM = 100
# M_TO_CM = 100
M3toCM3 = MtoCM * MtoCM * MtoCM

# Gravitational constant
G_EARTH = 9.80665 # Acceleration due to gravity (m/block_disp^2).
Gcmss = G_EARTH * MtoCM  # 980.665
Gftss = Gcmss * CMtoFT  # 32.1740486
Ginss = Gcmss * CMtoIN  # 386.088583



# perSec = 5
# interval = 1.0 / perSec