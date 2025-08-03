import os
import re
import shutil
import fire
import toolz.curried as T
from pathlib import Path
from typing import List, Generator

from pprint import pprint

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

preprocessor_line_pattern = re.compile(r'^\s*#.*$', re.MULTILINE)
def remove_preprocessor_lines(code: str) -> str:
    return preprocessor_line_pattern.sub('', code)

empty_line_pattern = re.compile(r'^\s*\n', re.MULTILINE)
def remove_empty_lines(code: str) -> str:
    return empty_line_pattern.sub('', code)

const_pattern = re.compile(r'\bconst\b\s*')
def remove_all_const(code: str) -> str:
    return const_pattern.sub('', code)

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
def extract_typedef_lines(code: str) -> List[str]:
    return typedef_line_pattern.findall(code)
def remove_typedef_lines(code: str) -> str:
    return typedef_line_pattern.sub('', code)

def preproces_code(code: str) -> str:
    code = T.pipe(
        code,
        remove_line_comments,
        remove_block_comments,
        remove_preprocessor_lines,
        remove_empty_lines,
        remove_all_const,
        flatten_function_signatures,
        remove_static_lines,
        remove_ellipsis_lines,
    )

    typedef_lines = extract_typedef_lines(code)
    code = remove_typedef_lines(code)

    return code, typedef_lines

def find_h_files(directory: Path, excluded: List[str]) -> Generator[str, None, None]:
    yield from directory.rglob("*.h")

params_pattern = re.compile(r'^\s*(?P<type>.+?)(?P<name>\w+)(?P<array>(?:\s*\[\s*\])*)\s*$')
function_pattern = re.compile(r'^(?P<type>\w[\w\s\*\d]+?)\s*(?P<array>\[\s*\d*\s*\])?\s+(?P<name>\w+)\s*\((?P<params>.*?)\)\s*(?P<suffix>(?:\w+\([^)]*\))*)\s*;\s*$', re.MULTILINE)
def parse_h_files(code: str) -> List[str]:
    def parse_params(params: str):
        if params.strip() == "void":
            return []
        
        return T.pipe(
            params.split(","),
            T.map(lambda s: s.strip()),
            T.map(params_pattern.match),
            T.map(lambda m: m.groupdict()),
            T.map(T.valmap(lambda s: s.strip())),
            list,
        )

    return T.pipe(
        code.splitlines(),
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
    ptr = False
    if info["type"].endswith("*"):
        ptr = True
        info["type"] = info["type"].strip("*").strip()
    elif info["array"] and info["array"].strip():
        ptr = True

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
        T.map(lambda param: f"{param['name']}: {param['mut']}{param['type']}"),
        ', '.join,
    )

@T.curry
def convert_return_type(typedef_set, info: dict) -> str:
    if info["type"] == "void" and (not info["array"] or not info["array"].strip()):
        return "()"
    
    info = convert_type(typedef_set, info)
    
    return f"{info['mut']}{info['type']}"
    
def generate_rs_file(file: Path) -> str:
    with open(file, "r") as fd:
        code, typedef_lines = preproces_code(fd.read())

    typedef_set = set()
    _convert_return_type = convert_return_type(typedef_set)
    _convert_params = convert_params(typedef_set)

    content_extern = T.pipe(
        code,
        parse_h_files,
        T.map(lambda f: {
            **f,
            "params": _convert_params(f["params"]),
            "type": _convert_return_type(f),
        }),
        T.map(lambda f: f"pub fn {f['name']}({f['params']}) -> {f['type']};"),
        T.map(lambda l: f"    {l}"),
        '\n'.join,
        lambda s: f'extern "C" {{\n{s}\n}}' if s else "",
    )

    content_typedef = T.pipe(
        typedef_set,
        T.map(lambda t: f"#[allow(non_camel_case_types)]\npub type {t} = c_void;"),
        '\n'.join,
    )

    content = T.pipe(
        [
            "use std::ffi::*;" if content_typedef else "",
            content_typedef,
            content_extern,
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
        try:
            content = generate_rs_file(file)
        except Exception as e:
            print(f"Error {file}: {e}")
        else:
            if not content.strip():
                continue
            
            outfile = get_rs_file_path(Path(output_dir) / "lvgl", file.relative_to(root))
            outfile.parent.mkdir(parents=True, exist_ok=True)
            with open(outfile, "w") as fd:
                fd.write(content)

    build_rust_crate(Path(output_dir) / "lvgl")

def build_rust_crate(root_dir: Path):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        with open(f"{dirpath}.rs", "w") as fd:
            T.pipe(
                T.concatv(dirnames, T.map(lambda f: f.strip(".rs"), filenames)),
                T.map(lambda mod: f"pub mod {mod};"),
                '\n'.join,
                fd.write,
            )
            
def main():
    fire.Fire(generate)

if __name__ == "__main__":
    main()
