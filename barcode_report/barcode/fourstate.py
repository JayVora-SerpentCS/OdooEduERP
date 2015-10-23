# -*- encoding: UTF-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Serpent Consulting Services PVT. LTD.
#    (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

_rm_patterns = {"0": "--||", "1": "-',|", "2": "-'|,", "3": "'-,|",
                "4": "'-|,", "5": "'',,", "6": "-,'|", "7": "-|-|",
                "8": "-|',", "9": "',-|", "A": "',',", "B": "'|-,",
                "C": "-,|'", "D": "-|,'", "E": "-||-", "F": "',,'",
                "G": "',|-", "H": "'|,-", "I": ",-'|", "J": ",'-|",
                "K": ",'',", "L": "|--|", "M": "|-',", "N": "|'-,",
                "O": ",-|'", "P": ",','", "Q": ",'|-", "R": "|-,'",
                "S": "|-|-", "T": "|',-", "U": ",,''", "V": ",|-'",
                "W": ",|'-", "X": "|,-'", "Y": "|,'-", "Z": "||--",
                "(": "'-,'", ")": "'|,|"
}

_ozN_patterns = {"0": "||",  "1": "|'",  "2": "|,",  "3": "'|",  "4": "''",
                 "5": "',",  "6": ",|",  "7": ",'",  "8": ",,",  "9": ".|"
}

_ozC_patterns = {"A": "|||", "B": "||'", "C": "||,", "D": "|'|",
                 "E": "|''", "F": "|',", "G": "|,|", "H": "|,'",
                 "I": "|,,", "J": "'||", "K": "'|'", "L": "'|,",
                 "M": "''|", "N": "'''", "O": "'',", "P": "',|",
                 "Q": "','", "R": "',,", "S": ",||", "T": ",|'",
                 "U": ",|,", "V": ",'|", "W": ",''", "X": ",',",
                 "Y": ",,|", "Z": ",,'", "a": "|,.", "b": "|.|",
                 "c": "|.'", "d": "|.,", "e": "|..", "f": "'|.",
                 "g": "''.", "h": "',.", "i": "'.|", "j": "'.'",
                 "k": "'.,", "l": "'..", "m": ",|.", "n": ",'.",
                 "o": ",,.", "p": ",.|", "q": ",.'", "r": ",.,",
                 "s": ",..", "t": ".|.", "u": ".'.", "v": ".,.",
                 "w": "..|", "x": "..'", "y": "..,", "z": "...",
                 "0": ",,,", "1": ".||", "2": ".|'", "3": ".|,",
                 "4": ".'|", "5": ".''", "6": ".',", "7": ".,|",
                 "8": ".,'", "9": ".,,", " ": "||.", "#": "|'.",
}
