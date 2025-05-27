
import kcl_lib.api as api

args = api.ExecProgram_Args(k_filename_list=["path/to/kcl.k"])
api = api.API()
result = api.exec_program(args)
print(result.yaml_result)
