#   Hyrrokkin - a library for building and running executable graphs
#
#   MIT License - Copyright (C) 2022-2025  Visual Topology Ltd

from hyrrokkin_engine.configuration_interface import ConfigurationInterface
import json

from .text_input_node import TextInputNode
from .word_frequency_node import WordFrequencyNode
from .table_display_node import TableDisplayNode

class TextgraphConfiguration(ConfigurationInterface):

    def __init__(self, services):
        self.services = services

    async def create_node(self, node_type_id, node_services):
        match node_type_id:
            case "text_input_node": return TextInputNode(node_services)
            case "word_frequency_node": return WordFrequencyNode(node_services)
            case "table_display_node": return TableDisplayNode(node_services)
            case _: return None

    async def encode(self, value, link_type):
        if value is not None:
            if link_type == "text":
                return value.encode("utf-8")
            elif link_type == "table":
                return json.dumps(value).encode("utf-8")
        return None

    async def decode(self, encoded_bytes, link_type):
        if encoded_bytes is not None:
            if link_type == "text":
                return encoded_bytes.decode("utf-8")
            elif link_type == "table":
                return json.loads(encoded_bytes.decode("utf-8"))
        return None





