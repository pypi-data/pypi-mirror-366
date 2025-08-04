import os
import re
import shutil
import fire
import toolz.curried as T
from pathlib import Path
from typing import List, Generator
from functools import wraps

from pprint import pprint

indent = " " * 4

native_type_map = {
    "char": "c_char",
    "double": "c_double",
    "float": "c_float",
    "int": "c_int",
    "long": "c_long",
    "long long": "c_longlong",
    "short": "c_short",
    "unsigned char": "c_uchar",
    "unsigned int": "c_uint",
    "unsigned long": "c_ulong",
    "unsigned long long": "c_ulonglong",
    "unsigned short": "c_ushort",
    "int8_t": "i8",
    "int16_t": "i16",
    "int32_t": "i32",
    "int64_t": "i64",
    "uint8_t": "u8",
    "uint16_t": "u16",
    "uint32_t": "u32",
    "uint64_t": "u64",
    "ssize_t": "isize",
    "size_t": "usize",
    "void": "c_void",
}

@T.curry
def apply(f):
    @wraps(f)
    def _(args):
        return f(*args)
    return _

line_comment_pattern = re.compile(r'//.*')
def remove_line_comments(code: str) -> str:
    return line_comment_pattern.sub('', code)

block_comment_pattern = re.compile(r'/\*.*?\*/', re.DOTALL)
def remove_block_comments(code: str) -> str:
    # pattern = re.compile(
    #     r'//.*?$|/\*.*?\*/',
    #     re.DOTALL | re.MULTILINE
    # )
    return block_comment_pattern.sub('', code)

lvgl_include_line_pattern = re.compile(r'#include\s+[<"]([^">]*?(?:lvgl|lv_)[^">]*)[>"]')
def extract_and_remove_lvgl_includes(code: str) -> tuple[str, List[str]]:
    return lvgl_include_line_pattern.sub('', code), lvgl_include_line_pattern.findall(code)

preprocessor_line_pattern = re.compile(r'^\s*#.*$', re.MULTILINE)
def remove_preprocessor_lines(code: str) -> str:
    return preprocessor_line_pattern.sub('', code)

empty_line_pattern = re.compile(r'^\s*\n', re.MULTILINE)
def remove_empty_lines(code: str) -> str:
    return empty_line_pattern.sub('', code)

const_pattern = re.compile(r'\bconst\b\s*')
def remove_all_const(code: str) -> str:
    return const_pattern.sub('', code)

extern_pattern = re.compile(r'\bextern\b\s*')
def remove_all_extern(code: str) -> str:
    return extern_pattern.sub('', code)

def flatten_function_signatures(code: str) -> str:
    lines = code.splitlines()
    result = []
    buffer = []
    in_signature = False

    for line in lines:
        stripped = line.strip()

        if not in_signature:
            if re.search(r'\w+\s*\(', stripped) and not stripped.endswith(';') and not ')' in stripped:
                buffer = [stripped]
                in_signature = True
            else:
                result.append(line)
        else:
            buffer.append(stripped)
            if ')' in stripped and stripped.endswith(';'):
                combined = ' '.join(buffer)
                result.append(combined)
                buffer = []
                in_signature = False

    if buffer:
        result.append(' '.join(buffer))

    return '\n'.join(result)

static_line_pattern = re.compile(r'^.*\bstatic\b.*$\n?', re.MULTILINE)
def remove_static_lines(code: str) -> str:
    return static_line_pattern.sub('', code)

ellipsis_line_pattern = re.compile(r'^.*\.\.\..*$\n?', re.MULTILINE)
def remove_ellipsis_lines(code: str) -> str:
    return ellipsis_line_pattern.sub('', code)

# def remove_brace_blocks(code: str) -> str:
#     pattern = r'\{(?:[^{}]*|(?R))*\}'
#     return regex.sub(pattern, '', code)

typedef_line_pattern = re.compile(r'^\s*typedef\b.*?;\s*$', re.MULTILINE)
def extract_and_remove_typedef_lines(code: str) -> tuple[str, List[str]]:
    return typedef_line_pattern.sub('', code), typedef_line_pattern.findall(code)

enum_block_pattern = re.compile(r'\b(?:typedef\s+)?enum(?:\s+\w+)?\s*{.*?}\s*(?:\w+\s*)?;', re.DOTALL | re.MULTILINE)
def extract_and_remove_enum_blocks(code: str) -> tuple[str, List[str]]:
    return enum_block_pattern.sub('', code),  enum_block_pattern.findall(code)

def preproces_code(code: str) -> str:
    code = T.pipe(
        code,
        remove_line_comments,
        remove_block_comments,
    )

    code, lvgl_includes = extract_and_remove_lvgl_includes(code)

    code = T.pipe(
        code,
        remove_preprocessor_lines,
        remove_empty_lines,
        remove_all_const,
        remove_all_extern,
        flatten_function_signatures,
        remove_static_lines,
        remove_ellipsis_lines,
    )

    code, typedef_lines = extract_and_remove_typedef_lines(code)
    code, enum_blocks = extract_and_remove_enum_blocks(code)

    return code, lvgl_includes, typedef_lines, enum_blocks

def find_h_files(directory: Path, excluded: List[str]) -> Generator[str, None, None]:
    yield from directory.rglob("*.h")

param_pattern = re.compile(r'^\s*(?P<type>.+?)(?P<name>\w+)(?P<array>(?:\s*\[\s*\])*)\s*$')
function_pattern = re.compile(r'^(?P<type>\w[\w\s\*\d]+?)\s*(?P<array>\[\s*\d*\s*\])?\s+(?P<name>\w+)\s*\((?P<params>.*?)\)\s*(?P<suffix>(?:\w+\([^)]*\))*)\s*;\s*$', re.MULTILINE)
def parse_h_files(code: str) -> List[str]:
    def parse_params(params: str):
        if params.strip() == "void":
            return []
        
        return T.pipe(
            params.split(","),
            T.map(lambda s: s.strip()),
            T.map(param_pattern.match),
            T.map(lambda m: m.groupdict()),
            T.map(T.valmap(lambda s: s.strip())),
            list,
        )

    return T.pipe(
        code.splitlines(),
        T.filter(lambda s: "&" not in s),
        T.map(function_pattern.match),
        T.filter(bool),
        T.map(lambda m: m.groupdict()),
        T.map(lambda f: {
            **f,
            "params": parse_params(f["params"]),
        }),
        list,
    )

@T.curry
def convert_type(typedef_set, info: dict) -> dict:
    info["type"] = info["type"].replace("struct ", "").strip()
    info["type"] = info["type"].replace("enum ", "").strip()
    info["type"] = info["type"].replace("union ", "").strip()

    ptr = False
    if info["type"].endswith("*"):
        ptr = True
        info["type"] = info["type"].replace("*", "").strip()
    elif info["array"] and info["array"].strip():
        ptr = True

    clean_type = re.sub(r'\b[A-Z0-9_]{2,}\b', '', info["type"]).strip()
    if clean_type:
        info["type"] = clean_type

    if info["type"] in native_type_map:
        info["type"] = f"{native_type_map[info["type"]]}"
    elif ptr:
        typedef_set.add(info["type"])

    info["mut"] = "*mut " if ptr else ""
    return info
    
@T.curry
def convert_params(typedef_set, params: List[dict]) -> str:
    return T.pipe(
        params,
        T.map(convert_type(typedef_set)),
        T.map(lambda param: {**param, "name": param["name"] if param["name"] not in ["fn", "type"] else f"r#{param['name']}"}),
        T.map(lambda param: f"{param['name']}{': ' if param['name'] else ''}{param['mut']}{param['type']}"),
        ', '.join,
    )

@T.curry
def convert_return_type(typedef_set, info: dict) -> str:
    if info["type"] == "void" and (not info["array"] or not info["array"].strip()):
        return "()"
    
    info = convert_type(typedef_set, info)
    
    return f"{info['mut']}{info['type']}"

def convert_enum_block(code: str) -> tuple[str, List[tuple[str, int]]]:
    pattern = re.compile(
        r"""
        (?:typedef\s+)?             # optional typedef
        enum
        (?:\s+(?P<name_head>\w+))?  # optional name before {
        \s*
        \{(?P<enum_body>.*?)\}      # enum body (non-greedy)
        \s*
        (?P<name_tail>[\w\s,]*)?    # optional tail name(s), e.g., "Status", "X, Y"
        \s*
        ;
        """,
        re.DOTALL | re.VERBOSE
    )
    matches = pattern.match(code)
    if not matches:
        return "", []

    info = matches.groupdict()
    enum_body = info["enum_body"]
    enum_name = info["name_tail"] or info["name_head"]
    entries = [e.strip() for e in enum_body.split(',')]

    def try_eval_enum_expr(expr, last_value):
        if expr.strip() == "" and last_value is not None:
            return last_value + 1
        
        try:
            allowed_names = {"__builtins__": None}
            return eval(expr, allowed_names, {})
        except Exception as e:
            try:
                allowed_names = {"__builtins__": None}
                expr = re.sub(
                    r'\b(\d+|0x[0-9a-fA-F]+)(?:[uU][lL]{0,2}|[lL]{1,2}[uU]?|[uU]|[lL]{1,2})\b',
                    r'\1',
                    expr.strip()
                ).strip()
                return eval(expr, allowed_names, {})
            except Exception as e:
                pass

        return None

    result = []
    last_value = -1

    for entry in filter(None, entries):
        if '=' in entry:
            name, expr = entry.split('=', 1)
        else:
            name, expr = entry, ""

        name = name.strip()

        if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', name):
            print(f"Illegal enumeration item name: '{name}'")
            return "", []

        value = try_eval_enum_expr(expr.strip(), last_value)
        if value is not None:
            result.append((name, value))
            last_value = value
        else:
            value = expr.strip()
            result.append((name, value))
            last_value = None

    return enum_name, result
    
@T.curry
def convert_typedef(typedef_set, code: str) -> str:
    code = code.replace("struct ", "").strip()
    code = code.replace("enum ", "").strip()
    code = code.replace("union ", "").strip()

    try:
        m = re.match(r'^\s*typedef\s+([a-zA-Z_][a-zA-Z0-9_<>]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*;', code)
        if m:
            old_type, new_type = m.groups()
            if old_type in native_type_map:
                old_type = f"{native_type_map[old_type]}"
            return f"pub type {new_type} = {old_type};"
        
        m = re.match(r'^\s*typedef\s+(?P<type>.+?)\s*\(\*(?P<name>\w+)\)\s*\((?P<params>.*)\)\s*;', code)
        if m:
            f = m.groupdict()
                
            param_pattern = re.compile(r'^\s*(?P<type>.+?)(?:\s+(?P<name>\w+))?(?P<array>(?:\s*\[\s*\])*)\s*$')

            def parse_params(params: str):
                if params.strip() == "void":
                    return []
                
                return T.pipe(
                    params.split(","),
                    T.map(lambda s: s.strip()),
                    T.map(param_pattern.match),
                    T.map(lambda m: m.groupdict()),
                    T.map(T.valmap(lambda s: s.strip() if isinstance(s, str) else "")),
                    list,
                )
            
            f["params"] = parse_params(f["params"])

            f["params"] = convert_params(typedef_set, f["params"])

            f["array"] = ""
            f["type"] = convert_return_type(typedef_set, f)

            return f"pub type {f['name']} = Option<unsafe extern \"C\" fn({f['params']}) -> {f['type']}>;"
    except Exception as e:
        print(f"Error parsing typedef: {code}")
        return ""

def generate_rs_file(file: Path) -> str:
    with open(file, "r") as fd:
        code, lvgl_includes, typedef_lines, enum_blocks = preproces_code(fd.read())

    typedef_set = set()
    _convert_return_type = convert_return_type(typedef_set)
    _convert_params = convert_params(typedef_set)
    _convert_typedef = convert_typedef(typedef_set)

    content_extern_C = T.pipe(
        code,
        parse_h_files,
        T.map(lambda f: {
            **f,
            "params": _convert_params(f["params"]),
            "type": _convert_return_type(f),
        }),
        T.map(lambda f: f"pub fn {f['name']}({f['params']}) -> {f['type']};"),
        T.map(lambda l: f"{indent}{l}"),
        '\n'.join,
        lambda s: f'extern "C" {{\n{s}\n}}' if s else "",
    )

    content_typedef = T.pipe(
        T.concatv(
            T.pipe(
                typedef_set,
                T.map(lambda t: f"pub type {t} = c_void;"),
            ),
            T.pipe(
                typedef_lines,
                T.map(_convert_typedef),
                T.filter(None),
            ),
        ),
        '\n'.join,
    )

    content_enums = T.pipe(
        enum_blocks,
        T.map(convert_enum_block),
        T.filter(lambda e: e[1]),
        T.map(apply(lambda name, entry: T.pipe(
            entry,
            T.map(apply(lambda e, v: f"pub const {e}: {name if name else "u32"} = {v};")),
            '\n'.join,
            lambda items: f"pub type {name} = u32;\n\n{items}" if name else items,
        ))),
        '\n\n'.join,
    )

    content_includes = T.pipe(
        lvgl_includes,
        T.map(lambda p: T.pipe(
            p.removesuffix(".h"),
            lambda p: p.split("/"),
            lambda ss: [] if "lv_conf_internal" in ss else ss,
            T.map(lambda s: s.replace("..", "super")),
            "::".join,
            lambda p: f"pub use super::{p}::*;" if p else "",
        )),
        '\n'.join,
    )

    content = T.pipe(
        [
            "#![allow(non_camel_case_types)]",
            "use std::ffi::*;",
            content_includes,
            content_typedef,
            content_enums,
            content_extern_C,
        ],
        '\n\n'.join,
    )

    return content

def get_rs_file_path(output_dir: Path, file: Path) -> Path:
    return output_dir / file.parent / f"{file.stem}.rs"

def generate(lvgl_src_dir: str, output_dir: str = "out", excluded: List[str] = []):
    root = T.pipe(
        lvgl_src_dir,
        Path,
        lambda path: path / "src",
    )

    shutil.rmtree(output_dir, ignore_errors=True)

    for file in find_h_files(root, excluded):
        outfile = get_rs_file_path(Path(output_dir) / "lvgl", file.relative_to(root))
        outfile.parent.mkdir(parents=True, exist_ok=True)
        with open(outfile, "w") as fd:
            try:
                content = generate_rs_file(file)
            except Exception as e:
                print(f"Error {file}: {e}")
            else:
                fd.write(content)

    build_rust_crate(Path(output_dir) / "lvgl")

def build_rust_crate(root_dir: Path):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        with open(f"{dirpath}.rs", "w") as fd:
            T.pipe(
                T.concatv(dirnames, T.map(lambda f: f[:-3], filenames)),
                T.map(lambda mod: f"pub mod {mod};"),
                '\n'.join,
                fd.write,
            )
            
def main():
    fire.Fire(generate)

if __name__ == "__main__":
    main()
