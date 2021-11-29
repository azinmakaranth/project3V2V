"""
Control layer.
constantly looks for sensor data,
According to the sensor data, then raise proper alerts

sensors used :
1. Speed gauge 
2. Tyre pressure
3. Steering wheel change
4. Proximity/ radar
5. GPS
6. Heartrate monitor
7. Brake sensor
8. Fuel gauge

if tyre pressure is low :
    then alert all peers --- I may cause an accident
if proximity sensor/radar data :
    then alert the neighbours --- you are too close to me
if speed increases :
    then alert the neighbours --- I am speeding up.
if speed decreases :
    then alert the neighbours --- I am slowing down
if steering wheel change : 
    then alert the neighbours ---- I am changing my direction
if GPS down or unavailable :
    then alert the neighbours
if Heartrate :
    then alert the neighbours --- Passenger in danger
if brake applied :
    then alert the neighbours --- Sudden brake
if .....

"""
# Azin
import logging
import argparse
import time
import threading
import random
import sensor_data_generators as sdg
import broadcast_system as bs

logging.basicConfig(level=logging.INFO)
args_parser = argparse.ArgumentParser()
args_parser.add_argument('--nodeid', help='a number', required=False)

FUEL_LIMIT = 80


class InfraControls(bs.BroadcastSystem):
    def __init__(self, vehicle_id, host_address, listening_port, sending_port):
        super().__init__(host_address, listening_port, sending_port)
        self.sensors = """ list of sensors for infra--->  weather, """
        self.nodeId = vehicle_id

    def run_infra(self):
        threading.Thread(target=self.periodic_updater).start()

    # Whenever a new data is received on this node,
    # the control comes here.
    def information_processor(self, data):
        """Wat to do with the received data ? """
        print("On infra--->[" + data + "]")

    # Thread to push periodic updates to all connected nodes
    def periodic_updater(self):
        while True:
            self.send_information("{'infraNodeId': '" + str(
                self.nodeId) + "', ''alert' : 'Weather alert', 'senorId' : 'WTR', 'senorReading' : dummy_readings}")
            time.sleep(10)

    def deploy(self):
        super().deploy(self.information_processor)
        self.run_infra()


class VehicleControls(bs.BroadcastSystem):
    def __init__(self, vehicle_id, host_address, listening_port, sending_port):
        super().__init__(host_address, listening_port, sending_port)
        self.vehicle_id = vehicle_id
        self.lane = random.choices([0, 1])
        self.speed = 0
        self.tyrePressure = 0
        self.proximity = 0
        self.BP = 0
        self.GPS = 0
        self.fuel = 0
        self.brake = 0
        self.position = 0
        self.sensors = sdg.Sensors().getSensors()  # [""" list of sensor objects"""]

    def run_vehicle(self):
        while True:
            for sensor in self.sensors:
                data = sensor.GET_DATA()
                # data = sensor()
                if data[0] == 'SPD':
                    self.process_speed_data(data)
                elif data[0] == 'TP':
                    self.process_tyre_pressure_data(data)
                elif data[0] == 'LT':
                    self.process_light_sensor_data(data)
                elif data[0] == 'PRX':
                    self.process_proximity_data(data)
                elif data[0] == 'GPS':
                    self.process_gps_data(data)
                elif data[0] == 'HRS':
                    self.process_HRS_data(data)
                elif data[0] == 'BRK':
                    self.process_brake_sensor_data(data)
                elif data[0] == 'FLG':
                    self.process_fuel_guage_data(data)
            time.sleep(1)

    def process_fuel_guage_data(self, data):
        self.fuel = data[1]
        if data[1] < FUEL_LIMIT:
            logging.info(f'[{self.vehicle_id}] Broadcasting low fuel alert')
            self.send_information("{'vehicleId': '" + str(
                self.vehicle_id) + "', ''alert' : 'Low fuel', 'senorId' : 'FLG', 'senorReading' : " + str(
                data[1]) + "}")

    def process_brake_sensor_data(self, data):
        self.brake = data[1]
        if data[1] == True:
            logging.info(f'[{self.vehicle_id}] Broadcasting stopping alert')
            self.send_information("{'vehicleId': '" + str(
                self.vehicle_id) + "', ''alert' : 'Brake applied', 'senorId' : 'BRK', 'senorReading' : " + str(
                data[1]) + "}")

    def process_HRS_data(self, data):
        self.BP = data[1]
        if data[1] < 60 or data[1] > 100:
            logging.info(f'[{self.vehicle_id}] Broadcasting passenger in danger alert')
            self.send_information("{'vehicleId': '" + str(
                self.vehicle_id) + "', ''alert' : 'Low or high heart rate', 'senorId' : 'HRS', 'senorReading' : " + str(
                data[1]) + "}")

    def process_gps_data(self, data):
        self.GPS = data[1]
        logging.info(f'[{self.vehicle_id}] Broadcasting low signal alert')
        self.send_information("{'vehicleId': '" + str(
            self.vehicle_id) + "', ''alert' : 'GPS co-ordinates', 'senorId' : 'GPS', 'senorReading' : " + str(
            data[1]) + "}")

    def process_proximity_data(self, data):
        self.proximity = data[1]
        if data[1] == True or data[2] == True or data[3] == True or data[4] == True:
            logging.info(f'[{self.vehicle_id}] Broadcasting proximity alert')
            self.send_information("{'vehicleId': '" + str(
                self.vehicle_id) + "', ''alert' : 'Proximity alert', 'senorId' : 'PRX', 'senorReading' : " + str(
                data[1]) + "}")

    def process_light_sensor_data(self, data):
        if data[1] == "LOW":
            logging.info(f'[ {self.vehicle_id}] Broadcasting low lights alert')
            self.send_information("{'vehicleId': '" + str(
                self.vehicle_id) + "', ''alert' : 'Low lights alert', 'senorId' : 'LT', 'senorReading' : " + str(
                data[1]) + "}")

    def process_tyre_pressure_data(self, data):
        self.tyrePressure = + data[1]
        if data[1] < 30 or data[1] > 35:
            logging.info(f'[ {self.vehicle_id}] Broadcasting tyre pressure low alert')
            self.send_information("{'vehicleId': '" + str(
                self.vehicle_id) + "', ''alert' : 'Low or high tyre pressure alert', 'senorId' : 'TP', 'senorReading' : " + str(
                data[1]) + "}")

    def process_speed_data(self, data):
        self.position = self.position + data[1]
        self.speed = data[1]
        print("position = " + str(self.position))
        if data[1] > 80:
            logging.info(f'[{self.vehicle_id}] Broadcasting overspeeding alert')
            self.send_information("{'vehicleId': '" + str(
                self.vehicle_id) + "', ''alert' : 'Over speeding alert', 'senorId' : 'SPD', 'senorReading' : " + str(
                data[1]) + "}")

    def get_vehicle_runner_thread(self):
        return threading.Thread(target=self.run_vehicle, args=( ))

    def information_processor():
        pass

    def deploy(self):
        super().deploy(self.information_listener)
        self.get_vehicle_runner_thread().start()

# runner.start()

# v = VehicleControls(vechile_id)

# runner = v.get_vehicle_runner_thread()

# runner.start()
