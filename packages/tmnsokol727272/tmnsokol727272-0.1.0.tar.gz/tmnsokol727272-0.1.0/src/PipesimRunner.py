import csv
import json
import logging
import os
import pandas as pd
import requests

class PipesimRunner():
    #CAL_HEAD = "/api/v1/calibration/vfm/head"
    #CAL_PI = "/api/v1/calibration/vfm/pi"
    
    SIM_PI = "/api/v1/simulation/vfm/pi"
    SIM_HEAD = "/api/v1/simulation/vfm/head"
    LICENSE_VALID = "/api/v1/license/expiration"
    PIPESIM_AUTH = 'asdf'
    HTTP_HEADER = {
    "Content-type": "application/json",
    "Authorization": f"Bearer {PIPESIM_AUTH}"
    }

    head_feature_columns = ['model_text_head', 'intake_pressure', 'discharge_pressure', 'motor_temperature', 'drive_frequency', 'well_test_water_cut', 'well_test_gor', 'well_test_api', 'flow_rate']
    pi_feature_columns = ['model_text_pi', 'intake_pressure', 'well_test_water_cut', 'well_test_gor', 'well_test_api', 'flow_rate']
    
    def __init__(self, head_output_csv_path, pi_output_csv_path):
        self.pipesim_url = os.getenv("PIPESIM_URI", "http://localhost:5000")
        
        self.head_output_csv_path = head_output_csv_path
        self.pi_output_csv_path = pi_output_csv_path
        self.__cleanup_files()
    
    def __cleanup_files(self):
        if(os.path.exists(self.head_output_csv_path)):
            os.remove(self.head_output_csv_path)
        
        if(os.path.exists(self.pi_output_csv_path)):
            os.remove(self.pi_output_csv_path)
            
    def run_simulations(self, model_text_pi, model_text_head, intake_pressure, discharge_pressure, motor_temperature, drive_frequency, well_test_water_cut, well_test_gor, well_test_api):
        flow_rate_head = -1
        flow_rate_pi = -1
        if(self.__is_valid(drive_frequency, intake_pressure, discharge_pressure)):
            # TODO:
            flow_rate_head = 1000 # self.__run_simulation_flow_rate_head(model_text_head, intake_pressure, well_test_water_cut, discharge_pressure, drive_frequency,  motor_temperature, well_test_gor, well_test_api)
            flow_rate_pi = 500 # self.__run_simulation_flow_rate_pi(model_text_pi, intake_pressure, well_test_water_cut, well_test_gor, well_test_api)
    
        new_row_flow_rate_head = [model_text_head, intake_pressure, discharge_pressure, motor_temperature, drive_frequency, well_test_water_cut, well_test_gor, well_test_api, flow_rate_head]
        self.__write_to_csv(self.head_output_csv_path, self.head_feature_columns, new_row_flow_rate_head)

        new_row_flow_rate_pi = [model_text_pi, intake_pressure, well_test_water_cut, well_test_gor, well_test_api, flow_rate_pi]
        self.__write_to_csv(self.pi_output_csv_path, self.pi_feature_columns, new_row_flow_rate_pi)

    def __write_to_csv(self, csv_path, header, row):
        is_existing_file = os.path.exists(csv_path)
        
        with(open(f"{csv_path}", "a", newline='') ) as file:
            writer = csv.writer(file)
            
            if(is_existing_file == False):
                writer.writerow(header)
            
            writer.writerow(row)
            
    def __run_simulation_flow_rate_pi(self, model_text_pi, intake_pressure, well_test_water_cut, well_test_gor, well_test_api):
        req_body = {
				"model_text": model_text_pi,
				"inlet_pressure": intake_pressure,
				"water_cut": well_test_water_cut,
				"gor":well_test_gor,
				"api":well_test_api
			}
    
        url = self.pipesim_url + self.SIM_PI
        logging.info(f"......calling PI Simulation API...... URL:{url}")
        
        data=json.dumps(req_body)
        response = requests.post(url=url, data=data, headers=self.HTTP_HEADER)
        
        logging.info(f"response with code {response.status_code}")
        
        flow_rate_pi = -1
        if response.status_code == 200:
            flow_rate_pi = round(response.json()['flowrate'])
            logging.info(f"Api response status in workflow_simulation_pi: {response.status_code}")
            logging.info("Flow Rate Pi value:" +str(flow_rate_pi))
        
        return flow_rate_pi
    
    def __run_simulation_flow_rate_head(self, model_text_head, intake_pressure, well_test_water_cut, discharge_pressure, drive_frequency,  motor_temperature, well_test_gor, well_test_api):
        req_body = {
                "model_text": model_text_head,
                "inlet_pressure":intake_pressure,
                "water_cut": well_test_water_cut,
                "outlet_pressure": discharge_pressure,
                "operating_frequency": drive_frequency,
                "motor_temperature": motor_temperature,
                "gor":well_test_gor,
                "api":well_test_api
            }
    
        url = self.pipesim_url + self.SIM_HEAD
        logging.info(f"......calling HEAD Simulation API...... URL:{url}")
        data=json.dumps(req_body)
        response = requests.post(url=url, data=data, headers=self.HTTP_HEADER)
        
        logging.info(f"response with code {response.status_code}")
        
        flow_rate_head = -1
        if response.status_code == 200:
            flow_rate_head = round(response.json()['flowrate'])
            logging.info(f"Api response status in workflow_simulation_head: {response.status_code}")
            logging.info("Flow Rate Head value:" +str(flow_rate_head))
        
        return flow_rate_head

    def __is_valid(self, drive_frequency, intake_pressure, discharge_pressure):
        return drive_frequency > 0 and discharge_pressure > intake_pressure
