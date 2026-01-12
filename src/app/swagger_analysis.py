import json
import re
from typing import Any, Dict, List, Optional

import yaml


class IDORAnalyzer:
    def __init__(self):
        # Common identifier names for heuristic rules
        self.common_identifier_names = {
            "id",
            "uuid",
            "guid",
            "name",
            "filename",
            "group",
            "key",
            "phone",
            "email",
            "user",
            "account",
            "bucket",
            "vault",
            "item",
            "resource",
            "object",
            "token",
        }
        # Precompile regex patterns for efficiency
        self.id_pattern = re.compile(r"id$|_id$|Id$", re.IGNORECASE)
        self.uuid_pattern = re.compile(r"uuid$|guid$", re.IGNORECASE)
        self.desc_pattern = re.compile(r"\b(id|uuid|guid|identifier)\b", re.IGNORECASE)

    def load_openapi_spec(self, file_path: str) -> Dict[str, Any]:
        """Load OpenAPI specification from file (JSON or YAML)."""
        with open(file_path, "r") as file:
            if file_path.endswith(".json"):
                return json.load(file)
            elif file_path.endswith(".yml") or file_path.endswith(".yaml"):
                return yaml.safe_load(file)
            else:
                raise ValueError("Unsupported file format. Use JSON or YAML.")

    def analyze(self, openapi_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Main method to analyze the OpenAPI spec for IDOR/BOLA vulnerabilities."""
        # Stage 1: Annotate the specification with IDOR/BOLA properties
        annotated_spec = self.annotate_properties(openapi_spec)
        # Stage 2: Analyze for attacks
        vulnerabilities = self.analyze_attacks(annotated_spec)
        return vulnerabilities

    def annotate_properties(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Annotate the OpenAPI spec with IDOR/BOLA properties."""
        annotated_spec = spec.copy()
        if "paths" not in annotated_spec:
            return annotated_spec

        # Check global security schemes
        global_security = spec.get("security", [])
        paths = annotated_spec["paths"]
        for path, path_item in paths.items():
            # Annotate endpoint level properties
            self.annotate_endpoint_level(path_item, path)
            # Annotate parameters at the path level
            path_params = path_item.get("parameters", [])
            for param in path_params:
                self.annotate_parameter_level(param, path)
            # Annotate each operation (method) in the path
            for method, operation in path_item.items():
                if method.upper() in [
                    "GET",
                    "POST",
                    "PUT",
                    "DELETE",
                    "PATCH",
                    "HEAD",
                    "OPTIONS",
                ]:
                    self.annotate_method_level(
                        operation, method, path_item, global_security
                    )
                    op_params = operation.get("parameters", [])
                    for param in op_params:
                        self.annotate_parameter_level(param, path)
        return annotated_spec

    def annotate_endpoint_level(self, path_item: Dict[str, Any], path: str) -> None:
        """Annotate endpoint level properties."""
        methods = [
            m.upper()
            for m in path_item.keys()
            if m.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        ]
        defined_verbs = (
            "single" if len(methods) == 1 else "multiple" if len(methods) > 1 else "all"
        )
        path_item["x_endor_defined_http_verbs"] = defined_verbs

    def annotate_method_level(
        self,
        operation: Dict[str, Any],
        method: str,
        path_item: Dict[str, Any],
        global_security: List[Any],
    ) -> None:
        """Annotate method level properties."""
        # Check if authorization is required
        security = operation.get("security", global_security)
        authorization_required = len(security) > 0 and security != [{}]
        operation["x_endor_authorization_required"] = authorization_required

        # Check parameters
        path_params = path_item.get("parameters", [])
        op_params = operation.get("parameters", [])
        all_params = path_params + op_params
        identifier_params = [p for p in all_params if self.is_identifier_parameter(p)]
        num_identifiers = len(identifier_params)
        operation["x_endor_identifiers_used"] = (
            "zero"
            if num_identifiers == 0
            else "single"
            if num_identifiers == 1
            else "multiple"
        )

        # Check if operation has parameters besides path level
        if len(op_params) > 0:
            operation["x_endor_operation_parameters"] = "non-empty"
        elif len(path_params) > 0:
            operation["x_endor_operation_parameters"] = "endpoint-level-only"
        else:
            operation["x_endor_operation_parameters"] = "empty"

    def annotate_parameter_level(self, param: Dict[str, Any], path: str) -> None:
        """Annotate parameter level properties."""
        param_name = param.get("name", "")
        param_in = param.get("in", "")
        param_schema = param.get("schema", {})
        param_type = param_schema.get("type", "string")
        param_desc = param.get("description", "")

        # Determine if parameter is an identifier
        is_identifier = self.is_identifier_parameter(param)
        param["x_endor_is_identifier"] = is_identifier

        # Annotate location
        location_map = {
            "path": "resource path in URI",
            "query": "URL parameter",
            "body": "Body",
            "header": "Request Header",
        }
        param["x_endor_location"] = location_map.get(param_in, "other")

        # Annotate ID type
        id_type = "other"
        if param_type == "integer":
            id_type = "numerical sequential identifier"
        elif param_type == "string":
            if (
                self.uuid_pattern.search(param_name)
                or "uuid" in param_desc.lower()
                or "guid" in param_desc.lower()
            ):
                id_type = "UUID/GUID"
            elif any(
                word in param_name.lower()
                for word in ["email", "phone", "account", "user"]
            ):
                id_type = "account/personal information"
            else:
                id_type = "string"
        elif param_type == "array":
            id_type = "array"
        param["x_endor_id_type"] = id_type

    def is_identifier_parameter(self, param: Dict[str, Any]) -> bool:
        """Determine if a parameter is a resource identifier using heuristic rules."""
        param_name = param.get("name", "").lower()
        param_in = param.get("in", "")
        param_desc = param.get("description", "").lower()
        param_schema = param.get("schema", {})
        param_type = param_schema.get("type", "string")

        # Rule based on parameter name
        if self.id_pattern.search(param_name) or self.uuid_pattern.search(param_name):
            return True
        if param_name in self.common_identifier_names:
            return True

        # Rule based on parameter location and path (simplified)
        if param_in == "path":
            # Check if parameter name is part of the path pattern (would need path context, so skipped here for simplicity)
            return True

        # Rule based on description
        if self.desc_pattern.search(param_desc):
            return True

        # Rule based on type
        if param_type in ["integer", "string"]:
            # More checks could be added
            return True

        return False

    def analyze_attacks(self, annotated_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze annotated spec for potential IDOR/BOLA vulnerabilities."""
        vulnerabilities = []
        paths = annotated_spec.get("paths", {})
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.upper() in [
                    "GET",
                    "POST",
                    "PUT",
                    "DELETE",
                    "PATCH",
                    "HEAD",
                    "OPTIONS",
                ]:
                    # Check each attack pattern
                    attacks = self.check_attack_patterns(operation, path_item)
                    if attacks:
                        vulnerabilities.append(
                            {"path": path, "method": method, "attacks": attacks}
                        )
        return {"vulnerabilities": vulnerabilities}

    def check_attack_patterns(
        self, operation: Dict[str, Any], path_item: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check all attack patterns for a given operation."""
        attacks = []
        # Enumeration without a priori knowledge
        if self.check_enumeration_without_priori(operation):
            attacks.append(
                {
                    "technique": "Enumeration without a priori knowledge",
                    "description": "Identifier is tampered for enumeration based on automatically determined pattern.",
                }
            )
        # Enumeration with a priori knowledge
        if self.check_enumeration_with_priori(operation):
            attacks.append(
                {
                    "technique": "Enumeration with a priori knowledge",
                    "description": "Targeted identifier is hard to enumerate but can be checked with known identifiers.",
                }
            )
        # Add/Change file extension
        if self.check_add_change_extension(operation):
            attacks.append(
                {
                    "technique": "Add/Change file extension",
                    "description": "Enumerated identifier is appended with an extension or changed to another extension.",
                }
            )
        # Wildcard replacement/appending
        if self.check_wildcard_replacement(operation):
            attacks.append(
                {
                    "technique": "Wildcard replacement/appending",
                    "description": "Enumerated identifier is decorated with a wildcard or special character.",
                }
            )
        # ID encoding/decoding
        if self.check_id_encoding(operation):
            attacks.append(
                {
                    "technique": "ID encoding/decoding",
                    "description": "Encoded or decoded identifier is substituted for enumeration.",
                }
            )
        # JSON List appending
        if self.check_json_list_appending(operation):
            attacks.append(
                {
                    "technique": "JSON List appending",
                    "description": "Identifiers of non-owned objects are appended to a list to exploit improper access control.",
                }
            )
        # Authorization token manipulation
        if self.check_authorization_token_manipulation(operation):
            attacks.append(
                {
                    "technique": "Authorization token manipulation",
                    "description": "Request is repeated with authorization cookies of another user.",
                }
            )
        # Parameter pollution
        if self.check_parameter_pollution(operation, path_item):
            attacks.append(
                {
                    "technique": "Parameter pollution",
                    "description": "Tampering with parameter values in different locations to bypass authorization.",
                }
            )
        # Endpoint verb tampering
        if self.check_verb_tampering(operation, path_item):
            attacks.append(
                {
                    "technique": "Endpoint verb tampering",
                    "description": "Changing HTTP method or adding parameters from other methods to bypass checks.",
                }
            )
        return attacks

    def check_enumeration_without_priori(self, operation: Dict[str, Any]) -> bool:
        """Check condition for enumeration without a priori knowledge."""
        auth = operation.get("x_endor_authorization_required", False)
        params_status = (
            operation.get("x_endor_operation_parameters", "empty") != "empty"
        )
        identifiers = operation.get("x_endor_identifiers_used", "zero") != "zero"
        # Check if any parameter is numerical
        params = operation.get("parameters", [])
        numerical_exists = any(
            p.get("x_endor_id_type") == "numerical sequential identifier"
            for p in params
        )
        return auth and params_status and identifiers and numerical_exists

    def check_enumeration_with_priori(self, operation: Dict[str, Any]) -> bool:
        """Check condition for enumeration with a priori knowledge."""
        auth = operation.get("x_endor_authorization_required", False)
        params_status = (
            operation.get("x_endor_operation_parameters", "empty") != "empty"
        )
        identifiers = operation.get("x_endor_identifiers_used", "zero") != "zero"
        params = operation.get("parameters", [])
        uuid_exists = any(p.get("x_endor_id_type") == "UUID/GUID" for p in params)
        string_exists = any(p.get("x_endor_id_type") == "string" for p in params)
        complex_exists = any(
            p.get("x_endor_id_type") in ["account/personal information", "other"]
            for p in params
        )
        return (
            auth
            and params_status
            and identifiers
            and (uuid_exists or string_exists or complex_exists)
        )

    def check_add_change_extension(self, operation: Dict[str, Any]) -> bool:
        """Check condition for add/change file extension attack."""
        auth = operation.get("x_endor_authorization_required", False)
        params_status = (
            operation.get("x_endor_operation_parameters", "empty") != "empty"
        )
        identifiers = operation.get("x_endor_identifiers_used", "zero") != "zero"
        return auth and params_status and identifiers

    def check_wildcard_replacement(self, operation: Dict[str, Any]) -> bool:
        """Check condition for wildcard replacement/appending."""
        auth = operation.get("x_endor_authorization_required", False)
        params_status = (
            operation.get("x_endor_operation_parameters", "empty") != "empty"
        )
        identifiers = operation.get("x_endor_identifiers_used", "zero") != "zero"
        params = operation.get("parameters", [])
        string_exists = any(p.get("x_endor_id_type") == "string" for p in params)
        return auth and params_status and identifiers and string_exists

    def check_id_encoding(self, operation: Dict[str, Any]) -> bool:
        """Check condition for ID encoding/decoding."""
        auth = operation.get("x_endor_authorization_required", False)
        params_status = (
            operation.get("x_endor_operation_parameters", "empty") != "empty"
        )
        identifiers = operation.get("x_endor_identifiers_used", "zero") != "zero"
        return auth and params_status and identifiers

    def check_json_list_appending(self, operation: Dict[str, Any]) -> bool:
        """Check condition for JSON list appending."""
        auth = operation.get("x_endor_authorization_required", False)
        params_status = (
            operation.get("x_endor_operation_parameters", "empty") != "empty"
        )
        identifiers = operation.get("x_endor_identifiers_used", "zero") != "zero"
        params = operation.get("parameters", [])
        array_exists = any(p.get("x_endor_id_type") == "array" for p in params)
        return auth and params_status and identifiers and array_exists

    def check_authorization_token_manipulation(self, operation: Dict[str, Any]) -> bool:
        """Check condition for authorization token manipulation."""
        auth = operation.get("x_endor_authorization_required", False)
        return auth

    def check_parameter_pollution(
        self, operation: Dict[str, Any], path_item: Dict[str, Any]
    ) -> bool:
        """Check condition for parameter pollution."""
        auth = operation.get("x_endor_authorization_required", False)
        identifiers = operation.get("x_endor_identifiers_used", "zero") == "multiple"
        # Check for parameters with same name in different locations
        params = operation.get("parameters", [])
        param_names = [p.get("name") for p in params]
        if len(param_names) != len(set(param_names)):
            return auth and identifiers
        return False

    def check_verb_tampering(
        self, operation: Dict[str, Any], path_item: Dict[str, Any]
    ) -> bool:
        """Check condition for endpoint verb tampering."""
        auth = operation.get("x_endor_authorization_required", False)
        identifiers = operation.get("x_endor_identifiers_used", "zero") != "zero"
        defined_verbs = path_item.get("x_endor_defined_http_verbs", "single")
        if defined_verbs != "all":
            # Check if parameters are not the same across methods
            methods = [
                m
                for m in path_item.keys()
                if m.upper()
                in ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
            ]
            if len(methods) > 1:
                param_sets = []
                for m in methods:
                    op = path_item[m]
                    params = op.get("parameters", [])
                    param_names = [p.get("name") for p in params]
                    param_sets.append(set(param_names))
                if len(set(tuple(s) for s in param_sets)) > 1:
                    return auth and identifiers
        return False

    def analyze_file_bytes(self, file_bytes: bytes) -> Dict[str, Any]:
        """Analyze a specification provided as raw bytes (JSON or YAML)."""
        try:
            # Attempt to decode as JSON
            spec = json.loads(file_bytes.decode())
        except Exception:
            try:
                # If JSON fails, try YAML
                spec = yaml.safe_load(file_bytes.decode())
            except Exception:
                raise ValueError("Unable to parse input bytes as JSON or YAML.")
        # Delegate to existing analyze method
        return self.analyze(spec)
