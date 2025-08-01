#!/usr/bin/env python3
"""A collection of utilities for sensor data."""
from pathlib import Path
import warnings
import numpy as np
from itkdb_gtk import ITkDButils

#
#   The following is taken from
#   https://gitlab.cern.ch/atlas-itk/sw/db/production_database_scripts.git
#
mm = 1e-3
cm = 1e-2
UpperV = 500  # For sensor to pass, I must be < Imax up until this voltage and no breakdown must be detected before then.
StabilityV = 700  # Voltage with multiple current readings to check stability

AreaDict = {
    "Unknown": (97.621 - 0.450) * (97.950 - 0.550) * mm * mm,
    #
    "ATLAS12": 95.7 * 95.64 * mm * mm,
    "ATLAS17LS": (97.621 - 0.450) * (97.950 - 0.550) * mm * mm,
    #
    "ATLAS18R0": 89.9031 * cm * cm,
    "ATLAS18R1": 89.0575 * cm * cm,
    "ATLAS18R2": 74.1855 * cm * cm,
    "ATLAS18R3": 80.1679 * cm * cm,
    "ATLAS18R4": 87.4507 * cm * cm,
    "ATLAS18R5": 91.1268 * cm * cm,
    #
    "ATLAS18SS": 93.6269 * cm * cm,
    "ATLAS18LS": 93.6269 * cm * cm,
    #
    "ATLASDUMMY18": (97.621 - 0.450) * (97.950 - 0.550) * mm * mm,
}


NO_BD_CONST = 9.99e99

def LocateMicroDischarge(
    I,
    V,
    sm_window=2,
    bd_limit=5.5,
    allow_running_bd=True,
    use_additional_cond=False,
    tolerence=0.05,
    voltage_span=4,
    fit_window=5,
):
    """
    Function for BDV estimation - if questions please contact Vera Latonova (vera.latonova@cern.ch).
    I,V must have same shape and voltages must be in ascending order,
    same indexes of I&V arrays must correspond each other,
    only invalid data or holdstep should be stripped before
    but it is not necessary. Measurments U=0&I=0 are removed.
    If there is same or higher amount of same voltages in row than
    sm_window, from this sequence we cannot estimete dI/dV and
    we have to remove this averaged point.

    It is assumed that only parameter use_additional_cond would be
    changed by caller. Changing of other parameters may affect
    BDV unexpectedly.


    @param[in] I                   - array of currents without any cut
    @param[in] V                   - array of voltages, ascending order, without any cut
    @param[in] sm_window           - size of smoothing window
    @param[in] bd_limit            - BD limit for |U| < 500V
    @param[in] allow_running_bd    - allow increase bd_limit for |U| > 500
    @param[in] use_additional_cond - use additional BD contition
    @param[in] tolerence           - configuration of additional condition
    @param[in] voltage_span        - max width of hump on spectra which may be neglected
                                     in voltage steps in additional contition
    @param[in] fit_window          - number of points used for linear fit before BD voltage

    @return BD voltage (always positive) or NO_BD_CONST = 9.99e99 if not found.
    """

    # add nan to the end of array
    V = np.abs(V)
    I = np.abs(I)

    # skip zeros
    ind = np.where(np.logical_or(I != 0, V != 0))
    V = V[ind]
    I = I[ind]

    V_ = np.append(V, np.nan * np.ones(sm_window - 1))
    I_ = np.append(I, np.nan * np.ones(sm_window - 1))

    # make 2D array of I's, V's each row_ind shifted by row_ind index
    # i.e from array [1,3,5] we make (for sm_window=2) 2D array
    # [  1,3,5,nan]
    # [nan,5,1,3]
    # than get average from each column -> I_avg, V_avg
    r = np.arange(sm_window)

    V2 = np.outer(np.ones(sm_window), V_)
    row_ind, col_ind = np.ogrid[: V2.shape[0], : V2.shape[1]]
    col_ind = col_ind - r[:, np.newaxis]
    V2 = V2[row_ind, col_ind]
    # strip fields with nans
    V2 = np.transpose(V2[:, (sm_window - 1) : -(sm_window - 1)])

    I2 = np.outer(np.ones(sm_window), I_)
    row_ind, col_ind = np.ogrid[: I2.shape[0], : I2.shape[1]]
    col_ind = col_ind - r[:, np.newaxis]
    I2 = I2[row_ind, col_ind]
    I2 = np.transpose(I2[:, (sm_window - 1) : -(sm_window - 1)])

    # get V & I averages
    try:
        V_avg = np.average(V2, axis=1)
        I_avg = np.average(I2, axis=1)
    except ZeroDivisionError:
        # not enough data
        return NO_BD_CONST

    # find dI / dV array
    # I'm not able to write this without cycle
    dIdV = np.array([])
    for i in range(V2.shape[0]):
        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            try:
                dIdV = np.append(dIdV, np.polyfit(V2[i, :], I2[i, :], 1)[0])
            except (np.RankWarning, TypeError):
                dIdV = np.append(dIdV, np.nan)

    # stripping U[n] == U[n+1] (i.e. hodlsetp) => fit cannot be sucessful =>
    # dIdV is nan @holdstep
    ind = np.where(np.isfinite(dIdV))
    I_avg = I_avg[ind]
    V_avg = V_avg[ind]
    dIdV = dIdV[ind]

    # get running BDV limit & compare
    bd_limit_running = bd_limit + np.where(
        allow_running_bd and V_avg > 500, (V_avg - 500.0) / 100.0, 0
    )
    V_avg_BD_ind = dIdV / (I_avg / V_avg) > bd_limit_running
    V_avg_BD = V_avg[V_avg_BD_ind]

    # Estimate BDV
    BDV = np.array([])

    # no break-down
    if V_avg_BD.shape == (0,):
        return NO_BD_CONST

    # if V_avg_BD_ind[0] == True ... BDV <- V[0]
    # for others V_avg_BD_ind[n] == True BDV <- (V_avg[n] + V_avg[n-1])/2
    if V_avg_BD_ind[0]:
        BDV = np.append(BDV, V[0])
    V_avg_BD_ind[0] = False

    BDV = np.append(
        BDV,
        (V_avg[np.where(V_avg_BD_ind)] + V_avg[np.where(V_avg_BD_ind)[0] - 1]) / 2.0,
    )

    ###########################################################################
    ## Application of additional condition ####################################
    ###########################################################################
    if not use_additional_cond:
        return BDV[0]

    # get index if V <= BDV
    B = np.where(np.less.outer(BDV, V))
    col_ind = np.mgrid[: BDV.shape[0], : V.shape[0]][1]
    col_ind[B[0], B[1]] = 0
    V_BDV_ind = np.max(col_ind, axis=1)

    back_ok_v_ind = 0
    while True:
        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            try:
                a, b = np.polyfit(
                    V[
                        max(back_ok_v_ind, V_BDV_ind[0] - fit_window) : max(
                            back_ok_v_ind, V_BDV_ind[0]
                        )
                    ],
                    I[
                        max(back_ok_v_ind, V_BDV_ind[0] - fit_window) : max(
                            back_ok_v_ind, V_BDV_ind[0]
                        )
                    ],
                    1,
                )
            except (np.RankWarning, TypeError):
                return BDV[0]

        ind = np.where(1 - (a * V + b) / I <= tolerence)[0]
        try:
            back_ok_v_ind = np.min(ind[ind > V_BDV_ind[0] + 1])
        except ValueError:
            # sensor is not going back
            return BDV[0]
        # hump is too long -- it cannot be skipped
        if back_ok_v_ind - V_BDV_ind[0] > voltage_span:
            return BDV[0]

        # skip BDVs inside hump
        ind = BDV >= V[back_ok_v_ind]
        BDV = BDV[ind]
        V_BDV_ind = V_BDV_ind[ind]
        if V_avg_BD.shape == (0,):
            return NO_BD_CONST

    return NO_BD_CONST


def scale_iv(I, T1, T2):
    """Normalize corrent  to given temperature (T2)

    Args:
        I (array): Current
        T1 (float): Original temperature
        T2 (float): New temperature.

    Return:
        Array with scaled currents.

    """
    factor = (T2 / T1) ** 2 * np.exp((-1.21 / 8.62) * (1 / T2 - 1 / T1))
    return factor * I


def sensor_data_to_json(session, mdata, mod_type, logger=None):
    """Read a Sensor data file and return the corresponding JSon for hte PDB.

    Args:
        mdata: Data as returned by :function:`read_sensor_file`.
        logger: an object that writes messages via a write_message method
    """
    # Check if we are dealing with sensors or modules
    is_module = "Module_SN" in mdata

    if is_module:
        test = ITkDButils.get_test_skeleton(session, "MODULE", mdata["TestType"])
        tp = "ATLAS18{}".format(mod_type[0:2])
        area = AreaDict[tp] / cm**2
        SN = mdata["Module_SN"]

    else:
        test = ITkDButils.get_test_skeleton(session, "SENSOR", mdata["TestType"])
        area = AreaDict[mod_type] / cm**2
        SN = mdata["Component"]

    if logger:
        logger.write_message("Analyzing {}\n".format(SN))

    # The data arrays
    V = np.abs(mdata["curve"]["V"])
    I = np.abs(mdata["curve"]["I"])
    passed = True

    # Find Current @ 500V
    try:
        indx = np.where(V == 500)[0]
        i_500 = I[indx][0] / area
    except IndexError:
        i_500 = 999

    if logger:
        logger.write_message("I @ 500V = {:.2f} nA/cm2\n".format(i_500))

    # Compute current stability
    IStability = abs(I[abs(V) == StabilityV])
    IVariation = -1
    if np.size(IStability) > 1:  # Maybe make == 4?
        IVariation = abs(np.std(IStability) / np.mean(IStability))

    if logger:
        logger.write_message("I stability = {:.6f} nA\n".format(IVariation))

    # Search for Micro discharges
    # Check for micro-discharge in non-normalized current,
    # removing duplicate Voltage entries (e.g. for stability measurements)
    comments = []
    defects = []
    UniqueVs, UniqueIndices = np.unique(V, return_index=True)
    MicroDischargeV = LocateMicroDischarge(I[UniqueIndices], UniqueVs)
    if MicroDischargeV < np.max(V):
        comments.append("Found micro discharge: {:.1f} V\n".format(MicroDischargeV))
        if logger:
            logger.write_message(comments[-1])

        if MicroDischargeV < UpperV:
            txt = "microdischarge happening before {:.1f}V.".format(UpperV)
            defects.append({
                        "name": "MicroDischarge",
                        "description": txt,
                        "properties": {}
                    }
            )
            if logger:
                logger.write_message("...{}. FAILED\n".format(txt))

            passed = False
    else:
        if MicroDischargeV == NO_BD_CONST:
            MicroDischargeV = 700.0

    test["component"] = SN
    test["institution"] = mdata["Institute"]
    test["runNumber"] = mdata["RunNumber"]
    test["date"] = ITkDButils.get_db_date(
        "{} {}".format(mdata["Date"], mdata["Time"])
    )
    test["passed"] = passed
    test["problems"] = False
    test["properties"]["VBIAS_SMU"] = mdata["Vbias_SMU"]
    test["properties"]["RSERIES"] = mdata["Rseries"]
    test["properties"]["TEST_DMM"] = mdata["Test_DMM"]
    test["properties"]["RSHUNT"] = mdata["Rshunt"]
    test["properties"]["RUNNUMBER"] = mdata["RunNumber"]
    test["properties"]["COMMENTS"] = mdata["Comments"]
    test["properties"]["ALGORITHM_VERSION"] = "0.0.0"
    if is_module:
        test["properties"]["SOFTWARE_TYPE_VERSION"] = "pyProbe"
        test["properties"]["MODULE_STAGE"] = mdata["Module_Stage"]

    test["results"]["TEMPERATURE"] = mdata["Temperature"]
    test["results"]["HUMIDITY"] = mdata["Humidity"]
    test["results"]["VBD"] = MicroDischargeV
    test["results"]["I_500V"] = i_500
    test["results"]["VOLTAGE"] = -np.abs(V)
    test["results"]["CURRENT"] = -np.abs(I)
    test["results"]["RMS_STABILITY"] = IVariation
    test["results"]["SHUNT_VOLTAGE"] = np.zeros(V.shape)
    test["defects"] = defects
    test["comments"] = comments

    return test


def read_sensor_file(fnam):
    """Read a data file. Return dictionary with all teh data."""
    labels = []
    metadata = {}
    with open(fnam, "r", encoding="utf-8") as ifile:
        first = True
        for line in ifile:
            if first:
                first = False
                ipos = line.rfind(".")
                metadata["fname"] = line[:ipos]
                continue

            if line.find("Voltage [V]") >= 0 or line.find("Voltage[V]") >= 0:
                labels = line.split("\t")
                break

            rc = line.find(":")
            if rc >= 0:
                key = line[:rc].strip()
                val = line[rc + 1 :].strip()
                if key in ["Temperature", "Humidity"]:
                    metadata[key] = float(val)
                else:
                    metadata[key] = val

        V = []
        I = []
        S = []
        for line in ifile:
            data = [float(s) for s in line.split()]
            V.append(data[0])
            I.append(data[1])
            try:
                S.append(data[2])
            except IndexError:
                S.append(0.0)

        metadata["curve"] = {
            "V": np.abs(np.array(V)),
            "I": np.abs(np.array(I)),
            "S": np.abs(np.array(S)),
            "labels": labels,
        }
        return metadata


def save_sensor_data(fnam, mdata, name=None):
    """Save sensor dat in file with the proper format.

    Args:
        fnam: file name or file object.
        mdata (dict): data as returned by :function:`read_sensor_file`

    """
    if hasattr(fnam, "write") and callable(fnam.write):
        data_out = fnam
        if name:
            fnam = name
        else:
            fnam = build_file_name(mdata)

    else:
        data_out = open(fnam, 'w', encoding="utf-8")
        fnam = Path(fnam).name

    is_module = "Module_SN" in mdata
    if is_module:
        SN = mdata["Module_SN"]
    else:
        SN = mdata["Component"]

    if is_module:
        items = [
            "Type",
            "Wafer",
            "Module_SN",
            "Module_Stage",
            "Date",
            "Time",
            "Institute",
            "TestType",
            "Vbias_SMU",
            "Rseries",
            "Test_DMM",
            "Rshunt",
            "Software type and version, fw version",
            "RunNumber",
            "Temperature",
            "Humidity",
            "Comments",
        ]
    else:
        items = [
            "Type",
            "Batch",
            "Wafer",
            "Component",
            "Date",
            "Time",
            "Institute",
            "TestType",
            "Vbias_SMU",
            "Rseries",
            "Test_DMM",
            "Rshunt",
            "RunNumber",
            "Temperature",
            "Humidity",
            "Comments",
        ]

    data_out.write("{}\n".format(fnam))
    for key in items:
        if key == "Module_SN" or key == "Component":
            data_out.write("{}: {}\n".format(key, SN))
        else:
            data_out.write("{}: {}\n".format(key, mdata[key]))

    labels = [lbl for lbl in mdata["curve"]["labels"]]
    if len(labels) < 3:
        labels.append("Shunt_voltage [mV]")

    for il, label in enumerate(labels):
        if il:
            data_out.write("\t")
        data_out.write(label)
    data_out.write("\n")


    # The data arrays
    V = np.abs(mdata["curve"]["V"])
    I = np.abs(mdata["curve"]["I"])
    S = np.abs(mdata["curve"]["S"])

    ndata = len(V)
    for i in range(ndata):
        data_out.write("{:10.2f}\t{:10.2f}\t{:10.2f}\n".format(V[i], I[i], S[i]))

    print(data_out.name)
    data_out.close()

def build_file_name(mdata):
    """Create a file name from the data."""
    is_module = "Module_SN" in mdata
    if is_module:
        SN = mdata["Module_SN"]
        fnam = "{}_{}_IV_{}".format(SN, mdata["Module_Stage"], mdata["RunNumber"])
    else:
        SN = mdata["Component"]
        fnam = "{}-W{}_IV_{}".format(mdata["Batch"], mdata["Wafer"], mdata["RunNumber"])

    return fnam
