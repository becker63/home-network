write a python library to iterate over `infra/**.k` files with a callback function with helpful
color coding on subfolders like bootstrap (use a hashmap with the key being the path and the value being the color).

could maybe also do some fun gradient stuff by instead representing it as an array of paths

I would like the iterator to automatically output debug info for me. It should print what file we're at and what
subfolder we're at on each iteration.

we can use the callback to do things like generate yaml or do specific things when inside the bootstrap dir 
or run specific valedations for specific dirs like an frp dir

add a filter parameter to only iterate on specific dirs like frp or bootstrap. That way we can cleanly write seperate logic


maybe look into pythons iterator api

or just write a function that will return an array with the k files from the dir we filtered.


array of enum types for filter param?


Need a way to do basic boolean logic on filters: EG: `not bootstrap`


```python
#iterator idea psuedo code:


for yamlFile in projectFilter(not direnums.Bootstrap)
    runKubernetesValidations(yamlFile)

```

```js
//js-like callback psuedo code:

projectFilter(not direnums.Bootstrap, (yamlFile) => {
	runKubernetesValidations(yamlFile)
	})
```
