#!/usr/bin/env python3
# sdaps_web - Webinterface for SDAPS
# Copyright(C) 2019, Benjamin Berg <benjamin@sipsolutions.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from sdaps import model
from sdaps import surface
from sdaps import image

class Questionnaire(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'sdaps_ctl'
    obj_class = model.questionnaire.Questionnaire

    def get_data(self):
        data = {}

        # We just need to iterate all boxes, and get their data objects.
        # These are then exported
        for qobject in self.obj.qobjects:
            for box in qobject.boxes:
                bdata = box.data
                data[box.id_str()] = {
                    'type' : box.__class__.__name__,
                    'state' : bool(bdata.state),
                    'quality' : bdata.quality,
                    'x' : bdata.x,
                    'y' : bdata.y,
                    'width' : bdata.width,
                    'height' : bdata.height,
                    'page' : box.page_number,
                }
                if isinstance(bdata, model.data.Textbox):
                    data[box.id_str()]['text'] = bdata.text
                if isinstance(bdata, model.data.Checkbox):
                    data[box.id_str()]['form'] = box.form

        return data


    def set_data(self, data):
        for qobject in self.obj.qobjects:
            for box in qobject.boxes:
                idstr = box.id_str()

                # Ignore missing items
                if idstr not in data:
                    continue

                # Ignore if type is not correct
                rdata = data[idstr]
                if 'type' not in rdata or rdata['type'] != box.__class__.__name__:
                    continue

                bdata = box.data

                # Copy data over (if it exists); we only accept updates to
                # some of the keys.
                items = [('state', int)]
                if isinstance(bdata, model.data.Textbox):
                    items += [('x', float), ('y', float), ('width', float), ('height', float)]
                    items += [('text', str)]

                # Try to convert values, if it fails, whatever
                values = {}
                for item, dtype in items:
                    if item not in rdata:
                        continue
                    try:
                        values[item] = dtype(rdata[item])
                    except ValueError:
                        pass

                for k, v in list(values.items()):
                    setattr(bdata, k, v)


