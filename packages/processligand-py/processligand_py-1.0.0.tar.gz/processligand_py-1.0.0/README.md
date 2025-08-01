# ProcessLigand as a Python Package

A Python package designed to prepare arguments and run `ProcessLigand`.

---

## Example usage:

```
from processligandpy import run_processligand

result = run_processligand(f='path/to/target_or_ligand')

# Using arguments:
# result = run_processligand(f='path/to/target_or_ligand', target=True, atom_index=1)

# Optional:
output = result.stdout
error = result.stderr
returncode = result.returncode
```

---

## Arguments

### Required Argument

| Arg | Description                                        |
|:----|:---------------------------------------------------|
| `f` | Input file (not listed in the provided dictionary) |

### Optional Arguments

| Flag         | Value Type            | Description                          |
|:-------------|:----------------------|:-------------------------------------|
| `target`     | `<BOOL>`              | Parse a target                       |
| `v`          | `<INT>`               | Verbose level                        |
| `o`          | `<STR>`               | Output base filename                 |
| `e`          | `<STR>`               | Residue to extract                   |
| `c`          | `<STR>`               | Convert molecule to specified format |
| `atom_index` | `<INT>`               | Starting atom index                  |
| `res_name`   | `<STR>`               | 3-char ligand code                   |
| `res_chain`  | `<CHAR>`              | Ligand chain                         |
| `res_number` | `<INT>`               | Ligand number                        |
| `force_gpa`  | `<INT>`               | Force reference atom                 |
| `force_pcg`  | `<FLOAT FLOAT FLOAT>` | Force protein center of geometry     |
| `hf`         | `<BOOL>`              | Include hydrogen flexible bonds      |
| `wh`         | `<BOOL>`              | Add hydrogen atoms in output         |
| `ref`        | `<BOOL>`              | Output final PDB from IC             |
| `gen3D`      | `<BOOL>`              | Generate 3D conformation             |


---

### Raises

| Exception            | Description                                    |
|:---------------------|:-----------------------------------------------|
| `FileNotFoundError`  | If the required input file 'f' does not exist. |
| `ProcessLigandError` | If the external process fails to execute.      |

---
### Returns

| Type                  | Description                                                       |
|:----------------------|:------------------------------------------------------------------|
| `ProcessLigandResult` | A namedtuple containing `stdout`, `stderr`, and the `returncode`. |
