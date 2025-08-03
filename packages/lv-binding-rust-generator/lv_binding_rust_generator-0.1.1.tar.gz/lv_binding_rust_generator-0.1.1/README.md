# lv_binding_rust

This project aims to provide basic Rust bindings for lvgl.

However, unlike the official Rust bindings project, this project makes minimal assumptions. For example, it makes no assumptions about the lvgl version number, and doesn't even care whether the lvgl codebase has been modified.

Given the complexities of C language conditional compilation, compilers, and compilation environments, this project doesn't attempt to parse C structs in memory, but simply provides wrappers with the same name.

This project also doesn't aim for complete API integrity, and the resulting code may not even be directly compiled by Rust, but it will significantly reduce the workload.

I will strive to maintain consistency in directory structure, file names, function names, parameter names, and type names, and do everything possible to avoid introducing ambiguity or new constructs.

Contributions are welcome.
