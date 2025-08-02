
import csv
import logging
import os
import joblib

from sklearn.tree import plot_tree
import matplotlib.pyplot as plt
    
from Config import Config
from FlushStreamHandler import FlushStreamHandler
from PipesimInputGenerator import PipesimInputGenerator
from MlModelGenerator import MlModelGenerator
from PipesimRunner import PipesimRunner
from TimerService import TimerService

class Runner():
    
    TARGET_COLUMN = 'flow_rate'
    PI_FEATURE_COLUMNS = ['intake_pressure', 'well_test_water_cut', 'well_test_gor', 'well_test_api']
    HEAD_FEATURE_COLUMNS = ['discharge_pressure', 'motor_temperature', 'drive_frequency'] + PI_FEATURE_COLUMNS
    
    def __init__(self, output_folder_path):
        self.output_folder_path = output_folder_path
    
    def generate_combinations(self, parameter_combinations_csv_name):
        param_ranges = {
                    "well_test_gor": range(1, 60, 20),
                    "well_test_api": range(1, 60, 20),
                    "well_test_water_cut": range(0, 100, 10),
                    "intake_pressure": range(1, 2500, 100),
                    "discharge_pressure": range(1, 2500, 100),
                    "motor_temperature": range(1, 500, 50),
                    "drive_frequency": range(1, 100, 20)
                }

        output_csv = os.path.join(self.output_folder_path, parameter_combinations_csv_name)
        pipesim_input_generator = PipesimInputGenerator()
        pipesim_input_generator.generate(param_ranges, output_csv)
        return output_csv

    def generate_models(self):
        parameter_combinations_input = self.generate_combinations("parameter_combinations.csv")
        
        # base64, constants for now
        model_text_head = "JCNQSVBFU0lNIGJ1aWxkOiAyMDIxLjEuNjg3LjAgb24gV2VkbmVzZGF5LCBNYXkgMywgMjAyMyAxMDozNDoxMCBQTQokIENIU0EtMDEwCmpvYgpVTklUUwlpbnB1dCA9IEVORyBvdXRwdXQgPSBFTkcKT1BUSU9OUyBwcG1ldGhvZCA9IDEgdGhtZXRob2QgPSAxClBSSU5UCXByaW1hcnkgYXV4aWxpYXJ5IGVjaG8KTk9QUklOVAlwcm9maWxlIGZsdWlkIGluZmxvdyBoaW4gaG91dCBzbHVnIGl0ZXIKUFJJTlQJQ0FTRVMgPSAxCk9QVElPTlMgICBlb2ZzID0gMQpPUFRJT05TIGd0Z3JhZGllbnQgPSBPTgpFUk9TSU9OIG1vZGVsID0gQVBJIEsgPSAxMDAgZW5nCgpFUk9TSU9OICBSSVNLTElNSVQ9KDAuMDEsMC40LDAuOCwxKQpDT1JST1NJT04gbW9kZWwgPSBERVdBQVJEIGVmZmljaWVuY3kgPSAxIHBoYWN0ID0gMApDT1JST1NJT04gIFJJU0tMSU1JVD0oMC4xLDEsMTAsNTApCgpTTFVHIFNHTFYgPSBNT0RJRklFRApwbG90ZmlsZWRhdGEgIipTVElOR1JBWSBpbmZsb3dzLENwbDEiCgokKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqCiQgICBPUEVSQVRJT04KJCoqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKgpwbG90CWNhc2VkYXRhIGpvYmRhdGEgeHljYXNlID0gZGMKaXRlcm4JdHlwZSA9IGxmbG93IHBvdXQgPSA/UE9VVCBwc2lhICAKCgpwbG90IHByb2ZpbGUgPStnOAoKCnBsb3QgcHJvZmlsZSA9K0Y4TTI0TTVONU81CgpwbG90IHByb2ZpbGUgPStXMjhZMjhVMjhWMjhGOE0yNEFCQ0RFRkdISUpLTE5PU1RVVlhZWkEyQjJDMkQyRTJGMkcySDJJMkoySzJMMlYyVzJYMkEzQjNDM0kzSzNaM0E0QjRDNEo0TTRUNFU0UTdUN04yNE80UDRRNEQ0UTdUN04yNE80UDRRNEQ0UDVRNVQ4VThHOUkxN0oxN1QxN0IyNUMyNUQyNUcyN0gyN0kyNwpwbG90IHN5c3RlbSA9K08xME4xMEFCQ0RFRkdISUk4SzhKS0xOT1BRUlNUVldXM001QzZFNlo4VDEwVTEwVjEwVzEwWDEwWTEwWjEwQTExQjExQzExRjExRzExSDExSTExSjExUTExUjExUzExRjZHNkg2STZKNks2TDZUMTFVMTFWMTFYMTFZMTFaMTFCMTJDMTJEMTJGMTJIMTJJMTJKMTJLMTJVVldYWUwyTTJOMk8yUDJRMlIyWjlON1MyVDJVMkIzQzNEM0UzSzNMM00zTjNPM0s1WlAzUTNTM1QzVjNQNVE1UjVTNVc1WDVFNk02VzZCN1k4UDlROVI5UzkKcGxvdCBzeXN0ZW0gPStUOVY3CiQqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioKJCAgIEZMVUlEUwokKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqCiQqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioKJCBGTFVJRCBEQVRBIC0gQ0hTQS0wMTAgICQgRGVzY3JpcHRpb24gOiAKJCoqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKgpiZWdpbiBmbHVpZCBuYW1lID0gJ0NIU0EtMDEwJwpwcm9wCWFwaSA9IDIwLjUgZ2Fzc2cgPSAwLjY0IHdhdGVyc2cgPSAxLjAyCnJhdGUJd2N1dCA9ID9XQ1VUICBnb3IgPSA1OCAgCmx2aXMJZG92Y29yciA9IGJlZ3JvYiBsb3Zjb3JyID0gQ0hFV0NPTiB1b3Zjb3JyID0gdmF6YmVnIApsdmlzCWVtdWxzaW9uID0gc3dhcCBib3VuZGFyeSA9IDYwICAKY29udGFtaW5hbnRzCWNvMiA9IDAgaDJzID0gMCBuMiA9IDAgaDIgPSAwIGNvID0gMCAKY3BmbHVpZAkgICAgCmtmbHVpZAkgICAKYmxhY2tvaWwJY29yciA9IExBU0FURVIgZ2FzemNvcnIgPSBTVEFORElORyAgb2Z2ZmNvcnIgPSBTVEFORElORyAKYmxhY2tvaWwJRU5USEFMUFk9MjAwOQplbmQgZmx1aWQKCgoKQkxBQ0tPSUwgVVNFID0gJ0NIU0EtMDEwJyAKCiQqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioKJCAgIElOTEVUCiQqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioKaW5sZXQJCXRlbXA9ID9URU1QICBwcmVzPSA/UElOICBsYWJlbCA9ICdDcGwxJyAKCgokKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqCiAgIFBST0ZJTEUKJCoqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKgp2Y29ycgkJdHlwZSA9IEhCUiBhbmdsZSA9IDQ0Ljk5OTk5OTk3NzIyNzkgZmZhY3RvciA9IDEgaGZhY3RvciA9IDEgCmhjb3JyCQl0eXBlID0gQkJSIGZmYWN0b3IgPSAxIGhmYWN0b3IgPSAxIApzcGhhc2UJCWNvcnIgPSBNT09EWQpvcHRpb25zCQl1ZmFjdG9yID0gMSAKSEVBVAkJcGFydGJ1cnltZXRob2QgPSAyMDA5IHNwaWZjbWV0aG9kID0gQkpBIG1waWZjbWV0aG9kID0gQkpBIAoKTEFZRVIJCXVzZSA9J0NIU0EtMDEwJyB0ZW1wPSAyNzMuNyAgbGFiZWwgPSAnQ3BsMScgCm5vZGUJCXR2ZCA9IDEgbWQgPSAxIHRlbXA9IDI3My43ICB1ID0gMgpXRUxMUEkJCXB3c3RhdGljID0gMTI0My44ICBscGkgPSAxRSswNSAgYnBjb3JyZWN0aW9uID0geWVzIGxhYmVsID0gJ0NwbDEnIHVpZD0xICAKJCAtLS0tLS0tLS0tLS0tLS0tLS0tIEVTUCBEQVRBIC0tLS0tLS0tLS0tLS0tLS0tLS0KUHVtcENydgluYW1lID0gJ0ROMTc1MF8xLjEnICBzdGFnZXMgPSAzODAgIHNwZWVkID0gNTQgSHogIHFtaW4gPSA0OTkuNSAgcW1heCA9IDg1My4zMSAgClB1bXBDcnYJbmFtZSA9ICdETjE3NTBfMS4xJyAgUSBiYmwvZCA9ICgwLjQxNjI1LCAzNC44NSwgNjkuMjg0LCAxMDMuNzIsIDEzOC4xNSwgMTcyLjU5LCAyMDcuMDIsIDI0MS40NSwgMjc1Ljg5LCAzMTAuMzIsIDM0NC43NiwgMzc5LjE5LCA0MTMuNjIsIDQ0OC4wNiwgNDgyLjQ5LCA1MTYuOTMsIDU1MS4zNiwgNTg1Ljc5LCA2MjAuMjMsIDY1NC42NiwgNjg5LjA5LCA3MjMuNTMsIDc1Ny45NiwgNzkyLjQsIDgyNi44MywgODYxLjI2LCA4OTUuNywgOTMwLjEzLCA5NjQuNTcsIDE0MDguOCkgClB1bXBDcnYJbmFtZSA9ICdETjE3NTBfMS4xJyAgaGVhZCBmdCA9ICgxMDIyNywgMTAzMzcsIDEwMzIzLCAxMDIyMCwgMTAwNTUsIDk4NTAsIDk2MjMuOCwgOTM4OS45LCA5MTU4LjQsIDg5MzYsIDg3MjYuNCwgODUzMC44LCA4MzQ3LjksIDgxNzUuMSwgODAwNy45LCA3ODQxLjMsIDc2NjkuNCwgNzQ4Ni4yLCA3Mjg1LjksIDcwNjMuNCwgNjgxNC40LCA2NTM2LjEsIDYyMjcuNywgNTg5MC4zLCA1NTI3LjksIDUxNDcuMiwgNDc1OC41LCA0Mzc1LjgsIDQwMTcuNSwgMy4zODU4KSAKUHVtcENydgluYW1lID0gJ0ROMTc1MF8xLjEnICBlZmYgPSAoMC4wODAxNTgsIDYuNjAwMiwgMTIuODgzLCAxOC44OTEsIDI0LjU3NiwgMjkuODk0LCAzNC44MDcsIDM5LjI5MywgNDMuMzQ2LCA0Ni45NzgsIDUwLjIxNCwgNTMuMDkzLCA1NS42NTUsIDU3Ljk0MywgNTkuOTkxLCA2MS44MjcsIDYzLjQ2NywgNjQuOTEyLCA2Ni4xNTQsIDY3LjE2OSwgNjcuOTI0LCA2OC4zNzMsIDY4LjQ2NSwgNjguMTQyLCA2Ny4zNTEsIDY2LjA1MSwgNjQuMjMzLCA2MS45NDEsIDU5LjMwNCwgMC4wNzEzNjgpIAokIC0tLS0tLS0tLS0tLS0tLSBFTkQgRVNQIERBVEEgLS0tLS0tLS0tLS0tLS0tLS0tLQoKCnNlcGFyYXRvcgl0eXBlID0gZ2FzIGVmZiA9IDk5ICBsYWJlbCA9ICdFU1AxIEdhcyBTZXBhcmF0b3InICB1aWQ9MiAKCgoKcHVtcAkJbmFtZSA9ICdETjE3NTBfMS4xJyBzdGFnZXMgPSAzODAgIGZyZXF1ZW5jeSA9ID9GUkVRIEh6ICB2aXNjQ29yciA9IENlbnRyaWxpZnQgIHN0YWdlY2FsY3MgPSBvbiBsYWJlbCA9ICdFU1AxJyBwbG90ID0gb24gIFBvd2VyQT0xIFBvd2VyQiA9MCBocCB1aWQ9MyAKCgoKVFVCSU5HCQlsYWJlbD0nVGJnMScgIHVpZD00IApwaXBlCQlpZCA9IDIuOTkyICBhb2QgPSA5LjYyNSAgd3QgPSAwLjI1NCAgcm91Z2huZXNzID0gMC4wMDEgIGZsb3d0eXBlID0gdHViaW5nIGxhYmVsID0gJ1RiZzEnICAgCmhlYXQJCWlmYyA9IGlucHV0IHUgPSBpbnB1dCAKbm9kZQkJdHZkID0gMSAgICAgICBtZCA9IDEgICAgICAKbm9kZQkJdHZkID0gMCAgICAgICBtZCA9IDAgICAgICAgIHRlbXAgPSA2MCAgdSA9IDIKCldFTExIRUFEIGxhYmVsPSdDSFNBLTAxMCcgdWlkPTUgCgoKRU5ESk9CCg=="
        model_text_pi = "JCNQSVBFU0lNIGJ1aWxkOiAyMDIxLjEuNjg3LjAgb24gV2VkbmVzZGF5LCBNYXkgMywgMjAyMyAxMDozODo0MyBQTQokIENIU0EtMDEwCmpvYgpVTklUUwlpbnB1dCA9IEVORyBvdXRwdXQgPSBFTkcKT1BUSU9OUyBwcG1ldGhvZCA9IDEgdGhtZXRob2QgPSAxClBSSU5UCXByaW1hcnkgYXV4aWxpYXJ5IGVjaG8KTk9QUklOVAlwcm9maWxlIGZsdWlkIGluZmxvdyBoaW4gaG91dCBzbHVnIGl0ZXIKUFJJTlQJQ0FTRVMgPSAxCk9QVElPTlMgICBlb2ZzID0gMQpPUFRJT05TIGd0Z3JhZGllbnQgPSBPTgpFUk9TSU9OIG1vZGVsID0gQVBJIEsgPSAxMDAgZW5nCgpFUk9TSU9OICBSSVNLTElNSVQ9KDAuMDEsMC40LDAuOCwxKQpDT1JST1NJT04gbW9kZWwgPSBERVdBQVJEIGVmZmljaWVuY3kgPSAxIHBoYWN0ID0gMApDT1JST1NJT04gIFJJU0tMSU1JVD0oMC4xLDEsMTAsNTApCgpTTFVHIFNHTFYgPSBNT0RJRklFRApwbG90ZmlsZWRhdGEgIipTVElOR1JBWSBpbmZsb3dzLENwbDEiCgokKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqCiQgICBPUEVSQVRJT04KJCoqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKgpwbG90CWNhc2VkYXRhIGpvYmRhdGEgeHljYXNlID0gZGMKaXRlcm4JdHlwZSA9IGxmbG93IHBvdXQgPSA/UE9VVCBwc2lhICAKCgpwbG90IHByb2ZpbGUgPStnOAoKCnBsb3QgcHJvZmlsZSA9K0Y4TTI0TTVONU81CgpwbG90IHByb2ZpbGUgPStXMjhZMjhVMjhWMjhGOE0yNEFCQ0RFRkdISUpLTE5PU1RVVlhZWkEyQjJDMkQyRTJGMkcySDJJMkoySzJMMlYyVzJYMkEzQjNDM0kzSzNaM0E0QjRDNEo0TTRUNFU0UTdUN04yNE80UDRRNEQ0UTdUN04yNE80UDRRNEQ0UDVRNVQ4VThHOUkxN0oxN1QxN0IyNUMyNUQyNUcyN0gyN0kyNwpwbG90IHN5c3RlbSA9K08xME4xMEFCQ0RFRkdISUk4SzhKS0xOT1BRUlNUVldXM001QzZFNlo4VDEwVTEwVjEwVzEwWDEwWTEwWjEwQTExQjExQzExRjExRzExSDExSTExSjExUTExUjExUzExRjZHNkg2STZKNks2TDZUMTFVMTFWMTFYMTFZMTFaMTFCMTJDMTJEMTJGMTJIMTJJMTJKMTJLMTJVVldYWUwyTTJOMk8yUDJRMlIyWjlON1MyVDJVMkIzQzNEM0UzSzNMM00zTjNPM0s1WlAzUTNTM1QzVjNQNVE1UjVTNVc1WDVFNk02VzZCN1k4UDlROVI5UzkKcGxvdCBzeXN0ZW0gPStUOVY3CiQqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioKJCAgIEZMVUlEUwokKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqCiQqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioKJCBGTFVJRCBEQVRBIC0gQ0hTQS0wMTAgICQgRGVzY3JpcHRpb24gOiAKJCoqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKgpiZWdpbiBmbHVpZCBuYW1lID0gJ0NIU0EtMDEwJwpwcm9wCWFwaSA9IDIwLjUgZ2Fzc2cgPSAwLjY0IHdhdGVyc2cgPSAxLjAyCnJhdGUJd2N1dCA9ID9XQ1VUICBnb3IgPSA1OCAgCmx2aXMJZG92Y29yciA9IGdoZXR0byBsb3Zjb3JyID0gR0hFVFRPIHVvdmNvcnIgPSBnaGV0dG8gCmx2aXMJZW11bHNpb24gPSB3dGlnaHQgYm91bmRhcnkgPSAqY2FsYyAKY29udGFtaW5hbnRzCWNvMiA9IDAgaDJzID0gMCBuMiA9IDAgaDIgPSAwIGNvID0gMCAKY3BmbHVpZAkgICAgCmtmbHVpZAkgICAKYmxhY2tvaWwJY29yciA9IExBU0FURVIgZ2FzemNvcnIgPSBTVEFORElORyAgb2Z2ZmNvcnIgPSBTVEFORElORyAKYmxhY2tvaWwJRU5USEFMUFk9MjAwOQplbmQgZmx1aWQKCgoKQkxBQ0tPSUwgVVNFID0gJ0NIU0EtMDEwJyAKCiQqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioKJCAgIElOTEVUCiQqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioKaW5sZXQJCXRlbXA9IDIxNSAgcHJlcz0gMTkzOSAgbGFiZWwgPSAnQ3BsMScgCgoKJCoqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKgogICBQUk9GSUxFCiQqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioqKioKdmNvcnIJCXR5cGUgPSBIQlIgYW5nbGUgPSA0NC45OTk5OTk5NzcyMjc5IGZmYWN0b3IgPSAxIGhmYWN0b3IgPSAxIApoY29ycgkJdHlwZSA9IEJCUiBmZmFjdG9yID0gMSBoZmFjdG9yID0gMSAKc3BoYXNlCQljb3JyID0gTU9PRFkKb3B0aW9ucwkJdWZhY3RvciA9IDEgCkhFQVQJCXBhcnRidXJ5bWV0aG9kID0gMjAwOSBzcGlmY21ldGhvZCA9IEJKQSBtcGlmY21ldGhvZCA9IEJKQSAKCkxBWUVSCQl1c2UgPSdDSFNBLTAxMCcgdGVtcD0gMjE1ICBsYWJlbCA9ICdDcGwxJyAKbm9kZQkJdHZkID0gNjY4IG1kID0gNjY4IHRlbXA9IDIxNSAgdSA9IDIKV0VMTFBJCQlwd3N0YXRpYyA9IDE5MzkgIGxwaSA9IDEuMDc3ICBicGNvcnJlY3Rpb24gPSB5ZXMgbGFiZWwgPSAnQ3BsMScgdWlkPTEgIApUVUJJTkcJCWxhYmVsPSdDc2cxJyAgdWlkPTIgCnBpcGUJCXd0ID0gMC40ODEyNSAgaWQgPSA5LjYyNSAgcm91Z2huZXNzID0gMC4wMDEgIGZsb3d0eXBlID0gdHViaW5nIGxhYmVsID0gJ0NzZzEnICAgCmhlYXQJCWlmYyA9IGlucHV0IHUgPSBpbnB1dCAKbm9kZQkJdHZkID0gNjY4ICAgICBtZCA9IDY2OCAgICAKbm9kZQkJdHZkID0gMCAgICAgICBtZCA9IDAgICAgICAgIHRlbXAgPSA2MCAgdSA9IDIKCldFTExIRUFEIGxhYmVsPSdDSFNBLTAxMCcgdWlkPTMgCgoKRU5ESk9CCg=="

        head_output_csv_path = os.path.join(self.output_folder_path, "head_output_csv_path.csv")
        pi_output_csv_path = os.path.join(self.output_folder_path, "pi_output_csv_path.csv")
        pipesim_runner = PipesimRunner(head_output_csv_path, pi_output_csv_path)
        
        output_head_pkl_model_path = os.path.join(self.output_folder_path, Config.OUTPUT_HEAD_PKL_MODEL_NAME)
        output_pi_pkl_model_path = os.path.join(self.output_folder_path, Config.OUTPUT_PI_PKL_MODEL_NAME)
        rows_counter = 0
        with open(parameter_combinations_input, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    intake_pressure = float(row['intake_pressure'])
                    discharge_pressure = float(row['discharge_pressure'])
                    motor_temperature = float(row['motor_temperature'])
                    drive_frequency = float(row['drive_frequency'])
                    well_test_water_cut = float(row['well_test_water_cut'])
                    well_test_gor = float(row['well_test_gor'])
                    well_test_api = float(row['well_test_api'])
                    
                    logging.info(f"Running simulation on input: {row}...")
                    pipesim_runner.run_simulations(model_text_pi, model_text_head, intake_pressure, discharge_pressure, motor_temperature, drive_frequency, well_test_water_cut, well_test_gor, well_test_api)
                    logging.info("Simulation completed...")
                    
                    rows_counter+=1
                    if(rows_counter % 1000 == 0):
                        logging.info("New 1000 cases added. Train the ML Model...")
                        
                        self.train_models(head_output_csv_path, pi_output_csv_path, output_head_pkl_model_path, output_pi_pkl_model_path)
                        os.remove(head_output_csv_path)
                        os.remove(pi_output_csv_path)
                        
                        logging.info("Models successfully trained.")
                except Exception as e:
                    logging.info(e)
        
        return output_head_pkl_model_path, output_pi_pkl_model_path

    def train_models(self, head_output_csv_path, pi_output_csv_path, output_head_pkl_model_path, output_pi_pkl_model_path):
        logging.info("Train HEAD model")
        head_ml_model_generator = MlModelGenerator(head_output_csv_path, self.HEAD_FEATURE_COLUMNS, self.TARGET_COLUMN)
        head_ml_model_generator.train(output_head_pkl_model_path)
                        
        logging.info("Train PI model")
        pi_ml_model_generator = MlModelGenerator(pi_output_csv_path, self.PI_FEATURE_COLUMNS, self.TARGET_COLUMN)
        pi_ml_model_generator.train(output_pi_pkl_model_path)


if __name__ == '__main__':
    FlushStreamHandler.setup_logging()

    timer_service = TimerService()
    timer_service.start_timer()
    
    if(os.path.exists(Config.OUTPUT_FOLDER_PATH) == False):
        os.mkdir(Config.OUTPUT_FOLDER_PATH)

    runner = Runner(Config.OUTPUT_FOLDER_PATH)
    
    
    

    pkl_model_path = r"D:\Git\chemical-pipesim-ai\Output\head_model_output.pkl"
    # if(os.path.exists(pkl_model_path)):
    #     with open(pkl_model_path, "rb") as f:
    #         model = joblib.load(f)
            
    #         import joblib
    #         import matplotlib.pyplot as plt
    #         import numpy as np

    #         # Extract preprocessor and classifier
    #         preprocessor = model.named_steps['preprocessor']
    #         clf = model.named_steps['classifier']

    #         # Get original feature names
    #         numeric_features = preprocessor.transformers_[0][2]  # The column list from 'num'
    #         # One-hot encoded features from 'cat' are empty in your case, but here's how it would work:
    #         categorical_features = preprocessor.transformers_[1][2]

    #         # Get transformed feature names (only numeric in your case)
    #         feature_names = list(numeric_features)  # Because categorical_features is empty

    #         # Plot feature importances
    #         importances = clf.feature_importances_
    #         indices = np.argsort(importances)[::-1]

    #         plt.figure(figsize=(10, 6))
    #         plt.title("Feature Importances (Random Forest)")
    #         plt.bar(range(len(importances)), importances[indices], align='center')
    #         plt.xticks(range(len(importances)), [feature_names[i] for i in indices], rotation=45, ha='right')
    #         plt.tight_layout()
    #         plt.show()




    logging.info("Generating Training Data...")
    output_head_pkl_model_path, output_pi_pkl_model_path = runner.generate_models()
    logging.info(f"Generation completed: {timer_service.get_elapsed_time_in_sec()}")

    logging.info("Test the ML Models...")
    # --- Example usage ---
    sample = {'intake_pressure': 750, 'discharge_pressure': 1000, 'motor_temperature': 150, 'drive_frequency': 80, 'well_test_water_cut': 50, 'well_test_gor': 10, 'well_test_api': 10}
    predicted_class_before_train = MlModelGenerator.predict(output_head_pkl_model_path, sample)
    print("Prediction for new sample:", predicted_class_before_train)
    
    
    # --- Retrain Model ---
    #new_head_input_data_csv = "D:\Git\chemical-pipesim-ai\Output\head_output_csv_path-retrained.csv"
    #new_pi_input_data_csv = "D:\Git\chemical-pipesim-ai\Output\head_output_csv_path-retrained.csv"
    #runner.train_models(new_head_input_data_csv, new_pi_input_data_csv, output_head_pkl_model_path, output_pi_pkl_model_path)
    predicted_class_after_train = MlModelGenerator.predict(output_head_pkl_model_path, sample)
    print("Prediction for new sample after retrain:", predicted_class_after_train)
    
    