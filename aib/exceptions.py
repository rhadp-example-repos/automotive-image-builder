"""AIB Exceptions module"""


class AIBException(Exception):
    pass


class InvalidOption(AIBException):
    def __init__(self, option, value):
        self.option = option
        self.value = value

    def __str__(self):
        return (
            f"Invalid value passed to {self.option}: '{self.value}': "
            "should be key=value"
        )


class MissingSection(AIBException):
    def __init__(self, section):
        self.section = section

    def __str__(self):
        return f"No {self.section} section in manifest"


class DefineFileError(AIBException):
    pass


class ManifestParseError(AIBException):
    def __init__(self, manifest_path):
        self.manifest = manifest_path

    def __str__(self):
        return f"Error parsing {self.manifest}"


class SimpleManifestParseError(AIBException):
    def __init__(self, manifest_path, errors):
        self.manifest = manifest_path
        self.errors = errors

    def __str__(self):
        return f"Error parsing {self.manifest}: " + "\n".join(
            e.message for e in self.errors
        )


class UnsupportedExport(AIBException):
    def __init__(self, export):
        self.export = export

    def __str__(self):
        return f"Unsupported export '{self.export}'"
