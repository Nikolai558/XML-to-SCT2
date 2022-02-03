import json

BLANK_COORDS = "N000.00.00.000 E000.00.00.000 N000.00.00.000 E000.00.00.000 RestrictedRed"

HEADER = """#define RestrictedRed 128

[INFO]
ZLC AIRAC 2201
SLC_33_CTR
KSLC
N043.31.08.418
W112.03.50.103
60.043
43.536
-11.8
1.000

[SID]
"""


def dd2dms(decimal_deg, islon):
    """
    Convert Decimal into SCT2 DMS format.

    :param decimal_deg: deg decimal 48.1515446
    :param islon: bool is longitude
    :return: dms format
    """
    d = int(decimal_deg)
    md = abs(decimal_deg - d) * 60
    m = int(md)
    sd = (md - m) * 60
    sd = round(sd, 3)

    formated_sd = str(int(sd)).zfill(2)
    try:
        formated_sd = formated_sd + "." + '{:<03d}'.format(int(str(sd).split('.')[1]))
    except IndexError:
        print(F"***************** {decimal_deg} {islon} ******************")
        formated_sd = formated_sd + "." + "000"

    if islon:
        if d >= 0:
            d = "E" + str(d).zfill(3)
        else:
            d = "W" + str(d)[1:].zfill(3)
    else:
        if d >= 0:
            d = "N" + str(d).zfill(3)
        else:
            d = "S" + str(d)[1:].zfill(3)

    return [str(d), str(m).zfill(2), formated_sd]


def dms2dd(dms_deg):
    """
    Convert a DMS to Decimal.

    :param dms_deg: full DMS (N60.58.58.110)
    :return: Decimal Format
    """
    direction = dms_deg[0]
    degrees = dms_deg.split('.')[0][1:]
    minutes = dms_deg.split('.')[1]
    seconds = ".".join(dms_deg.split('.')[2:])

    dd = float(degrees) + float(minutes) / 60 + float(seconds) / (60 * 60)
    if direction == 'W' or direction == 'S':
        dd *= -1

    dd = round(dd, 6)
    return dd


def convertXML(full_file_path):
    """
    Convert a XML file to SCT2 Files.

    :param full_file_path: full file path for xml file.
    :return: nothing.
    """
    with open(full_file_path, 'r') as xml_file:
        xml_lines = xml_file.readlines()

    with open('xml_converted_output.sct2', 'w') as output_file:
        with open('log.txt', 'w') as logFile:
            output_file.write(HEADER)
            for line in xml_lines:
                if "Description=" in line:
                    name = line[line.index("Description=\"") + len("Description=\""):].split('"')[0]
                    output_file.write(name + (' ' * (26 - len(name))) + BLANK_COORDS + "\n")

                if "type=\"Line\"" in line:
                    # logFile.write("\n"+line.strip()+'\n')

                    startLat = float(line[line.index("StartLat=\"") + len("StartLat=\""):].split('"')[0])
                    logFile.write(f'\t StartLat: {startLat} -> ')
                    startLat = ".".join(dd2dms(startLat, False))
                    logFile.write(f'{startLat}\n')

                    startLon = float(line[line.index("StartLon=\"") + len("StartLon=\""):].split('"')[0])
                    logFile.write(f'\t StartLon: {startLon} -> ')
                    startLon = ".".join(dd2dms(startLon, True))
                    logFile.write(f'{startLon}\n')

                    endLat = float(line[line.index("EndLat=\"") + len("EndLat=\""):].split('"')[0])
                    logFile.write(f'\t EndLat: {endLat} -> ')
                    endLat = ".".join(dd2dms(endLat, False))
                    logFile.write(f'{endLat}\n')

                    endLon = float(line[line.index("EndLon=\"") + len("EndLon=\""):].split('"')[0])
                    logFile.write(f'\t EndLon: {endLon} -> ')
                    endLon = ".".join(dd2dms(endLon, True))
                    logFile.write(f'{endLon}\n')
                    logFile.write((' ' * 26) + f"{startLat} {startLon} " + f"{endLat} {endLon} " + "RestrictedRed\n")

                    output_file.write(
                        (' ' * 26) +
                        f"{startLat} {startLon} " +
                        f"{endLat} {endLon} " +
                        "RestrictedRed\n")


def convert_from_geojson(full_file_path='geojson.json'):
    """
    Convert a geojson to SCT2 File.
    Can be downloaded from: https://github.com/maiuswong/simaware-tracon-project/blob/main/TRACONBoundaries.geojson

    :param full_file_path: full file path for geojson.json file
    :return: nothing.
    """
    file = open(full_file_path, 'r')

    data = json.load(file)
    counter = 0
    all_options = "ALL" + (' ' * (26 - len("ALL"))) + BLANK_COORDS + "\n"
    with open('output.sct2', 'w') as outFile:
        outFile.write(HEADER)
        for features in data["features"]:
            counter += 1
            name = features['properties']['id'] + features['properties']['prefix'][0] + str(counter)

            outFile.write(name + (' ' * (26 - len(name))) + BLANK_COORDS + "\n")
            previous = ''

            if features['geometry']["coordinates"][0][0][0] != features['geometry']["coordinates"][0][0][-1]:
                features['geometry']["coordinates"][0][0].append(features['geometry']["coordinates"][0][0][0])

            for coordinate in features['geometry']["coordinates"][0][0]:
                if previous != '':
                    outFile.write(
                        (' ' * 26) +
                        previous +
                        F" {'.'.join(dd2dms(coordinate[1], False))} {'.'.join(dd2dms(coordinate[0], True))} " +
                        "RestrictedRed\n")
                    all_options += (' ' * 26) + \
                                   previous + \
                                   F" {'.'.join(dd2dms(coordinate[1], False))}" \
                                   F" {'.'.join(dd2dms(coordinate[0], True))} " +\
                                   "RestrictedRed\n"
                previous = F"{'.'.join(dd2dms(coordinate[1], False))} {'.'.join(dd2dms(coordinate[0], True))}"
        outFile.write(all_options)

    file.close()
