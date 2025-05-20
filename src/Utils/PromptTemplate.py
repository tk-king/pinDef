from jinja2 import BaseLoader, Environment

class PromptTemplate():
    def __init__(self, template):
        self.template_string = template
        self.template = Environment(loader=BaseLoader).from_string(template)

    @classmethod
    def from_string(cls, string):
        # Class method to initialize from a string
        return cls(string)

    def invoke(self, input=None, **kwargs):
        # Handle various input types
        if isinstance(input, dict):
            render_input = {**input, **kwargs}
        else:
            render_input = kwargs

        # Render the template with the combined input
        return self.template.render(**render_input)