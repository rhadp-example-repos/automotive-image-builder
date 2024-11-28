import yaml
import collections


# pylint: disable=too-many-ancestors
class YamlOrderedLoader(yaml.Loader):
    def construct_mapping(self, node, deep=False):
        if not isinstance(node, yaml.MappingNode):
            raise yaml.constructor.ConstructorError(
                None, None,
                f"expected a mapping node, but found {node.id}",
                node.start_mark)
        mapping = collections.OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, collections.abc.Hashable):
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping", node.start_mark,
                    "found unhashable key", key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping

    def construct_yaml_map(self, node):
        data = collections.OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)


yaml.add_constructor('tag:yaml.org,2002:map',
                     YamlOrderedLoader.construct_yaml_map)


def yaml_load_ordered(source):
    return yaml.load(source, YamlOrderedLoader)
