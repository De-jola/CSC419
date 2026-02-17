"""
Control Layer - Smart Home Energy Management System
Implements Finite State Machines (FSM) for AC and Lighting control.
"""

""" Import sensors from sensor.py 
"""

from typing import Dict, Any
from sensors import SensorObserver

class ACController:
    """
    FSM for Air Conditioning.
    States: OFF, STANDBY, COOLING
    Logic:
    - OFF: Room is empty.
    - STANDBY: Room occupied, temp < 28°C.
    - COOLING: Room occupied, temp > 28°C. 
    - Hysteresis: If COOLING, stay COOLING until temp < 24°C to prevent flickering.
    """
    def __init__(self):
        self.state = "OFF"
    def update_state(self, occupied: bool, temp: float) -> str:
        if not occupied:
            self.state = "OFF"
        elif self.state == "OFF":
            # Transition from OFF to active states
            self.state = "COOLING" if temp >= 28 else "STANDBY"
        elif self.state == "STANDBY":
            if temp >= 28:
                self.state = "COOLING"
        elif self.state == "COOLING":
            if temp < 24:
                self.state = "STANDBY"

        return self.state

class LightController:
    """
    FSM for Lighting.
    States: OFF, ON
    Logic: ON only when occupied AND light level < 300.
    """
    def __init__(self):
        self.state = "OFF"

    def update_state(self, occupied: bool, light_level: int) -> str:
        if occupied and light_level < 300:
            self.state = "ON"
        else:
            self.state = "OFF"

        return self.state

class RoomController(SensorObserver):
    """
    Implements SensorObserver to receive data from sensors.py.
    Manages AC and Light FSMs and supports manual overrides.
    """
    def __init__(self, room_name: str):
        self.room_name = room_name
        self.ac = ACController()
        self.lights = LightController()

        self.current_temp = 20.0
        self.is_occupied = False
        self.current_light_level = 500

        self.manual_ac_override = None
        self.manual_light_override = None

    def update(self, sensor_data: Dict[str, Any]) -> None:
        """
        Receives updates from the Sensor Layer.
        Note: sensor_data is sent per sensor type as per sensors.py
        """

        stype = sensor_data.get('sensor_type')

        if stype == 'temperature':
            self.current_temp = sensor_data['value']
        elif stype == 'pir':
            self.is_occupied = sensor_data['occupied']
        elif stype == 'ldr':
            self.current_light_level = sensor_data['value']

    def _log_status(self, ac_state: str, light_state: str):
        print(f"[{self.room_name}] Temp: {self.current_temp}°C | "
              f"Occ: {self.is_occupied} | Lvl: {self.current_light_level} | "
              f"AC: {ac_state} | Lights: {light_state}")

if __name__ == "__main__":
    from sensors import RoomSensors

    print("Starting Smart Home Control Test...")
    living_room = RoomSensors("Living Room", base_temp=25.0)
    controller = RoomController("Living Room")

    for hour in range(24):
        print(f"\n--- Hour {hour}:00 ---")
        living_room.read_all(hour)
