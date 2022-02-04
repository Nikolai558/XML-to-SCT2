import json
from pyperclip import copy

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


def dd2dms(decimal_deg: float, islon: bool) -> str:
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

    formatted_sd = str(int(sd)).zfill(2)
    try:
        formatted_sd = formatted_sd + "." + '{:<03d}'.format(int(str(sd).split('.')[1]))
    except IndexError:
        print(F"***************** {decimal_deg} {islon} ******************")
        formatted_sd = formatted_sd + "." + "000"

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

    # return [str(d), str(m).zfill(2), formatted_sd]
    return '{}.{}.{}'.format(str(d), str(m).zfill(2), formatted_sd)


def dms2dd(dms_deg: str) -> float:
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


def convert_xml_file(xml_file_path: str, out_file_path: str = "xml_converted_output.sct2") -> None:
    """
    Convert an XML file to SCT2 Files.

    :param out_file_path: output file path for the created sct2 file.
    :param xml_file_path: full file path for xml file.
    :return: nothing.
    """
    with open(xml_file_path, 'r') as xml_file:
        xml_lines = xml_file.readlines()

    with open(out_file_path, 'w') as output_file:
        output_file.write(HEADER)
        for line in xml_lines:
            if "Description=" in line:
                name = line[line.index("Description=\"") + len("Description=\""):].split('"')[0]
                output_file.write(name + (' ' * (26 - len(name))) + BLANK_COORDS + "\n")

            if "type=\"Line\"" in line:
                start_lat = float(line[line.index("StartLat=\"") + len("StartLat=\""):].split('"')[0])
                start_lat = dd2dms(start_lat, False)

                start_lon = float(line[line.index("StartLon=\"") + len("StartLon=\""):].split('"')[0])
                start_lon = dd2dms(start_lon, True)

                end_lat = float(line[line.index("EndLat=\"") + len("EndLat=\""):].split('"')[0])
                end_lat = dd2dms(end_lat, False)

                end_lon = float(line[line.index("EndLon=\"") + len("EndLon=\""):].split('"')[0])
                end_lon = dd2dms(end_lon, True)

                output_file.write(
                    (' ' * 26) +
                    f"{start_lat} {start_lon} " +
                    f"{end_lat} {end_lon} " +
                    "RestrictedRed\n")


def convert_from_geojson(full_file_path: str = 'geojson.json') -> None:
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
                                   F" {'.'.join(dd2dms(coordinate[0], True))} " + \
                                   "RestrictedRed\n"
                previous = F"{'.'.join(dd2dms(coordinate[1], False))} {'.'.join(dd2dms(coordinate[0], True))}"
        outFile.write(all_options)

    file.close()


def console_conversion():
    print("Convert Sector File Lat/Lon to Decimal")
    print("This program will copy the result to your clipboard.")
    print("Valid Formats are as follows: ")
    print("\tN045.49.43.012\n\tN045.49.43.012 W108.18.35.310\n"
          "\tN045.49.43.012 W108.18.35.310 N045.49.44.988 W108.18.38.587")
    print("----------------------------------------------------------------")
    while True:
        user_input = input("> ").strip()

        try:
            if len(user_input.split(' ')) == 2:
                first = dms2dd(user_input.split(' ')[0])
                second = dms2dd(user_input.split(' ')[1])
                copy(f"{first} {second}")
                print("Copied to clipboard: ", f"{first} {second}")
            elif len(user_input.split(' ')) == 4:
                first = dms2dd(user_input.split(' ')[0])
                second = dms2dd(user_input.split(' ')[1])
                third = dms2dd(user_input.split(' ')[2])
                fourth = dms2dd(user_input.split(' ')[3])
                copy(f"{first} {second} {third} {fourth}")
                print("Copied to clipboard: ", f"{first} {second} {third} {fourth}")
            elif len(user_input.split(' ')) == 1:
                decimal_format = dms2dd(user_input)
                copy(decimal_format)
                print("Copied to clipboard: ", str(decimal_format))
            else:
                print("Invalid Input: {}".format(user_input))
        except IndexError:
            print("Invalid Input: {}".format(user_input))
        except ValueError:
            print("Invalid Input: {}".format(user_input))


if __name__ == '__main__':
    pass
