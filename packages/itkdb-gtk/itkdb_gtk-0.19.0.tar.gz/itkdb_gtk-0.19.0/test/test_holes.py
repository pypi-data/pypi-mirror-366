import random

# initialize
random.seed()

# module_param[iring][i_sensor][i_hybrid][i_row]
module_param = { 
    0: [
        [
            [[255, 830], [1343, 1918], [2431, 3006], [3519, 4094]],
            [[831, 1342], [1919, 2430], [3007, 3518], [4095, 4606]],
        ]
    ],
    1: [
        [
            [[271, 974], [1615, 2318], [2959, 3662], [4303, 5006]],
            [[975, 1614], [2319, 2958], [3663, 4302], [5007, 5646]],
        ]
    ],
    2: [
        [
            [[201, 968], [969, 1736], [1737, 2504], [2505, 3272]]
        ]
    ],
    3: [
        [
            [[566, 1013], [2358, 2805], [4150, 4597], [5942, 6389]],
            [[1462, 1909], [3254, 3701], [5046, 5493], [6838, 7285]]
        ],
        [
            [[1014, 1461], [2806, 3253], [4598, 5045], [6390, 6837]],
            [[1910, 2357], [3702, 4149], [5494, 5941], [7286, 7733]]
        ]
    ],
    4: [
        [
            [[318, 829], [1342, 1853], [2366, 2877], [3390, 3901]]
        ],
        [
            [[830, 1341], [1854, 2365], [2878, 3389], [3902, 4413]]
        ]
    ],
    5: [
        [
            [[332, 907], [1484, 2059], [2636, 3211], [3788, 4363]]
        ],
        [
            [[908, 1483], [2060, 2635], [3212, 3787], [4364, 4939]]
        ]
    ],
}


def wire2strip(mod_par, irow, iwire):
    """Convert from wirebond index to strip_number."""
    for isensor in mod_par:
        for ihyb in isensor:
            rng = ihyb[irow-1]
            if iwire>= rng[0] and iwire<=rng[1]:
                if irow % 2:
                    ichan = 2*(iwire-rng[0]) + 1
                else:
                    ichan = 2*(iwire-rng[0])
                    
                return ichan

    return None


def get_module_type(SN):
    """Get parameters of module type.

    Args:
        SN: Serial Number

    Returns:
        list: list with bond numbers.
    """
    if len(SN) != 14 or SN[:3]!="20U":
        raise ValueError("Wrong serial number {}".format(SN))
    
    if SN[3:5] != "SE":
        raise ValueError("Cannot handle barrel modules yet.")
    
    mod_type  = SN[5:7]
    if mod_type[0] != "M":
        raise ValueError("Does not seem to be a RingModule: {}".format(SN))

    ring = int(mod_type[-1])
    param = module_param[ring]

    return param



def find_holes(chan_list, max_chan=1e10):
    """Fidn groups of consecutive channels."""
    out = sorted(chan_list)
    nchan = 0
    last_chan = -1
    ichan = -1
    holes = []
    for chan in out:
        if last_chan < 0:
            last_chan = chan
            continue
        
        if chan - last_chan > 1:
            if nchan:
                holes.append([ichan, nchan])
            nchan = 0
            ichan = -1
        else:
            if last_chan < max_chan and chan >= max_chan:
                # WE are in another sensor
                holes.append([ichan, nchan])
                nchan = 0
                ichan = -1
                last_chan = chan
                continue
            
            nchan += 1
            if ichan < 0:
                ichan = last_chan
                nchan += 1
            
        last_chan = chan
    
    if nchan:
         holes.append([ichan, nchan])
    return holes


iring = random.randint(0, 5)
mod_par = module_param[iring]
nsensor = len(mod_par)
isensor = random.randint(0, nsensor-1)
nhyb = len(mod_par[0])
ihyb = random.randint(0, nhyb-1)

rng = mod_par[isensor][ihyb][0]
nchip = (rng[1]-rng[0]+1)/64
max_chan = 128 * nchip

segment = random.randint(0, 1)
nchan = random.randint(1, 10)
bonds = []
channels = []
rng = mod_par[isensor][ihyb]
for i in range(nchan):
    ichan = random.randint(0, max_chan-1)
    channels.append(ichan)
    if ichan % 1:
        irow = 1
    else:
        irow = 2
        
    irow += 2*segment
    ilow = rng[irow-1][0]
    ibond = int(ilow + ichan/2)
    
    jchan = wire2strip(mod_par, irow, ibond)
    bonds.append(jchan)

print(channels)
print(bonds)

SN = "20USEM00000040"
SN = "20USEM30000030"
mod_par = get_module_type(SN)
ichan = wire2strip(mod_par, 1, 334)

chan_list = [0, 3, 9, 20, 21, 22, 50, 60, 61, 62, 63, 64 ]
H = find_holes(chan_list, 62)
print(H)
