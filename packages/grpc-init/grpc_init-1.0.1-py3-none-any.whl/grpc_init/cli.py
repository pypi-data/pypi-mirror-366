"""
This module contains the CLI for the grpc-init package.

Author: Achraf MATAICH <achraf.mataich@outlook.com>
"""

import typer
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple
from .utils import generate_crud_proto

app = typer.Typer()

# Valid proto3 field types
VALID_PROTO_TYPES = {
    'double', 'float', 'int32', 'int64', 'uint32', 'uint64', 'sint32', 'sint64',
    'fixed32', 'fixed64', 'sfixed32', 'sfixed64', 'bool', 'string', 'bytes'
}

def validate_service_name(service: str) -> str:
    """Validate and sanitize service name."""
    if not service:
        raise typer.BadParameter("Service name cannot be empty")
    
    # Remove invalid characters and ensure it starts with uppercase
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '', service)
    if not sanitized:
        raise typer.BadParameter("Service name must contain at least one alphanumeric character")
    
    return sanitized[0].upper() + sanitized[1:] if len(sanitized) > 1 else sanitized.upper()

def validate_identifier(name: str, field_name: str) -> str:
    """Validate proto identifier (message names, field names, etc.)."""
    if not name:
        raise typer.BadParameter(f"{field_name} cannot be empty")
    
    # Proto identifiers must start with letter and contain only letters, numbers, underscore
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '', name)
    if not sanitized or not sanitized[0].isalpha():
        raise typer.BadParameter(f"{field_name} must start with a letter and contain only letters, numbers, and underscores")
    
    return sanitized

def validate_package_name(package: str) -> str:
    """Validate proto package name."""
    if not package.strip():
        raise typer.BadParameter("Package name cannot be empty")
    
    # Package names can contain letters, numbers, dots, and underscores
    # Each segment (separated by dots) must start with a letter
    segments = package.split('.')
    validated_segments = []
    
    for segment in segments:
        if not segment:
            raise typer.BadParameter("Package name cannot contain empty segments (consecutive dots)")
        
        # Remove invalid characters
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '', segment)
        if not sanitized:
            raise typer.BadParameter(f"Package segment '{segment}' must contain at least one alphanumeric character")
        if not sanitized[0].isalpha():
            raise typer.BadParameter(f"Package segment '{segment}' must start with a letter")
        
        validated_segments.append(sanitized.lower())  # Package names are typically lowercase
    
    return '.'.join(validated_segments)

def parse_fields(fields_str: str) -> List[Tuple[str, str]]:
    """Parse and validate field definitions."""
    if not fields_str.strip():
        raise typer.BadParameter("Fields cannot be empty")
    
    fields = []
    field_list = [f.strip() for f in fields_str.split(',') if f.strip()]
    
    if not field_list:
        raise typer.BadParameter("At least one field must be specified")
    
    for i, field in enumerate(field_list):
        if ':' not in field:
            raise typer.BadParameter(f"Field '{field}' must be in format 'name:type'")
        
        parts = field.split(':')
        if len(parts) != 2:
            raise typer.BadParameter(f"Field '{field}' must have exactly one colon separating name and type")
        
        name, field_type = parts[0].strip(), parts[1].strip()
        
        if not name:
            raise typer.BadParameter(f"Field name cannot be empty in field '{field}'")
        if not field_type:
            raise typer.BadParameter(f"Field type cannot be empty in field '{field}'")
        
        # Validate field name
        name = validate_identifier(name, f"Field name '{name}'")
        
        # Validate field type
        if field_type not in VALID_PROTO_TYPES:
            raise typer.BadParameter(f"Invalid proto3 field type '{field_type}'. Valid types: {', '.join(sorted(VALID_PROTO_TYPES))}")
        
        fields.append((name, field_type))
    
    return fields

def parse_simple_methods(methods_str: str) -> List[str]:
    """Parse simple comma-separated method names (legacy format)."""
    if not methods_str.strip():
        raise typer.BadParameter("Methods cannot be empty")
    
    methods = []
    method_list = [m.strip() for m in methods_str.split(',') if m.strip()]
    
    if not method_list:
        raise typer.BadParameter("At least one method must be specified")
    
    for method in method_list:
        validated_method = validate_identifier(method, f"Method name '{method}'")
        methods.append(validated_method)
    
    return methods

def parse_enhanced_methods(methods_str: str) -> List[dict]:
    """
    Parse enhanced method definitions with streaming and message specs.
    
    Format: methodName|inputType|inputSpec|outputType|outputSpec
    Where:
    - inputType/outputType: 'unary' or 'stream'
    - inputSpec/outputSpec: either existing message name or field definitions like 'name:string,age:int32'
    
    Example: transformToZombie|unary|User|stream|User;sayHello|unary|name:string|unary|message:string
    """
    if not methods_str.strip():
        raise typer.BadParameter("Methods cannot be empty")
    
    methods = []
    method_list = [m.strip() for m in methods_str.split(';') if m.strip()]
    
    if not method_list:
        raise typer.BadParameter("At least one method must be specified")
    
    for method_def in method_list:
        parts = [p.strip() for p in method_def.split('|')]
        
        if len(parts) != 5:
            raise typer.BadParameter(
                f"Method definition '{method_def}' must have format: "
                "methodName|inputType|inputSpec|outputType|outputSpec"
            )
        
        method_name, input_type, input_spec, output_type, output_spec = parts
        
        # Validate method name
        method_name = validate_identifier(method_name, f"Method name '{method_name}'")
        
        # Validate stream types
        if input_type not in ['unary', 'stream']:
            raise typer.BadParameter(f"Input type must be 'unary' or 'stream', got '{input_type}'")
        if output_type not in ['unary', 'stream']:
            raise typer.BadParameter(f"Output type must be 'unary' or 'stream', got '{output_type}'")
        
        # Parse message specifications
        def parse_message_spec(spec: str, spec_type: str):
            # Check if it's an existing message reference (single word, capitalized)
            if ':' not in spec and spec[0].isupper() and spec.replace('_', '').isalnum():
                return {'type': 'reference', 'name': spec}
            else:
                # Parse as field definitions
                try:
                    fields = parse_fields(spec)
                    return {'type': 'definition', 'fields': fields}
                except Exception as e:
                    raise typer.BadParameter(f"Invalid {spec_type} specification '{spec}': {e}")
        
        input_msg = parse_message_spec(input_spec, "input message")
        output_msg = parse_message_spec(output_spec, "output message")
        
        methods.append({
            'name': method_name,
            'input_type': input_type,
            'input_message': input_msg,
            'output_type': output_type,
            'output_message': output_msg
        })
    
    return methods

def is_enhanced_method_format(methods_str: str) -> bool:
    """Check if the methods string uses the enhanced format (contains | or ;)."""
    return '|' in methods_str or ';' in methods_str

def parse_model_definition(model_str: str) -> Tuple[str, List[Tuple[str, str]]]:
    """
    Parse model definition that can include field definitions.
    
    Format: ModelName:field1:type1,field2:type2,field3:type3
    or just: ModelName (fields will be taken from --fields parameter)
    
    Returns: (model_name, fields_list)
    """
    if not model_str.strip():
        raise typer.BadParameter("Model cannot be empty")
    
    if ':' not in model_str:
        # Simple model name without fields
        model_name = validate_service_name(model_str.strip())
        return model_name, []
    
    # Parse model with field definitions
    parts = model_str.split(':', 1)  # Split only on first colon
    if len(parts) != 2:
        raise typer.BadParameter("Model definition must be in format 'ModelName:field1:type1,field2:type2'")
    
    model_name = parts[0].strip()
    fields_str = parts[1].strip()
    
    if not model_name:
        raise typer.BadParameter("Model name cannot be empty")
    if not fields_str:
        raise typer.BadParameter("Fields definition cannot be empty when using model field syntax")
    
    model_name = validate_service_name(model_name)
    fields = parse_fields(fields_str)
    
    return model_name, fields

def generate_simple_proto(service: str, methods: List[str], request: str, response: str, fields: List[Tuple[str, str]], package_name: str) -> str:
    """Generate proto for simple method definitions (legacy format)."""
    field_lines = []
    for i, (name, typ) in enumerate(fields, 1):
        field_lines.append(f"  {typ} {name} = {i};")

    methods_lines = [
        f"  rpc {method.capitalize()}({request}) returns ({response});"
        for method in methods
    ]

    proto = f"""syntax = "proto3";

package {package_name};

message {request} {{
{chr(10).join(field_lines)}
}}

message {response} {{
  bool success = 1;
  string message = 2;
}}

service {service} {{
{chr(10).join(methods_lines)}
}}
"""
    return proto

def generate_enhanced_proto(service: str, enhanced_methods: List[dict], package_name: str, existing_messages: dict = None) -> str:
    """Generate proto for enhanced method definitions with streaming support."""
    if existing_messages is None:
        existing_messages = {}
    
    messages = []
    service_methods = []
    message_counter = {}
    
    def get_message_name(base_name: str) -> str:
        """Generate unique message name."""
        if base_name not in message_counter:
            message_counter[base_name] = 0
            return base_name
        else:
            message_counter[base_name] += 1
            return f"{base_name}{message_counter[base_name]}"
    
    def generate_message_from_fields(name: str, fields: List[Tuple[str, str]]) -> str:
        """Generate message definition from fields."""
        if not fields:
            return f"message {name} {{}}\n"
        
        field_lines = []
        for i, (field_name, field_type) in enumerate(fields, 1):
            field_lines.append(f"  {field_type} {field_name} = {i};")
        
        return f"message {name} {{\n" + "\n".join(field_lines) + "\n}\n"
    
    def process_message_spec(method_name: str, msg_spec: dict, msg_type: str) -> str:
        """Process message specification and return message name."""
        if msg_spec['type'] == 'reference':
            # Reference to existing message
            msg_name = msg_spec['name']
            if msg_name not in existing_messages:
                # Add to existing_messages to track it
                existing_messages[msg_name] = True
            return msg_name
        else:
            # Generate new message from field definitions
            base_name = f"{method_name.capitalize()}{msg_type.capitalize()}"
            msg_name = get_message_name(base_name)
            message_def = generate_message_from_fields(msg_name, msg_spec['fields'])
            messages.append(message_def)
            return msg_name
    
    # Process each enhanced method
    for method in enhanced_methods:
        method_name = method['name']
        
        # Process input message
        input_msg_name = process_message_spec(method_name, method['input_message'], 'request')
        
        # Process output message  
        output_msg_name = process_message_spec(method_name, method['output_message'], 'response')
        
        # Generate service method signature
        input_stream = "stream " if method['input_type'] == 'stream' else ""
        output_stream = "stream " if method['output_type'] == 'stream' else ""
        
        service_method = f"  rpc {method_name.capitalize()}({input_stream}{input_msg_name}) returns ({output_stream}{output_msg_name});"
        service_methods.append(service_method)
    
    # Build complete proto
    proto_parts = [
        'syntax = "proto3";',
        '',
        f'package {package_name};',
        ''
    ]
    
    # Add generated messages
    for message in messages:
        proto_parts.append(message)
    
    # Add service definition
    proto_parts.append(f'service {service} {{')
    proto_parts.extend(service_methods)
    proto_parts.append('}')
    
    return '\n'.join(proto_parts)

def combine_crud_and_enhanced_proto(service: str, model: str, crud_fields: List[Tuple[str, str]], enhanced_methods: List[dict], package_name: str) -> str:
    """Combine CRUD proto with enhanced methods."""
    from .utils.operations import generate_crud_proto
    
    # Generate base CRUD proto
    crud_proto = generate_crud_proto(service, model, crud_fields, package_name)
    
    # Extract existing messages from CRUD proto for reference
    existing_messages = {
        model: True,
        f'Create{model}Request': True,
        f'Create{model}Response': True,
        f'Read{model}Request': True,
        f'Read{model}Response': True,
        f'Update{model}Request': True,
        f'Update{model}Response': True,
        f'Delete{model}Request': True,
        f'Delete{model}Response': True,
        f'List{model}Request': True,
        f'List{model}Response': True,
    }
    
    # Generate enhanced methods proto
    enhanced_proto = generate_enhanced_proto(service, enhanced_methods, package_name, existing_messages)
    
    # Combine them by extracting parts
    crud_lines = crud_proto.split('\n')
    enhanced_lines = enhanced_proto.split('\n')
    
    # Find the service definition in CRUD proto
    crud_service_start = -1
    crud_service_end = -1
    for i, line in enumerate(crud_lines):
        if line.startswith(f'service {service}'):
            crud_service_start = i
        elif crud_service_start != -1 and line == '}':
            crud_service_end = i
            break
    
    # Extract CRUD service methods (without the service wrapper)
    crud_methods = []
    if crud_service_start != -1 and crud_service_end != -1:
        crud_methods = crud_lines[crud_service_start + 1:crud_service_end]
    
    # Find enhanced service methods
    enhanced_service_start = -1
    enhanced_service_end = -1
    for i, line in enumerate(enhanced_lines):
        if line.startswith(f'service {service}'):
            enhanced_service_start = i
        elif enhanced_service_start != -1 and line == '}':
            enhanced_service_end = i
            break
    
    enhanced_methods_lines = []
    if enhanced_service_start != -1 and enhanced_service_end != -1:
        enhanced_methods_lines = enhanced_lines[enhanced_service_start + 1:enhanced_service_end]
    
    # Build combined proto
    combined_parts = []
    
    # Add header from CRUD
    header_end = crud_service_start if crud_service_start != -1 else len(crud_lines)
    combined_parts.extend(crud_lines[:header_end])
    
    # Add enhanced messages (everything before service in enhanced proto)
    enhanced_header_end = enhanced_service_start if enhanced_service_start != -1 else len(enhanced_lines)
    enhanced_messages = enhanced_lines[4:enhanced_header_end]  # Skip header (syntax, package)
    combined_parts.extend(enhanced_messages)
    
    # Add combined service
    combined_parts.append(f'service {service} {{')
    combined_parts.extend(crud_methods)
    combined_parts.extend(enhanced_methods_lines)
    combined_parts.append('}')
    
    return '\n'.join(combined_parts)

def check_grpc_tools():
    """Check if grpc_tools is available for compilation."""
    try:
        import grpc_tools.protoc
        return True
    except ImportError:
        return False

@app.command()
def init(
    service: str = typer.Option(..., help="Service name, e.g. UserService"),
    methods: str = typer.Option(None, help="Methods: simple 'create,get,delete' or enhanced 'methodName|unary|User|stream|User;other|unary|name:string|unary|message:string'"),
    model: str = typer.Option(None, help="Model for CRUD: 'User' or with fields 'User:id:int32,name:string,email:string'"),
    crud: bool = typer.Option(False, help="Generate CRUD operations (create, read, update, delete, list)"),
    package: str = typer.Option(None, help="Package name for proto file, e.g. 'com.company.service' (defaults to lowercased service name)"),
    request: str = typer.Option("RequestMessage", help="Request message name (only for simple methods)"),
    response: str = typer.Option("ResponseMessage", help="Response message name (only for simple methods)"),
    fields: str = typer.Option(None, help="Fields for simple methods or fallback: id:int32,name:string"),
    out: Path = typer.Option("protos", help="Output folder for the .proto file"), 
    compile: bool = typer.Option(False, help="Compile Python stubs using grpcio-tools")
):
    """Generate gRPC service definition (.proto file) and optionally compile Python stubs."""
    
    try:
        # Validate inputs based on mode
        has_methods = methods is not None and methods.strip()
        is_enhanced_methods = has_methods and is_enhanced_method_format(methods)
        has_fields = fields is not None and fields.strip()
        
        if not crud and not has_methods:
            raise typer.BadParameter("Either --crud or --methods must be specified")
        
        if crud and not model:
            raise typer.BadParameter("Model is required when using --crud option")
        
        # Validate and sanitize inputs
        service = validate_service_name(service)
        
        # Determine package name
        if package:
            package_name = validate_package_name(package)
        else:
            package_name = service.lower()
        
        # Parse model and extract fields if CRUD is used
        model_name = None
        model_fields = []
        if crud:
            model_name, model_fields = parse_model_definition(model)
            
            # If model doesn't have fields defined, use --fields parameter
            if not model_fields:
                if not has_fields:
                    raise typer.BadParameter("Fields must be specified either in --model or --fields when using --crud")
                model_fields = parse_fields(fields)
        
        # Parse fields for non-CRUD operations
        field_list = []
        if not crud and has_fields:
            field_list = parse_fields(fields)
        
        # Create output directory
        try:
            out.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            typer.echo(f"❌ Failed to create output directory '{out}': {e}", err=True)
            raise typer.Exit(1)

        # Determine generation mode and generate proto content
        proto_path = out / f"{service.lower()}.proto"
        
        if crud and has_methods and is_enhanced_methods:
            # CRUD + Enhanced methods
            enhanced_methods = parse_enhanced_methods(methods)
            
            try:
                content = combine_crud_and_enhanced_proto(service, model_name, model_fields, enhanced_methods, package_name)
                proto_path.write_text(content, encoding='utf-8')
                typer.echo(f"✅ Generated CRUD + enhanced methods proto: {proto_path}")
            except Exception as e:
                typer.echo(f"❌ Failed to generate CRUD + enhanced methods proto: {e}", err=True)
                raise typer.Exit(1)
                
        elif crud and has_methods and not is_enhanced_methods:
            # CRUD + Simple methods (not supported - would be messy)
            raise typer.BadParameter("CRUD can only be combined with enhanced methods format. Use enhanced format: 'method|unary|spec|unary|spec'")
                
        elif crud and not has_methods:
            # CRUD only
            try:
                content = generate_crud_proto(service, model_name, model_fields, package_name)
                proto_path.write_text(content, encoding='utf-8')
                typer.echo(f"✅ Generated CRUD proto: {proto_path}")
            except Exception as e:
                typer.echo(f"❌ Failed to generate CRUD proto: {e}", err=True)
                raise typer.Exit(1)
                
        elif has_methods and is_enhanced_methods:
            # Enhanced methods only
            enhanced_methods = parse_enhanced_methods(methods)
            
            try:
                content = generate_enhanced_proto(service, enhanced_methods, package_name)
                proto_path.write_text(content, encoding='utf-8')
                typer.echo(f"✅ Generated enhanced methods proto: {proto_path}")
            except Exception as e:
                typer.echo(f"❌ Failed to generate enhanced methods proto: {e}", err=True)
                raise typer.Exit(1)
                
        elif has_methods and not is_enhanced_methods:
            # Simple methods (legacy format)
            if not field_list:
                raise typer.BadParameter("Fields are required for simple methods (use --fields parameter)")
            
            request = validate_identifier(request, "Request message name")
            response = validate_identifier(response, "Response message name")
            method_list = parse_simple_methods(methods)
            
            try:
                content = generate_simple_proto(service, method_list, request, response, field_list, package_name)
                proto_path.write_text(content, encoding='utf-8')
                typer.echo(f"✅ Generated simple methods proto: {proto_path}")
            except Exception as e:
                typer.echo(f"❌ Failed to generate simple methods proto: {e}", err=True)
                raise typer.Exit(1)
        else:
            # This shouldn't happen due to earlier validation
            raise typer.BadParameter("Invalid combination of parameters")

        # Compile Python stubs if requested
        if compile:
            if not check_grpc_tools():
                typer.echo("❌ grpcio-tools not found. Install it with: pip install grpcio-tools", err=True)
                raise typer.Exit(1)
            
            try:
                result = subprocess.run([
                    sys.executable, "-m", "grpc_tools.protoc",
                    f"--proto_path={out}",
                    f"--python_out={out}",
                    f"--grpc_python_out={out}",
                    str(proto_path)
                ], check=True, capture_output=True, text=True)
                typer.echo("✅ Compiled Python stubs successfully")
            except subprocess.CalledProcessError as e:
                typer.echo(f"❌ Compilation failed: {e.stderr}", err=True)
                raise typer.Exit(1)
            except FileNotFoundError:
                typer.echo(f"❌ Python executable not found: {sys.executable}", err=True)
                raise typer.Exit(1)
    except typer.BadParameter as e:
        typer.echo(f"❌ {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Unexpected error: {e}", err=True)
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
