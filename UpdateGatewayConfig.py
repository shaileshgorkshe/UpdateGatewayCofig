from subprocess import Popen, PIPE
import xml.etree.ElementTree as ET
import subprocess
import sys
import time
import os

def service_status(service_name):
    """ Check if the service is running. """
    result = subprocess.run(["sc", "query", service_name], capture_output=True, text=True)
    return "RUNNING" in result.stdout

def stop_service(service_name):
    print(f"Checking if {service_name} is running...")
    if service_status(service_name):
        try:
            subprocess.run(["net", "stop", service_name], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error stopping {service_name}: {e}")
            print("The service might not be running.")
    else:
        print(f"{service_name} is not running, skipping stop.")

def start_service(service_name):
    try:
        subprocess.run(["net", "start", service_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting {service_name}: {e}")
        print("Please check the Event Viewer for more details.")

def replace_realm_value(xml_file, ns, customer):
    print(f"Updating realm value to '{customer}' in the XML file...")
    
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Namespace handling
    namespaces = {'ns0': f'{ns}'}
    # Find and replace the <ns0:name> value under <ns0:realm>
    realm_name_element = root.find(".//ns0:realm/ns0:name", namespaces)
    if realm_name_element is not None:
        original_value = realm_name_element.text
        print(f"Original realm value: {original_value}")
        realm_name_element.text = customer

        # Replace all occurrences of the original value in the XML
        for elem in root.iter():
            if elem.text and original_value in elem.text:
                elem.text = elem.text.replace(original_value, customer)

        # Write changes back to the XML file
        tree.write(xml_file)
        print(f"Replaced '{original_value}' with '{customer}' successfully.")
    else:
        print("No <ns0:realm> or <ns0:name> found in the XML.")

def main(service_name, xml_file, ns, customer):
    stop_service(service_name)
    time.sleep(3)  # Wait for 3 seconds to ensure the service has fully stopped
    replace_realm_value(xml_file, ns, customer)
    start_service(service_name)
    time.sleep(3)   # Wait for 3 seconds to ensure the service has fully started

if __name__ == "__main__":
    # Check if the script was called with the required argument
    if len(sys.argv) != 2:
        print("Usage: python script.py <customer>")
        sys.exit(1)

    # Get the new realm value from the command-line argument
    customer = sys.argv[1]
    
    service_name = "KWICService"    #Service Name    
    xml_file = r"C:\Softwares\kwic-5.9.29-windows\kwic-5.9.29\conf\kwic-config.xml" # Path to the XML file
    ns = r"http://xmlns.kaazing.com/2012/09/gateway"
    
    # Call the main function
    main(service_name, xml_file, ns, customer)