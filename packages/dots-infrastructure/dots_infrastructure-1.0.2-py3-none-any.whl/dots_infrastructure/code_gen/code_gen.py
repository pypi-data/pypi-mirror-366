from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from re import sub

from dots_infrastructure.code_gen.code_meta_data import CalculationServiceMetaData

TEMPLATE_DIR = Path(__file__).parent / "templates"
JINJA_ENV = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

class CodeGenerator:

    helics_data_type_to_python_data_type = {
        "STRING" : "str",
        "DOUBLE" : "float",
        "INT" : "int",
        "COMPLEX" : "complex",
        "VECTOR" : "List",
        "COMPLEX_VECTOR" : "List[complex]",
        "BOOLEAN" : "bool",
        "TIME" : "int"
    }

    def camel_case(self, s):
        s = sub(r"(_|-| )+", " ", s).title().replace(" ", "")
        return ''.join([s[0].upper(), s[1:]])
    
    def get_python_name(self, s):
        return sub(r"(_|-| )+", " ", s).lower().replace(" ", "_")
    
    def get_base_class_name(self, class_name):
        return f'{class_name}Base'

    def render_template(self, template_path: Path, output_dir: Path, output_file: Path, **data):
        # jinja expects a string, representing a relative path with forward slashes
        template_path_str = str(template_path.relative_to(TEMPLATE_DIR)).replace("\\", "/")
        template = JINJA_ENV.get_template(template_path_str)
        JINJA_ENV.trim_blocks = True
        JINJA_ENV.lstrip_blocks = True

        output = template.render(**data)
        output_dir.mkdir(parents=True, exist_ok=True)
        with output_file.open(mode="w", encoding="utf-8") as output_file:
            output_file.write(output)

    def _extract_valid_python_datatype(self, data_type : str, name : str):
        if data_type in self.helics_data_type_to_python_data_type:
            return self.helics_data_type_to_python_data_type[data_type]
        else:
            raise ValueError(f"Unsupported helics data type: {data_type} for {name}, expected one of {", ".join(self.helics_data_type_to_python_data_type.keys())}")

    def render_calculation_service(self, template_path: Path, json_data : str, output_dir: Path):

        dataset_meta_data: CalculationServiceMetaData = CalculationServiceMetaData.schema().loads(json_data)

        class_name = self.camel_case(dataset_meta_data.name)
        base_class_name = self.get_base_class_name(class_name)
        file_name = self.get_python_name(dataset_meta_data.name)
        output_file = output_dir / f"{file_name}_base.py"

        for calculation in dataset_meta_data.calculations:
            calculation.calculation_function_name = calculation.name.replace(" ", "_").replace("-", "_").replace(".", "_")
            for input in calculation.inputs:
                input.python_name = self.get_python_name(input.name)
                self._extract_valid_python_datatype(input.data_type, input.name)
            for output in calculation.outputs:
                output.python_name = self.get_python_name(output.name)
                output.python_data_type = self._extract_valid_python_datatype(output.data_type, output.name)

        self.render_template(
            template_path=template_path,
            output_dir=output_dir,
            output_file=output_file,
            calculations=dataset_meta_data.calculations,
            name=base_class_name,
            esdl_type=dataset_meta_data.esdl_type
        )

    def render_output_dataclasses(self, template_path: Path, json_data : str, output_dir: Path):
        dataset_meta_data: CalculationServiceMetaData = CalculationServiceMetaData.schema().loads(json_data)

        file_name = self.get_python_name(dataset_meta_data.name)
        output_file = output_dir / f"{file_name}_dataclasses.py"

        for calculation in dataset_meta_data.calculations:
            calculation.calculation_output_class_name = f"{self.camel_case(calculation.name)}Output"
            for output in calculation.outputs:
                output.python_data_type = self._extract_valid_python_datatype(output.data_type, output.name)
                output.python_name = self.get_python_name(output.name)
                
        self.render_template(
            template_path=template_path,
            output_dir=output_dir,
            output_file=output_file,
            calculations=dataset_meta_data.calculations
        )

    def render_documentation(self, template_path: Path, json_data : str, output_dir: Path):
        dataset_meta_data: CalculationServiceMetaData = CalculationServiceMetaData.schema().loads(json_data)

        output_file = output_dir / f"{dataset_meta_data.name}.md"

        dataset_meta_data.relevant_links = [] if dataset_meta_data.relevant_links is None else dataset_meta_data.relevant_links

        self.render_template(
            template_path=template_path,
            output_dir=output_dir,
            output_file=output_file,
            calculations=dataset_meta_data.calculations,
            name=dataset_meta_data.name,
            esdl_type=dataset_meta_data.esdl_type,
            description=dataset_meta_data.description,
            relevant_links=dataset_meta_data.relevant_links
        )

    def code_gen(self, input : str, code_output_dir : str, documentation_ouput_dir : str):
        render_funcs = {
            "calculation_service": (self.render_calculation_service, code_output_dir),
            "cs_documentation": (self.render_documentation, documentation_ouput_dir),
            "cs_data_classes": (self.render_output_dataclasses, code_output_dir)
        }

        # render attribute classes
        for template_name, render_func_output_pair in render_funcs.items():
            for template_path in TEMPLATE_DIR.rglob(f"{template_name}.*.jinja"):
                render_func = render_func_output_pair[0]
                output_dir = Path(render_func_output_pair[1])
                output_path = output_dir 
                output_path.parent.mkdir(parents=True, exist_ok=True)
                print(f"Generating file in {output_path}")
                render_func(template_path=template_path, json_data=input, output_dir=output_path)

