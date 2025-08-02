import fire
import regex
import toolz.curried as T
from pathlib import Path
from typing import List, Generator

from pprint import pprint

params_pattern = regex.compile(r'(?:const\s+)?(?P<param_type>(?:unsigned\s+|signed\s+)?(?:\w+\s*\*?\s*)+?)\s+(?P<param_name>\w+)')
function_pattern = regex.compile(r"""
    ^
    (?=[a-zA-Z])
    (?:const\s+)?
    (?P<return_type>[\w\s\*]+?)
    \s+
    (?P<func_name>\w+)
    \s*
    \(
        \s*
        (?P<params>
            void
            |
            (?:
                (?:const\s+)?[\w\s\*]+?\s+\w+\s*(?:,\s*|)*
            )*
            |
            \s*
        )
    \)
    \s*;
    \s*$
    """, regex.VERBOSE)

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

def find_h_files(directory: Path, excluded: List[str]) -> Generator[str, None, None]:
    yield from directory.rglob("*.h")

def remove_c_comments(code: str) -> str:
    pattern = regex.compile(
        r'//.*?$|/\*.*?\*/',
        regex.DOTALL | regex.MULTILINE
    )
    return regex.sub(pattern, '', code)

def remove_brace_blocks(code: str) -> str:
    pattern = r'\{(?:[^{}]*|(?R))*\}'
    return regex.sub(pattern, '', code)

def parse_h_files(file: Path):
    with open(file, "r") as fd:
        def parse_params(params: str):
            return T.pipe(
                params.split(","),
                T.map(lambda s: s.strip()),
                T.map(params_pattern.match),
                T.filter(bool),
                T.map(lambda m: m.groupdict()),
                list,
            )

        return T.pipe(
            fd.read(),
            remove_c_comments,
            remove_brace_blocks,
            lambda code: code.splitlines(),
            T.filter(bool),
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
def convert_params(param_type_set, params: List[dict]) -> str:
    ptr_pattern = regex.compile(r'(\w+)\s*\*')

    def convert_param(param: dict) -> str:
        if ptr_pattern.match(param["param_type"]):
            param['param_type'] = param['param_type'].replace('*', '').strip()

            if param['param_type'] in native_type_map:
                param['param_type'] = f"{native_type_map[param['param_type']]}"
            else:
                param_type_set.add(param['param_type'])

            return f"{param['param_name']}: *mut {param['param_type']}"
        else:
            if param['param_type'] in native_type_map:
                param['param_type'] = f"{native_type_map[param['param_type']]}"
                
            return f"{param['param_name']}: {param['param_type']}"
        
    return T.pipe(
        params,
        T.map(convert_param),
        ', '.join,
    )

@T.curry
def convert_return_type(param_type_set, return_type: str) -> str:
    if return_type == "void":
        return "()"
    
    ptr_pattern = regex.compile(r'(\w+)\s*\*')

    if ptr_pattern.match(return_type):
        return_type = return_type.replace('*', '').strip()

        if return_type in native_type_map:
            return_type = f"{native_type_map[return_type]}"
        else:
            param_type_set.add(return_type)

        return f"*mut {return_type}"
    else:
        if return_type in native_type_map:
            return_type = f"{native_type_map[return_type]}"

        return f"{return_type}"
    
def convert_h_file(file: Path) -> str:
    param_type_set = set()
    _convert_return_type = convert_return_type(param_type_set)
    _convert_params = convert_params(param_type_set)

    content_extern = T.pipe(
        file,
        parse_h_files,
        T.map(lambda f: {
            **f,
            "return_type": _convert_return_type(f["return_type"]),
            "params": _convert_params(f["params"]),
        }),
        T.map(lambda f: f"pub fn {f['func_name']}({f['params']}) -> {f['return_type']};"),
        T.map(lambda l: f"    {l}"),
        '\n'.join,
        lambda s: f'extern "C" {{\n{s}\n}}' if s else "",
    )

    content_typedef = T.pipe(
        param_type_set,
        T.map(lambda t: f"pub type {t} = c_void;"),
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

def gen(lvgl_src_dir: str, output_dir: str = "binding", excluded: List[str] = []):
    root = T.pipe(
        lvgl_src_dir,
        Path,
        lambda path: path / "src",
    )

    for file in find_h_files(root, excluded):
        print(file)

        outfile = get_rs_file_path(Path(output_dir), file.relative_to(root))

        try:
            content = convert_h_file(file)
        except Exception as e:
            print(f"Error: {e}")
        else:
            if not content.strip():
                continue
            
            outfile.parent.mkdir(parents=True, exist_ok=True)
            with open(outfile, "w") as fd:
                fd.write(content)

def main():
    fire.Fire(gen)

if __name__ == "__main__":
    main()
