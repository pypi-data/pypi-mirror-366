"""
This module contains the functions to generate the proto file for the CRUD operations.

Author: Achraf MATAICH <achraf.mataich@outlook.com>
"""

from typing import List, Tuple

def generate_crud_proto(service: str, model: str, fields: List[Tuple[str, str]], package_name: str) -> str:
    def field_lines(fields_subset, indent=2):
        return [
            " " * indent + f"{typ} {name} = {i+1};"
            for i, (name, typ) in enumerate(fields_subset)
        ]

    # Fields are already parsed as tuples from the calling function
    if not fields:
        raise ValueError("At least one field is required for CRUD operations")
    
    def message_block(name, field_subset):
        if not field_subset:
            return f"message {name} {{}}\n"
        return f"message {name} {{\n" + "\n".join(field_lines(field_subset)) + "\n}\n"

    messages = []

    # For CRUD operations, we assume the first field is the ID field
    id_field = fields[0] if fields else None
    non_id_fields = fields[1:] if len(fields) > 1 else []

    if not id_field:
        raise ValueError("CRUD operations require at least one field (typically an ID field)")

    # Create - all fields except ID (assuming ID is auto-generated)
    if non_id_fields:
        messages.append(message_block(f"Create{model}Request", non_id_fields))
    else:
        # If only ID field exists, create an empty request
        messages.append(f"message Create{model}Request {{}}\n")
    messages.append(message_block(f"Create{model}Response", [("success", "bool"), ("message", "string")]))

    # Read - only ID field for lookup
    messages.append(message_block(f"Read{model}Request", [id_field]))
    messages.append(message_block(f"Read{model}Response", fields))

    # Update - all fields (including ID to identify which record to update)
    messages.append(message_block(f"Update{model}Request", fields))
    messages.append(message_block(f"Update{model}Response", [("success", "bool")]))

    # Delete - only ID field for lookup
    messages.append(message_block(f"Delete{model}Request", [id_field]))
    messages.append(message_block(f"Delete{model}Response", [("success", "bool")]))

    # List - empty request, returns repeated response
    messages.append(f"message List{model}Request {{}}\n")
    messages.append(f"message List{model}Response {{\n  repeated {model} {model.lower()}s = 1;\n}}\n")
    
    # Add the model message itself
    messages.append(message_block(model, fields))

    # Service block
    service_block = f"""service {service} {{
  rpc Create(Create{model}Request) returns (Create{model}Response);
  rpc Read(Read{model}Request) returns (Read{model}Response);
  rpc Update(Update{model}Request) returns (Update{model}Response);
  rpc Delete(Delete{model}Request) returns (Delete{model}Response);
  rpc List(List{model}Request) returns (List{model}Response);
}}"""

    return 'syntax = "proto3";\n\npackage ' + package_name + ";\n\n" + "\n".join(messages) + "\n" + service_block