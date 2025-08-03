#################################################################################
# Eclipse Tractus-X - Software Development KIT
#
# Copyright (c) 2025 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License, Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the
# License for the specific language govern in permissions and limitations
# under the License.
#
# SPDX-License-Identifier: Apache-2.0
#################################################################################

import traceback
import logging
from tractusx_sdk.dataspace.tools import op
from tractusx_sdk.dataspace.tools.validate_submodels import submodel_schema_finder
import copy

class SammSchemaContextTranslator:
    def __init__(self, logger:logging.Logger=None, verbose:bool=False):
        self.baseSchema = {}
        self.rootRef = "#"
        self.refKey = "$ref"
        self.path_sep = "#/"
        self.actualPathSep = "/-/"
        self.refPathSep = "/"
        self.propertiesKey = "properties"
        self.logger = logger
        self.verbose = verbose
        self.itemKey = "items"
        self.schemaPrefix = "schema"
        self.aspectPrefix = "aspect"
        self.contextPrefix = "@context"
        self.recursionDepth = 2
        self.depth = 0
        self.initialJsonLd = {
            "@version": 1.1,
            self.schemaPrefix: "https://schema.org/"
        }
        self.contextTemplate = {
            "@version": 1.1,
            "id": "@id",
            "type": "@type"
        }

    def fetch_schema_from_semantic_id(self, semantic_id, link_core: str = 'https://raw.githubusercontent.com/eclipse-tractusx/sldt-semantic-models/main/'):
        """
        Fetch a JSON schema using the semantic ID and the submodel schema finder.
        
        Args:
            semantic_id (str): The semantic ID, e.g., "urn:samm:io.catenax.pcf:7.0.0#Pcf"
        
        Returns:
            dict or None: The fetched schema dictionary, or None if failed
        """
        try:
            if self.verbose and self.logger:
                self.logger.info(f"Fetching schema for semantic ID: {semantic_id}")
            
            # Use the existing submodel_schema_finder from the SDK
            result = submodel_schema_finder(semantic_id, link_core=link_core)
            
            if result['status'] == 'ok':
                schema_dict = result['schema']
                if self.verbose and self.logger:
                    self.logger.info(f"Successfully fetched schema: {result['message']}")
                return schema_dict
            else:
                if self.logger:
                    self.logger.error(f"Failed to fetch schema: {result.get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error fetching schema for {semantic_id}: {e}")
            return None

    def _prepare_schema_and_context(self, semantic_id: str, schema: dict = None, link_core: str = 'https://raw.githubusercontent.com/eclipse-tractusx/sldt-semantic-models/main/') -> tuple:
        """
        Common preparation logic for both flattened and nested JSON-LD context generation.
        
        Args:
            semantic_id (str): The semantic ID of the SAMM model
            schema (dict, optional): The schema to convert. If None, will auto-fetch.
            link_core (str): Base URL for fetching schemas
            
        Returns:
            tuple: (schema, aspect_name, jsonld_context, response_context)
        """
        # If schema is None, try to fetch it using the semantic ID
        if schema is None:
            if self.verbose and self.logger:
                self.logger.info(f"Schema not provided, attempting to fetch from semantic ID: {semantic_id}")
            schema = self.fetch_schema_from_semantic_id(semantic_id, link_core=link_core)
            if schema is None:
                raise Exception(f"Could not fetch schema for semantic ID: {semantic_id}")
        
        self.baseSchema = copy.copy(schema)
        semantic_parts = semantic_id.split(self.rootRef)  
        if((len(semantic_parts) < 2) or (semantic_parts[1] == '')):
            raise Exception("Invalid semantic id, missing the model reference!")
        
        aspect_name = semantic_parts[1]
        self.aspectPrefix = aspect_name
        
        # Create the node context for the schema
        jsonld_context = self.create_node(property=schema)
        
        if jsonld_context is None:
            raise Exception("It was not possible to generated the json-ld!")
        
        # Start with the basic JSON-LD structure
        response_context = copy.copy(self.initialJsonLd)
        
        # Add semantic path reference
        semantic_path = semantic_parts[0]
        response_context[self.aspectPrefix] = semantic_path + self.rootRef
        
        return schema, aspect_name, jsonld_context, response_context

    def schema_to_jsonld(self, semantic_id: str, schema: dict = None, link_core: str = 'https://raw.githubusercontent.com/eclipse-tractusx/sldt-semantic-models/main/') -> dict:
        """
        Convert a SAMM schema to a flattened JSON-LD context suitable for verifiable credentials.
        
        This variant creates a flattened context where the semantic model properties are mapped
        directly at the root level of the context, rather than nested under the aspect name.
        This is suitable for verifiable credentials where the credentialSubject contains
        the semantic model properties directly without nesting.
        
        Args:
            semantic_id (str): The semantic ID of the SAMM model
            schema (dict, optional): The schema to convert. If None, will auto-fetch.
            link_core (str): Base URL for fetching schemas
            
        Returns:
            dict: Flattened JSON-LD context
        """
        try:
            schema, _, jsonld_context, response_context = self._prepare_schema_and_context(
                semantic_id, schema, link_core
            )
            
            # Flatten the properties to root level
            if "@context" in jsonld_context and isinstance(jsonld_context["@context"], dict):
                # Merge the properties from the nested context to the root level
                nested_context = jsonld_context["@context"]
                for key, value in nested_context.items():
                    if key not in ["@version", "id", "type"]:  # Skip standard JSON-LD keys
                        response_context[key] = value
            
            # Add description if available
            if "description" in schema:
                response_context["@definition"] = schema["description"]
                
            return {
                "@context": response_context
            }
        except:
            traceback.print_exc()
            raise Exception("It was not possible to create flattened jsonld schema")

    def schema_to_jsonld_nested(self, semantic_id: str, schema: dict = None, link_core: str = 'https://raw.githubusercontent.com/eclipse-tractusx/sldt-semantic-models/main/') -> dict:
        """
        Convert a SAMM schema to a nested JSON-LD context.
        
        This variant creates a nested context where the semantic model properties are grouped
        under the aspect name in the context structure.
        
        Args:
            semantic_id (str): The semantic ID of the SAMM model
            schema (dict, optional): The schema to convert. If None, will auto-fetch.
            link_core (str): Base URL for fetching schemas
            
        Returns:
            dict: Nested JSON-LD context
        """
        try:
            schema, aspect_name, jsonld_context, response_context = self._prepare_schema_and_context(
                semantic_id, schema, link_core
            )
            
            # Create nested structure under aspect name
            jsonld_context["@id"] = ":".join([self.aspectPrefix, aspect_name])
            response_context[aspect_name] = jsonld_context
            
            # Add description if available
            if "description" in schema:
                response_context[aspect_name]["@context"]["@definition"] = schema["description"]
                
            return {
                "@context": response_context
            }
        except:
            traceback.print_exc()
            raise Exception("It was not possible to create jsonld schema")
    

    def expand_node(self, ref, actualref, key=None):
        try:
            ## Ref must not be None
            if (ref is None): return None
            ## Get expanded node
            expandedNode = self.get_schema_ref(ref=ref, actualref=actualref)

            newRef = self.actualPathSep.join([actualref, ref])

            if(expandedNode is None): return None
            return self.create_node(property=expandedNode, actualref=newRef, key=key)
        except:
            traceback.print_exc()
            raise Exception("It was not possible to expand the node")

    def create_node(self, property, actualref="", key=None):
        try:
            ## Schema must be not none and type must be in the schema
            if (property is None) or (not "type" in property): return None
            
            ## Start by creating a simple node
            node = self.create_simple_node(property=property, key=key)

            ## If is not possible to create the simple node it is not possible to create any node
            if(node is None): return None

            propertyType = property["type"]

            if propertyType == "object":
                return self.create_object_node(property=property, node=node, actualref=actualref)
            
            if propertyType == "array":
                return self.create_array_node(property=property, node=node, actualref=actualref)
            
            return self.create_value_node(property=property, node=node)
        except:
            traceback.print_exc()
            raise Exception("It was not possible to create the node")

    def create_value_node(self, property, node):
        try:
            ## If type exists add definition to the node
            if not ("type" in property): return None
            
            node["@type"] = self.schemaPrefix+":"+property["type"]
            return node
        except:
            traceback.print_exc()
            raise Exception("It was not possible to create value node")
    
    def create_object_node(self, property, node, actualref):
        try:
            ## If object has not the properties key
            if not (self.propertiesKey in property): return None
            
            properties = property[self.propertiesKey]

            node[self.contextPrefix] = self.create_properties_context(properties=properties, actualref=actualref)
            return node
        except:
            traceback.print_exc()
            raise Exception("It was not possible to create object node")

    def create_array_node(self, property, node, actualref=None):
        try:
            ## If array node has not the item key
            if not (self.itemKey in property): return None
            
            item = property[self.itemKey]
            node["@container"] = "@list" 

            ## If list is with different types of data, dont specify a type
            if(isinstance(item, list)):
                return node

            if not (self.refKey in item):
                return self.create_value_node(property=item, node=node)

            node[self.contextPrefix] = self.create_item_context(item=item, actualref=actualref)
            return node
        except:
            traceback.print_exc()
            raise Exception("It was not possible to create the array node")


    def filter_key(self, key):
        cleanKey = key
        if ("@" in cleanKey): 
            cleanKey = cleanKey.replace("@","")
        
        if (" " in cleanKey): 
            cleanKey = cleanKey.replace(" ","-")
        return cleanKey


    def create_properties_context(self, properties, actualref):
        try:
            ## If no key is provided or node is empty
            if(properties is None): return None
            
            ## If no key is found
            if(not isinstance(properties, dict)): return None
            
            ## If no keys are provided in the properties
            if(len(properties.keys())  == 0): return None
            
            ## Create new context dict from template
            newContext = copy.copy(self.contextTemplate)
            oldProperties = copy.copy(properties)

            ## Fill the node context with the properties
            for propKey, prop in oldProperties.items():
                key = self.filter_key(key=propKey)
                prop = self.create_node_property(key=key, node=prop, actualref=actualref)
                if (prop is None):
                    continue
                

                newContext[key] = prop

            ## Add context properties to the node context
            return newContext
        except:
            traceback.print_exc()
            raise Exception("It was not possible to create properties context")
        
    def create_item_context(self, item, actualref):
        try:
            ## If no key is provided or node is empty
            if(item is None): return None
            
            newContext = copy.copy(self.contextTemplate)
            ref = item[self.refKey]
            nodeItem = self.expand_node(ref=ref, actualref=actualref)

            ## If was not possible to get the reference return None
            if nodeItem is None: return None

            newContext.update(nodeItem)
            ## Overite the existing description of ref item

            if not ("description" in item):
                return newContext
            
            if not ("@context" in newContext):
                newContext["@context"] = dict()

            newContext["@context"]["@definition"]  = item["description"] 

            return newContext
        except:
            traceback.print_exc()
            raise Exception("It was not possible to create the item context")
        
    def create_node_property(self, key, node, actualref):
        try:
            ## If no key is provided or node is empty
            if(key is None) or (node is None): return None

            ## Ref property must exist in a property inside properties
            if not (self.refKey in node): return None

            ## Get reference from the base schema
            ref = node[self.refKey]
            nodeProperty = self.expand_node(ref=ref, actualref=actualref, key=key)

            ## If was not possible to get the reference return None
            if nodeProperty is None: return None

            ## Overite the existing description of ref property
            if not ("description" in node):
                return nodeProperty
            
            if not ("@context" in nodeProperty):
                nodeProperty["@context"] = dict()

            nodeProperty["@context"]["@definition"]  = node["description"]

            return nodeProperty
        except:
            traceback.print_exc()
            raise Exception("It was not possible to create node property")


    def create_simple_node(self, property, key=None):
        """
        Creates a simple node with key and object from a schema property
        Receives:
            key: :str: attribute key
            node: :dict: contains the node object with or without description and type
        Returns:
            response: :dict: json ld simple node with the information of the node object
        """
        try:
            ## If no key is provided or node is empty
            if (property is None): return None
            
            ## Create new json ld simple node
            newNode = dict()

            ## If the key is not none create a new node
            if not (key is None):
                newNode["@id"] = self.aspectPrefix+":"+key
            

            ## If description exists add definition to the node

            if not ("description" in property):
                return newNode
            
            if not ("@context" in newNode):
                newNode["@context"] = dict()

            newNode["@context"]["@definition"] = property["description"]

            return newNode
        except:
            traceback.print_exc()
            raise Exception("It was not possible to create the simple node")

    def get_schema_ref(self, ref, actualref):
        """
        Creates a simple node with key and object from a schema property
        Receives:
            key: :str: attribute key
            node: :dict: contains the node object with or without description and type
        Returns:
            response: :dict: json ld simple node with the information of the node object
        """
        try:
            if(not isinstance(ref, str)): return None
            
            # If the actual reference is already found means we are going in a loop
            if not(ref in actualref):     
                path = ref.removeprefix(self.path_sep) 
                return op.get_attribute(self.baseSchema, attr_path=path, path_sep=self.refPathSep, default_value=None)
            
            if(self.depth >= self.recursionDepth):
                if(self.verbose and self.logger is not None):
                    self.logger.warning(f"[WARNING] Infinite recursion detected in the following path: ref[{ref}] and acumulated ref[{actualref}]!")
                self.depth=0
                return None
            
            self.depth+=1
            
            path = ref.removeprefix(self.path_sep) 

            return op.get_attribute(self.baseSchema, attr_path=path, path_sep=self.refPathSep, default_value=None)
        except:
            traceback.print_exc()
            raise Exception("It was not possible to get schema reference")