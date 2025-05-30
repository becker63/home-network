TODO tmr

1. <MAYBE> Move the golang FRP schema generation code to its own github repo
  * Write a github workflow to periodically generate it
  * Maybe create a repo for all kcl schema generation

2. Reorganize scripts
  * We dont need a src dir remove it
  * Give root/scripts a better name, like kcl-tasks

3. More verbose pytest output
  * What source file and kcl file is it actually running?

4. Helper for kcl mod import
  * Wrap the UpdateDependencies_Args with our projects defaults (where our root kcl module is)

5. Add a way to mark kcl files as library only
  * do some title/filter magic like export_* to only synth yaml for those files
  * some of our kcl code will be like library code and not exported
