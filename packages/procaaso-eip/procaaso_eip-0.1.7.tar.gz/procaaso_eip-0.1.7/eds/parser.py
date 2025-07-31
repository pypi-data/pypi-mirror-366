import click
import re
import yaml
import os


class EDSParser:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_eds(self):
        self.content = self.read_file()
        self.params = self.extract_params()
        self.connections = self.extract_connections()
        self.device_info = self.extract_device_info()

    def read_file(self):
        with open(self.file_path, "r") as file:
            return file.read()

    def extract_params(self):
        param_pattern = r"Param\d+ =[\s\S]*?;"
        params = re.findall(param_pattern, self.content)
        param_info = {}
        for param in params:
            name, param_dict = self.parse_param(param)
            param_info[name] = param_dict
        return param_info

    def parse_param(self, param_str):
        lines = param_str.strip().split("\n")
        param = {
            "name": lines[0].split("=")[0].strip(),
            "min": None,
            "max": None,
            "default": None,
        }
        for line in lines[1:]:
            if "min" in line and "max" in line and "default" in line:
                values = line.split(",")
                param["min"] = values[0].strip()
                param["max"] = values[1].strip()
                param["default"] = values[2].strip().split(";")[0].strip()
            elif "name" in line:
                values = line.split(",")
                param["name"] = values[0].strip().strip('"')
        return lines[0].split("=")[0].strip(), param

    def extract_connections(self):
        connection_pattern = r"Connection\d+ =[\s\S]*?;"
        connections = re.findall(connection_pattern, self.content)
        connection_info = {}
        for connection in connections:
            connection_dict = self.parse_connection(connection)
            connection_info[connection_dict["name"]] = connection_dict
        return connection_info

    def parse_connection(self, connection_str):
        lines = connection_str.strip().split("\n")
        connection = {
            "name": lines[0].split("=")[0].strip(),
            "input": {"assembly": "", "rpi": "", "size": ""},
            "output": {"assembly": "", "rpi": "", "size": ""},
            "path": "",
        }
        for line in lines[1:]:
            if "=" in line:
                key, value = line.split("=", 1)
                if "T->O RPI, size, format" in line:
                    (
                        connection["input"]["rpi"],
                        connection["input"]["size"],
                        connection["input"]["assembly"],
                    ) = self.parse_rpi_size_format(value)
                elif "O->T RPI, size, format" in line:
                    (
                        connection["output"]["rpi"],
                        connection["output"]["size"],
                        connection["output"]["assembly"],
                    ) = self.parse_rpi_size_format(value)
            elif "$" in line:
                if "T->O RPI, size, format" in line:
                    (
                        connection["input"]["rpi"],
                        connection["input"]["size"],
                        connection["input"]["assembly"],
                    ) = self.parse_rpi_size_format(line.split("$")[0].strip())
                elif "O->T RPI, size, format" in line:
                    (
                        connection["output"]["rpi"],
                        connection["output"]["size"],
                        connection["output"]["assembly"],
                    ) = self.parse_rpi_size_format(line.split("$")[0].strip())
            elif "20 04" in line:
                connection["path"] = line.split(";")[0].strip().strip('"')
        return connection

    def parse_rpi_size_format(self, value):
        parts = value.split(",")
        rpi = self.get_param_details(parts[0].strip())
        size = self.get_param_details(parts[1].strip())
        assembly = parts[2].strip() if len(parts) > 2 else ""
        return rpi, size, assembly

    def get_param_details(self, param_name):
        if param_name in self.params:
            param = self.params[param_name]
            return {
                "min": param["min"],
                "max": param["max"],
                "default": param["default"],
            }
        return param_name

    def substitute_params_with_hex(self, string):
        def replace_match(match):
            param_name = match.group(1)
            param_value = self.params.get(param_name, {}).get("default", match.group(0))
            if isinstance(param_value, str) and param_value.isdigit():
                param_value = int(param_value)
            if isinstance(param_value, int):
                param_value_hex = (
                    f"{param_value:02X}"  # Convert to hex with at least 2 digits
                )
            else:
                param_value_hex = match.group(0)  # Leave unchanged if not a valid int
            return param_value_hex

        # Use regex to find placeholders and substitute values
        pattern = re.compile(r"\[([^\]]+)\]")
        result = pattern.sub(replace_match, string)
        return result

    def get_path_info(self, connection_name):
        connection = self.connections[connection_name]
        if "Param" in connection["path"]:
            connection["path"] = self.substitute_params_with_hex(connection["path"])
        return connection["path"]

    def parse_path_for_assemblies(self, path):
        # Split the path into components and identify the assemblies
        parts = path.split()
        configuration_assembly = int(parts[3], 16)
        output_assembly = int(parts[5], 16)
        input_assembly = int(parts[7], 16)
        return {
            "configuration_assembly": configuration_assembly,
            "input_assembly": input_assembly,
            "output_assembly": output_assembly,
        }

    def get_assembly_info(
        self,
        connection_name="Connection1",
        rpi_select="default",
        size="default",
        rpi_default=100000,
    ):
        path = self.get_path_info(connection_name)
        assemblies = self.parse_path_for_assemblies(path)

        # Also get RPI values from the connection data
        connection = self.connections[connection_name]
        input_rpi = connection["input"]["rpi"]
        output_rpi = connection["output"]["rpi"]

        if input_rpi != "" and rpi_select != "override":
            assemblies["input_rpi"] = int(input_rpi[rpi_select])
            assemblies["output_rpi"] = int(output_rpi[rpi_select])
        else:
            assemblies["input_rpi"] = rpi_default
            assemblies["output_rpi"] = rpi_default

        input_size = connection["input"]["size"]
        output_size = connection["output"]["size"]
        if isinstance(input_size, str):
            int(input_size)
        else:
            assemblies["input_size"] = int(input_size[size])
        if isinstance(output_size, str):
            int(output_size)
        else:
            assemblies["output_size"] = int(output_size[size])

        return assemblies

    def extract_device_info(self):
        device_info = {}
        device_info_pattern = r"\[Device\][\s\S]*?\[.*?\]"
        match = re.search(device_info_pattern, self.content)
        if match:
            device_info_str = match.group(0)
            device_info = self.parse_device_info(device_info_str)
        return device_info

    def parse_device_info(self, device_info_str):
        lines = device_info_str.strip().split("\n")
        device_info = {}
        for line in lines:
            if "VendName" in line:
                key, value = line.split("=", 1)
                print(value.strip().strip(";").strip('"'))
                device_info[key.strip()] = value.strip().strip(";").strip('"')
            elif "ProdName" in line:
                key, value = line.split("=", 1)
                print(value.strip().strip(";").strip('"'))
                device_info[key.strip()] = value.strip().strip(";").strip('"')
            elif "ProdTypeStr" in line:
                key, value = line.split("=", 1)
                print(value.strip().strip(";").strip('"'))
                device_info[key.strip()] = value.strip().strip(";").strip('"')
        return device_info

    def generate_io_map(
        self,
        file_path,
        unique_id,
        address,
        component="Component Name",
        instrument="Instrument Name",
        attribute="Attribute Name",
        io_key="IO Map Name",
    ):
        connection_name = "Connection1"  # You may need to adjust this based on your specific connection name
        assembly_info = self.get_assembly_info(connection_name)

        # Check if the file exists and load existing content
        if os.path.exists(file_path):
            with open(file_path, "r") as yaml_file:
                existing_data = yaml.safe_load(yaml_file)
        else:
            existing_data = {}

        # Create new data to be added
        new_io_map = {
            component: {
                "instruments": {
                    instrument: {
                        "attributes": {
                            attribute: {
                                "ioMaps": {
                                    io_key: {
                                        "unique_id": unique_id,
                                        "model": self.device_info.get("ProdName", ""),
                                        "vendor": self.device_info.get("VendName", ""),
                                        "description": self.device_info.get(
                                            "ProdTypeStr", ""
                                        ),  # Description might need a different approach if it is not in EDS
                                        "protocol": "Ethernet I/P",  # Assuming protocol as a constant; modify as needed
                                        "address": address,
                                        "configuration_assembly": str(
                                            assembly_info.get("configuration_assembly")
                                        ),
                                        "input_assembly": str(
                                            assembly_info.get("input_assembly")
                                        ),
                                        "input_rpi": str(
                                            assembly_info.get("input_rpi")
                                        ),
                                        "input_size": str(
                                            assembly_info.get("input_size")
                                        ),
                                        "output_assembly": str(
                                            assembly_info.get("output_assembly")
                                        ),
                                        "output_rpi": str(
                                            assembly_info.get("output_rpi")
                                        ),
                                        "output_size": str(
                                            assembly_info.get("output_size")
                                        ),
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        # Update the existing data with the new data
        existing_data.update(new_io_map)

        # Write the updated data back to the YAML file
        with open(file_path, "w") as yaml_file:
            yaml.dump(existing_data, yaml_file, default_flow_style=False)


@click.command()
@click.argument("file_path")
@click.option("-o", "--output", default="io_map.yaml", help="Output YAML file path")
@click.option("-uid", "--unique_id", required=True, help="Unique ID of the device")
@click.option("-add", "--address", required=True, help="Device address")
@click.option(
    "-c", "--component", default="Replace_Me_With_Component_Name", help="Component name"
)
@click.option(
    "-i",
    "--instrument",
    default="Replace_Me_With_Instrument_Name",
    help="Instrument name",
)
@click.option(
    "-a", "--attribute", default="Replace_Me_With_Attribute_Name", help="Attribute name"
)
@click.option("-io", "--io_key", default="io", help="IO key")
def main(
    file_path, output, unique_id, address, component, instrument, attribute, io_key
):
    parser = EDSParser(file_path)
    parser.load_eds()
    parser.generate_io_map(
        file_path=output,
        unique_id=unique_id,
        address=address,
        component=component,
        instrument=instrument,
        attribute=attribute,
        io_key=io_key,
    )


if __name__ == "__main__":
    main()
