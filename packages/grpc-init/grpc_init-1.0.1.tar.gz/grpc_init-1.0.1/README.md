# gRPC Proto Generator CLI 🧬

A powerful Typer-based CLI tool to **generate `.proto` files** for gRPC services from simple command-line arguments. Supports **CRUD**, **simple**, and **enhanced streaming** methods with optional Python stub compilation.

> ⚡ Ideal for rapidly bootstrapping gRPC-based microservices and APIs.

---

## Features

- Validate and sanitize service, method, model, and field definitions.
- Supports **CRUD** scaffolding for your data models.
- Supports **simple RPCs** (`create,get,update`) with custom request/response messages.
- Supports **enhanced streaming RPCs** (unary/stream with custom messages or inline fields).
- Combines CRUD + enhanced methods into one `.proto` file.
- Automatically compiles `.proto` to Python stubs with `grpcio-tools`.

---

## Installation

```bash
pip install grpc-init
```

## Usage

```bash
grpc-init [OPTIONS]
```

## Required options

- `--service <ServiceName>` : Name of your gRPC service
- One of
  - `--crud` + `--model`
  - `--methods`
  - Both options (enhanced format only)

## Examples of usage

### Generate a simple RPC service

```bash
grpc-init --service GreetService \
  --methods "sayHello,askAge" \
  --fields "name:string" \
  --request GreetRequest \
  --response GreetResponse
```

### Generate CRUD service

```bash
grpc-init --service UserService \
  --crud \
  --model "User:id:int32,name:string,email:string"
```

or with separated fields from model:

```bash
grpc-init --service UserService \
  --crud \
  --model User \
  --fields "id:int32,name:string,email:string"
```

### Generate Enhanced RPCs (with streaming)

```bash
grpc-init --service ZombieService \
  --methods "transformToZombie|unary|id:int32|stream|message:string;sayHello|unary|name:string|unary|message:string"
```

### Combine CRUD + Enhanced

```bash
grpc-init --service UserService \
  --crud \
  --model "User:id:int32,name:string,email:string" \
  --methods "streamStats|stream|User|unary|longmessage:string"
```

### Create proto file and compile it

```bash
grpc-init --service UserService \
  --crud \
  --model "User:id:int32,name:string,email:string" \
  --methods "streamStats|stream|User|unary|longmessage:string"
  --compile
```

## Limitations

While this CLI tool covers many common use cases, there are some known limitations to be aware of:

### No Automatic `.proto` Imports

- External message types (e.g., shared User messages across files) must be manually imported.
- The CLI does not currently auto-resolve or manage import paths between .proto files.

> You can still use import manually and reuse message types in enhanced methods after proto file generation (but the compiling will be also done manually 😢)

### Proto3-Only Support

This tool generates .proto files strictly in proto3 syntax.

### Other limmitations (can be added in future releases)

- Nested messages
- `oneof` fields
- The optional `--compile` step only generates Python gRPC code using grpcio-tools

## Author

<img src="https://avatars.githubusercontent.com/u/100163733?size=128" alt="Achraf MATAICH" width="64" height="64" style="border-radius: 50%;">

Achraf MATAICH <achraf.mataich@outlook.com>