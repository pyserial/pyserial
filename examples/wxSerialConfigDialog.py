#!/usr/bin/env python
#
# A serial port configuration dialog for wxPython. A number of flags can
# be used to configure the fields that are displayed.
#
# (C) 2001-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

import wx
import serial
import serial.tools.list_ports

SHOW_BAUDRATE = 1 << 0
SHOW_FORMAT = 1 << 1
SHOW_FLOW = 1 << 2
SHOW_TIMEOUT = 1 << 3
SHOW_ALL = SHOW_BAUDRATE | SHOW_FORMAT | SHOW_FLOW | SHOW_TIMEOUT


class SerialConfigDialog(wx.Dialog):
    """\
    Serial Port configuration dialog, to be used with pySerial 2.0+
    When instantiating a class of this dialog, then the "serial" keyword
    argument is mandatory. It is a reference to a serial.Serial instance.
    the optional "show" keyword argument can be used to show/hide different
    settings. The default is SHOW_ALL which corresponds to
    SHOW_BAUDRATE|SHOW_FORMAT|SHOW_FLOW|SHOW_TIMEOUT. All constants can be
    found in this module (not the class).
    """

    def __init__(self, *args, **kwds):
        # grab the serial keyword and remove it from the dict
        self.serial = kwds['serial']
        del kwds['serial']
        self.show = SHOW_ALL
        if 'show' in kwds:
            self.show = kwds.pop('show')
        # begin wxGlade: SerialConfigDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.label_2 = wx.StaticText(self, -1, "Port")
        self.choice_port = wx.Choice(self, -1, choices=[])
        self.label_1 = wx.StaticText(self, -1, "Baudrate")
        self.combo_box_baudrate = wx.ComboBox(self, -1, choices=[], style=wx.CB_DROPDOWN)
        self.sizer_1_staticbox = wx.StaticBox(self, -1, "Basics")
        self.panel_format = wx.Panel(self, -1)
        self.label_3 = wx.StaticText(self.panel_format, -1, "Data Bits")
        self.choice_databits = wx.Choice(self.panel_format, -1, choices=["choice 1"])
        self.label_4 = wx.StaticText(self.panel_format, -1, "Stop Bits")
        self.choice_stopbits = wx.Choice(self.panel_format, -1, choices=["choice 1"])
        self.label_5 = wx.StaticText(self.panel_format, -1, "Parity")
        self.choice_parity = wx.Choice(self.panel_format, -1, choices=["choice 1"])
        self.sizer_format_staticbox = wx.StaticBox(self.panel_format, -1, "Data Format")
        self.panel_timeout = wx.Panel(self, -1)
        self.checkbox_timeout = wx.CheckBox(self.panel_timeout, -1, "Use Timeout")
        self.text_ctrl_timeout = wx.TextCtrl(self.panel_timeout, -1, "")
        self.label_6 = wx.StaticText(self.panel_timeout, -1, "seconds")
        self.sizer_timeout_staticbox = wx.StaticBox(self.panel_timeout, -1, "Timeout")
        self.panel_flow = wx.Panel(self, -1)
        self.checkbox_rtscts = wx.CheckBox(self.panel_flow, -1, "RTS/CTS")
        self.checkbox_xonxoff = wx.CheckBox(self.panel_flow, -1, "Xon/Xoff")
        self.sizer_flow_staticbox = wx.StaticBox(self.panel_flow, -1, "Flow Control")
        self.button_ok = wx.Button(self, wx.ID_OK, "")
        self.button_cancel = wx.Button(self, wx.ID_CANCEL, "")

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        # attach the event handlers
        self.__attach_events()

    def __set_properties(self):
        # begin wxGlade: SerialConfigDialog.__set_properties
        self.SetTitle("Serial Port Configuration")
        self.choice_databits.SetSelection(0)
        self.choice_stopbits.SetSelection(0)
        self.choice_parity.SetSelection(0)
        self.text_ctrl_timeout.Enable(False)
        self.button_ok.SetDefault()
        # end wxGlade
        self.SetTitle("Serial Port Configuration")
        if self.show & SHOW_TIMEOUT:
            self.text_ctrl_timeout.Enable(0)
        self.button_ok.SetDefault()

        if not self.show & SHOW_BAUDRATE:
            self.label_1.Hide()
            self.combo_box_baudrate.Hide()
        if not self.show & SHOW_FORMAT:
            self.panel_format.Hide()
        if not self.show & SHOW_TIMEOUT:
            self.panel_timeout.Hide()
        if not self.show & SHOW_FLOW:
            self.panel_flow.Hide()

        # fill in ports and select current setting
        preferred_index = 0
        self.choice_port.Clear()
        self.ports = []
        for n, (portname, desc, hwid) in enumerate(sorted(serial.tools.list_ports.comports())):
            self.choice_port.Append(u'{} - {}'.format(portname, desc))
            self.ports.append(portname)
            if self.serial.name == portname:
                preferred_index = n
        self.choice_port.SetSelection(preferred_index)
        if self.show & SHOW_BAUDRATE:
            preferred_index = None
            # fill in baud rates and select current setting
            self.combo_box_baudrate.Clear()
            for n, baudrate in enumerate(self.serial.BAUDRATES):
                self.combo_box_baudrate.Append(str(baudrate))
                if self.serial.baudrate == baudrate:
                    preferred_index = n
            if preferred_index is not None:
                self.combo_box_baudrate.SetSelection(preferred_index)
            else:
                self.combo_box_baudrate.SetValue(u'{}'.format(self.serial.baudrate))
        if self.show & SHOW_FORMAT:
            # fill in data bits and select current setting
            self.choice_databits.Clear()
            for n, bytesize in enumerate(self.serial.BYTESIZES):
                self.choice_databits.Append(str(bytesize))
                if self.serial.bytesize == bytesize:
                    index = n
            self.choice_databits.SetSelection(index)
            # fill in stop bits and select current setting
            self.choice_stopbits.Clear()
            for n, stopbits in enumerate(self.serial.STOPBITS):
                self.choice_stopbits.Append(str(stopbits))
                if self.serial.stopbits == stopbits:
                    index = n
            self.choice_stopbits.SetSelection(index)
            # fill in parities and select current setting
            self.choice_parity.Clear()
            for n, parity in enumerate(self.serial.PARITIES):
                self.choice_parity.Append(str(serial.PARITY_NAMES[parity]))
                if self.serial.parity == parity:
                    index = n
            self.choice_parity.SetSelection(index)
        if self.show & SHOW_TIMEOUT:
            # set the timeout mode and value
            if self.serial.timeout is None:
                self.checkbox_timeout.SetValue(False)
                self.text_ctrl_timeout.Enable(False)
            else:
                self.checkbox_timeout.SetValue(True)
                self.text_ctrl_timeout.Enable(True)
                self.text_ctrl_timeout.SetValue(str(self.serial.timeout))
        if self.show & SHOW_FLOW:
            # set the rtscts mode
            self.checkbox_rtscts.SetValue(self.serial.rtscts)
            # set the rtscts mode
            self.checkbox_xonxoff.SetValue(self.serial.xonxoff)

    def __do_layout(self):
        # begin wxGlade: SerialConfigDialog.__do_layout
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_flow_staticbox.Lower()
        sizer_flow = wx.StaticBoxSizer(self.sizer_flow_staticbox, wx.HORIZONTAL)
        self.sizer_timeout_staticbox.Lower()
        sizer_timeout = wx.StaticBoxSizer(self.sizer_timeout_staticbox, wx.HORIZONTAL)
        self.sizer_format_staticbox.Lower()
        sizer_format = wx.StaticBoxSizer(self.sizer_format_staticbox, wx.VERTICAL)
        grid_sizer_1 = wx.FlexGridSizer(3, 2, 0, 0)
        self.sizer_1_staticbox.Lower()
        sizer_1 = wx.StaticBoxSizer(self.sizer_1_staticbox, wx.VERTICAL)
        sizer_basics = wx.FlexGridSizer(3, 2, 0, 0)
        sizer_basics.Add(self.label_2, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 4)
        sizer_basics.Add(self.choice_port, 0, wx.EXPAND, 0)
        sizer_basics.Add(self.label_1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 4)
        sizer_basics.Add(self.combo_box_baudrate, 0, wx.EXPAND, 0)
        sizer_basics.AddGrowableCol(1)
        sizer_1.Add(sizer_basics, 0, wx.EXPAND, 0)
        sizer_2.Add(sizer_1, 0, wx.EXPAND, 0)
        grid_sizer_1.Add(self.label_3, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 4)
        grid_sizer_1.Add(self.choice_databits, 1, wx.EXPAND | wx.ALIGN_RIGHT, 0)
        grid_sizer_1.Add(self.label_4, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 4)
        grid_sizer_1.Add(self.choice_stopbits, 1, wx.EXPAND | wx.ALIGN_RIGHT, 0)
        grid_sizer_1.Add(self.label_5, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 4)
        grid_sizer_1.Add(self.choice_parity, 1, wx.EXPAND | wx.ALIGN_RIGHT, 0)
        sizer_format.Add(grid_sizer_1, 1, wx.EXPAND, 0)
        self.panel_format.SetSizer(sizer_format)
        sizer_2.Add(self.panel_format, 0, wx.EXPAND, 0)
        sizer_timeout.Add(self.checkbox_timeout, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 4)
        sizer_timeout.Add(self.text_ctrl_timeout, 0, 0, 0)
        sizer_timeout.Add(self.label_6, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 4)
        self.panel_timeout.SetSizer(sizer_timeout)
        sizer_2.Add(self.panel_timeout, 0, wx.EXPAND, 0)
        sizer_flow.Add(self.checkbox_rtscts, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 4)
        sizer_flow.Add(self.checkbox_xonxoff, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 4)
        sizer_flow.Add((10, 10), 1, wx.EXPAND, 0)
        self.panel_flow.SetSizer(sizer_flow)
        sizer_2.Add(self.panel_flow, 0, wx.EXPAND, 0)
        sizer_3.Add(self.button_ok, 0, 0, 0)
        sizer_3.Add(self.button_cancel, 0, 0, 0)
        sizer_2.Add(sizer_3, 0, wx.ALL | wx.ALIGN_RIGHT, 4)
        self.SetSizer(sizer_2)
        sizer_2.Fit(self)
        self.Layout()
        # end wxGlade

    def __attach_events(self):
        self.button_ok.Bind(wx.EVT_BUTTON, self.OnOK)
        self.button_cancel.Bind(wx.EVT_BUTTON, self.OnCancel)
        if self.show & SHOW_TIMEOUT:
            self.checkbox_timeout.Bind(wx.EVT_CHECKBOX, self.OnTimeout)

    def OnOK(self, events):
        success = True
        self.serial.port = self.ports[self.choice_port.GetSelection()]
        if self.show & SHOW_BAUDRATE:
            try:
                b = int(self.combo_box_baudrate.GetValue())
            except ValueError:
                with wx.MessageDialog(
                        self,
                        'Baudrate must be a numeric value',
                        'Value Error',
                        wx.OK | wx.ICON_ERROR) as dlg:
                    dlg.ShowModal()
                success = False
            else:
                self.serial.baudrate = b
        if self.show & SHOW_FORMAT:
            self.serial.bytesize = self.serial.BYTESIZES[self.choice_databits.GetSelection()]
            self.serial.stopbits = self.serial.STOPBITS[self.choice_stopbits.GetSelection()]
            self.serial.parity = self.serial.PARITIES[self.choice_parity.GetSelection()]
        if self.show & SHOW_FLOW:
            self.serial.rtscts = self.checkbox_rtscts.GetValue()
            self.serial.xonxoff = self.checkbox_xonxoff.GetValue()
        if self.show & SHOW_TIMEOUT:
            if self.checkbox_timeout.GetValue():
                try:
                    self.serial.timeout = float(self.text_ctrl_timeout.GetValue())
                except ValueError:
                    with wx.MessageDialog(
                            self,
                            'Timeout must be a numeric value',
                            'Value Error',
                            wx.OK | wx.ICON_ERROR) as dlg:
                        dlg.ShowModal()
                    success = False
            else:
                self.serial.timeout = None
        if success:
            self.EndModal(wx.ID_OK)

    def OnCancel(self, events):
        self.EndModal(wx.ID_CANCEL)

    def OnTimeout(self, events):
        if self.checkbox_timeout.GetValue():
            self.text_ctrl_timeout.Enable(True)
        else:
            self.text_ctrl_timeout.Enable(False)

# end of class SerialConfigDialog


class MyApp(wx.App):
    """Test code"""
    def OnInit(self):
        wx.InitAllImageHandlers()

        ser = serial.Serial()
        print(ser)
        # loop until cancel is pressed, old values are used as start for the next run
        # show the different views, one after the other
        # value are kept.
        for flags in (SHOW_BAUDRATE, SHOW_FLOW, SHOW_FORMAT, SHOW_TIMEOUT, SHOW_ALL):
            dialog_serial_cfg = SerialConfigDialog(None, -1, "", serial=ser, show=flags)
            self.SetTopWindow(dialog_serial_cfg)
            result = dialog_serial_cfg.ShowModal()
            print(ser)
            if result != wx.ID_OK:
                break
        # the user can play around with the values, CANCEL aborts the loop
        while True:
            dialog_serial_cfg = SerialConfigDialog(None, -1, "", serial=ser)
            self.SetTopWindow(dialog_serial_cfg)
            result = dialog_serial_cfg.ShowModal()
            print(ser)
            if result != wx.ID_OK:
                break
        return 0

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
