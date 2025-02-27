#!usr/bin/env python
"""
Class Intro Here..
"""

from cmath import pi
import math
import time
import datetime
from PyQt5.QtWidgets import QInputDialog
from sympy import symbols, Eq


class Profile:

    def __init__(self):
        # Identification Fields
        self.ID = None
        self.date = str(time.time())
        self.line = None
        self.track = None
        self.stationing = None
        self.equipment = None
        # Data Fields
        self.LEA = None
        self.REA = None
        self.SEA = None
        self.SEO = None
        self.SP = []
        self.envelope = None
        # Calculation Parameters
        self.inside = True
        self.a_division = True
        # Image placeholders
        self.im_inside = None
        self.im_outside = None

    def brAvailable(self):
        if self.LEA is None:
            return False
        if self.REA is None:
            return False
        return True

    def bendRadius(self):
        if self.brAvailable():
            # Inf. Radius Condition
            if self.LEA == 180.00 and self.REA == 0.00:
                return math.inf
            if self.inside:
                lx = 300 * math.cos(self.LEA * (pi / 180.0))
                ly = 300 * math.sin(self.LEA * (pi / 180.0))
                rx = 300 * math.cos(self.REA * (pi / 180.0))
                ry = 300 * math.sin(self.REA * (pi / 180.0))
                x, y, z = complex(0, 0), complex(lx, ly), complex(rx, ry)
                w = z - x
                w /= y - x
                c = (x - y) * (w - abs(w) ** 2) / 2j / w.imag - x
                return [abs(c + x) / 12.0, None]
            else:
                # !!!!!!!!NEED TO CONFIRM!!!!!!!!!
                lx = 600 * math.cos(self.LEA * (pi / 180.0))
                ly = 600 * math.sin(self.LEA * (pi / 180.0))
                rx = 600 * math.cos(self.REA * (pi / 180.0))
                ry = 600 * math.sin(self.REA * (pi / 180.0))
                # Left Radius
                l_slope = (ly / lx)
                l_slope_perp = -1 / l_slope
                lcy = l_slope_perp * (0 - (lx / 2)) + (ly / 2)
                lcx = 0
                lbr = math.sqrt(lcx ** 2 + lcy ** 2) / 12.0
                # Right Radius
                r_slope = (ry / rx)
                r_slope_perp = -1 / r_slope
                rcy = r_slope_perp * (0 - (rx / 2)) + (ry / 2)
                rcx = 0
                rbr = math.sqrt(rcx ** 2 + rcy ** 2) / 12.0
                return [lbr, rbr]
                # !!!!!!!!!!NEED TO CONFIRM!!!!!!!!!!!!!
        else:
            return None

    def centerExcess(self):
        if self.brAvailable():
            br = self.bendRadius()
            if None in br:
                br = br[0]
            else:
                br = min(br)
            if self.a_division:
                return 1944 / br
            else:
                return 4374 / br
        else:
            return 0.00

    def endExcess(self):
        if self.brAvailable():
            br = self.bendRadius()
            if None in br:
                br = br[0]
            else:
                br = min(br)
            if self.a_division:
                return 1512 / br
            else:
                return 2945 / br
        else:
            return 0.00

    def seAvailable(self):
        if self.SEA == None:
            return False
        if self.SEO == None:
            return False
        return True

    def scan_string(self):
        out_string = ""
        if len(self.SP) > 0:
            for point in self.SP:
                if out_string != "":
                    out_string += ", "
                out_string += f"{point[0]}|{point[1]}"
        else:
            out_string = "None"
        return out_string

    def generate_insert_query(self, table):
        if self.date is None:
            self.date = time.time()
        query_parameters = (self.date, self.line, self.track, self.stationing, int(self.inside), int(self.a_division),
                            self.LEA, self.REA, self.bendRadius(), self.centerExcess(), self.endExcess(),
                            self.SEA, self.scan_string(), self.im_inside, self.im_outside)
        this_query = f"INSERT INTO {table} (DATE, LINE, TRACK, STATIONING, INSIDE, A_DIVISION, LEA, REA, BR, CE," \
                     f" EE, SEA, SP, IM_INSIDE, IM_OUTSIDE) " \
                     f"VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
        return [this_query, query_parameters]

    def generate_update_query(self, table):
        query_parameters = (self.line, self.track, self.stationing, int(self.inside), int(self.a_division),
                            self.LEA, self.REA, self.bendRadius(), self.centerExcess(), self.endExcess(),
                            self.SEA, self.scan_string(), self.im_inside, self.im_outside, self.date)
        this_query = f"UPDATE {table} SET LINE=?, TRACK=?, STATIONING=?, INSIDE=?, A_DIVISION=?, LEA=?, REA=?, BR=?," \
                     f" CE=?, EE=?, SEA=?, SP=? IM_INSIDE=?, IM_OUTSIDE=?" \
                     f" WHERE DATE=?;"
        return [this_query, query_parameters]

    def bulk_data_upload(self, data):
        # Passes list of all data points, in same order as sql tables
        self.ID = data[0]
        self.date = data[1]
        self.line = data[2]
        self.track = data[3]
        self.stationing = data[4]
        self.inside = bool(data[5])
        self.a_division = bool(data[6])
        self.LEA = data[7]
        self.REA = data[8]
        self.SEA = data[12]
        self.im_inside = data[14]
        self.im_outside = data[15]
        sp_string = ""
        sp_string = data[13]
        if sp_string != "None":
            while sp_string != "":
                if "," in sp_string:
                    this_point = sp_string[0:sp_string.index(",")]
                    sp_string = sp_string[sp_string.index(",") + 1:]
                else:
                    this_point = sp_string
                    sp_string = ""
                br_index = this_point.index("|")
                this_x = float(this_point[0:br_index])
                this_y = float(this_point[br_index + 1:])
                self.SP.append([this_x, this_y])
        else:
            self.SP = []

    def get_timestamp(self):
        timestamp = datetime.datetime.fromtimestamp(float(self.date))
        timestamp = timestamp[0:timestamp.index(" ")]
        return timestamp

    def date_string(self):
        # Seconds since 1/1/70
        this_date = float(self.date)
        str_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(this_date))
        return str_date


