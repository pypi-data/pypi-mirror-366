import json
from typing import Callable

import logging
logger = logging.getLogger(__name__)

from carveracontroller.CNC import CNC
from carveracontroller.Controller import Controller

from kivy.clock import Clock
from kivy.uix.settings import SettingItem
from kivy.uix.spinner import Spinner
from kivy.uix.anchorlayout import AnchorLayout
from kivy.config import Config

class OverrideController:
    def __init__(self, get_value: Callable[[], float],
                 set_value: Callable[[float], None],
                 min_limit: int = 0, max_limit: int = 200,
                 step: int = 10) -> None:
        self._get_value = get_value
        self._set_value = set_value
        self._min_limit = min_limit
        self._max_limit = max_limit
        self._step = step

    def on_increase(self) -> None:
        new_value = min(self._get_value() + self._step, self._max_limit)
        self._set_value(new_value)

    def on_decrease(self) -> None:
        new_value = max(self._get_value() - self._step, self._min_limit)
        self._set_value(new_value)

class Pendant:
    def __init__(self, controller: Controller, cnc: CNC,
                 feed_override: OverrideController,
                 spindle_override: OverrideController,
                 is_jogging_enabled: Callable[[], None],
                 handle_run_pause_resume: Callable[[], None],
                 handle_probe_z: Callable[[], None],
                 open_probing_popup: Callable[[], None],
                 report_connection: Callable[[], None],
                 report_disconnection: Callable[[], None]) -> None:
        self._controller = controller
        self._cnc = cnc
        self._feed_override = feed_override
        self._spindle_override = spindle_override

        self._is_jogging_enabled = is_jogging_enabled
        self._handle_run_pause_resume = handle_run_pause_resume
        self._handle_probe_z = handle_probe_z
        self._open_probing_popup = open_probing_popup
        self._report_connection = report_connection
        self._report_disconnection = report_disconnection

    def close(self) -> None:
        pass

    def executor(self, f: Callable[[], None]) -> None:
        Clock.schedule_once(lambda _: f(), 0)

    def run_macro(self, macro_id: int) -> None:
        macro_key = f"pendant_macro_{macro_id}"
        macro_value = Config.get("carvera", macro_key)

        if not macro_value:
            logger.warning(f"No macro defined for ID {macro_id}")
            return

        macro_value = json.loads(macro_value)

        try:
            lines = macro_value.get("gcode", "").splitlines()
            for l in lines:
                l = l.strip()
                if l == "":
                    continue
                self._controller.sendGCode(l)
        except Exception as e:
            logger.error(f"Failed to run macro {macro_id}: {e}")


class NonePendant(Pendant):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


try:
    from . import whb04
    WHB04_SUPPORTED = True
except Exception as e:
    logger.warn(f"WHB04 pendant not supported: {e}")
    WHB04_SUPPORTED = False

if WHB04_SUPPORTED:
    class WHB04(Pendant):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)

            self._is_spindle_running = False

            self._daemon = whb04.Daemon(self.executor)

            self._daemon.on_connect = self._handle_connect
            self._daemon.on_disconnect = self._handle_disconnect
            self._daemon.on_update = self._handle_display_update
            self._daemon.on_jog = self._handle_jogging
            self._daemon.on_button_press = self._handle_button_press

            self._daemon.start()

        def _handle_connect(self, daemon: whb04.Daemon) -> None:
            daemon.set_display_step_indicator(whb04.StepIndicator.STEP)
            self._report_connection()

        def _handle_disconnect(self, daemon: whb04.Daemon) -> None:
            self._report_disconnection()

        def _handle_display_update(self, daemon: whb04.Daemon) -> None:
            daemon.set_display_position(whb04.Axis.X, self._cnc.vars["wx"])
            daemon.set_display_position(whb04.Axis.Y, self._cnc.vars["wy"])
            daemon.set_display_position(whb04.Axis.Z, self._cnc.vars["wz"])
            # There are no absolute positions for the rotational axis, hence ma
            # instead of wa is used.
            daemon.set_display_position(whb04.Axis.A, self._cnc.vars["ma"])
            daemon.set_display_feedrate(self._cnc.vars["curfeed"])
            daemon.set_display_spindle_speed(self._cnc.vars["curspindle"])

        def _handle_jogging(self, daemon: whb04.Daemon, steps: int) -> None:
            if not self._is_jogging_enabled():
                return

            distance = steps * daemon.step_size_value
            axis = daemon.active_axis_name

            if axis not in "XYZA":
                return

            # Jog as fast as you can as the machine should follow the pendant as
            # closely as possible. We choose some reasonably high speed here,
            # the machine will limit itself to the maximum speed it can handle.
            self._controller.jog_with_speed(f"{axis}{distance}", 10000)

        def _handle_button_press(self, daemon: whb04.Daemon, button: whb04.Button) -> None:
            is_fn_pressed = whb04.Button.FN in daemon.pressed_buttons
            is_action_primary = Config.get("carvera", "pendant_primary_button_action") == "Key-specific Action"

            should_run_action = is_fn_pressed
            if is_action_primary:
                should_run_action = not should_run_action

            if button == whb04.Button.RESET:
                self._controller.estopCommand()
            if button == whb04.Button.STOP:
                self._controller.abortCommand()
            if button == whb04.Button.START_PAUSE:
                self._handle_run_pause_resume()

            if should_run_action:
                if button == whb04.Button.FEED_PLUS:
                    self._feed_override.on_increase()
                if button == whb04.Button.FEED_MINUS:
                    self._feed_override.on_decrease()
                if button == whb04.Button.SPINDLE_PLUS:
                    self._spindle_override.on_increase()
                if button == whb04.Button.SPINDLE_MINUS:
                    self._spindle_override.on_decrease()
                if button == whb04.Button.M_HOME:
                    self._controller.gotoMachineHome()
                if button == whb04.Button.SAFE_Z:
                    self._controller.gotoSafeZ()
                if button == whb04.Button.W_HOME:
                    self._controller.gotoWCSHome()
                if button == whb04.Button.S_ON_OFF:
                    self._is_spindle_running = not self._is_spindle_running
                    self._controller.setSpindleSwitch(self._is_spindle_running)
                if button == whb04.Button.PROBE_Z:
                    self._handle_probe_z()
            else:
                MACROS = [
                    whb04.Button.FEED_PLUS,
                    whb04.Button.FEED_MINUS,
                    whb04.Button.SPINDLE_PLUS,
                    whb04.Button.SPINDLE_MINUS,
                    whb04.Button.M_HOME,
                    whb04.Button.SAFE_Z,
                    whb04.Button.W_HOME,
                    whb04.Button.S_ON_OFF,
                    whb04.Button.PROBE_Z,
                    whb04.Button.MACRO_10
                ]
                if button not in MACROS:
                    return
                macro_idx = 1 + MACROS.index(button)
                self.run_macro(macro_idx)


SUPPORTED_PENDANTS = {
    "None": NonePendant
}

if WHB04_SUPPORTED:
    SUPPORTED_PENDANTS["WHB04"] = WHB04


class SettingPendantSelector(SettingItem):
    def __init__(self, **kwargs):
        # Wrapper to ensure the content is centered vertically
        wrapper = AnchorLayout(anchor_y='center', anchor_x='left')

        self.spinner = Spinner(text="None", values=list(SUPPORTED_PENDANTS.keys()), size_hint=(1, None), height='36dp')
        super().__init__(**kwargs)
        self.spinner.bind(text=self.on_spinner_select)
        wrapper.add_widget(self.spinner)
        self.add_widget(wrapper)

    def on_spinner_select(self, spinner, text):
        self.panel.set_value(self.section, self.key, text)

    def on_value(self, instance, value):
        if self.spinner.text != value:
            self.spinner.text = value
