<p align="center"><img width="40.0%" src="pics/sah.png"></p>


The Spectral Analysis for Hydrogenous samples (SAH) allows researchers to dive into INS, Raman and FTIR spectral data.

Named after the ancient egyptian god Sah, the personification of the constellation Orion and highly related with Osiris.

Check the [full documentation online](https://pablogila.github.io/sah/).


# Index

| | |  
| --- | --- |  
| [classes](https://pablogila.github.io/sah/sah/classes.html)     | Definition of the `Spectra`, `Plotting` and `Material` classes, instantiated as `sah.Class()` |  
| [fit](https://pablogila.github.io/sah/sah/fit.html)             | Spectral fitting functions |  
| [normalize](https://pablogila.github.io/sah/sah/normalize.html) | Spectra normalisation |  
| [deuterium](https://pablogila.github.io/sah/sah/deuterium.html) | Deuteration estimation functions |  
| [plot](https://pablogila.github.io/sah/sah/plot.html)           | Spectra plotting, as `sah.plot(Spectra)` |  
| [samples](https://pablogila.github.io/sah/sah/samples.html)     | Sample materials for testing |  


# Examples

To load two INS spectra CSV files with cm$^{-1}$ as input units,
and plot them in meV units, normalizing their heights over the range from 20 to 50 meV:
```python
import sah
# Set plotting parameters
plotting_options = sah.Plotting(
    title     = 'Calculated INS',
    )
# Load the spectral data
ins = sah.Spectra(
    type     = 'INS',
    files    = ['example_1.csv', 'example_2.csv'],
    units_in = 'cm-1',
    units    = 'meV',
    plotting = plotting_options,
    )
# Normalize the spectra
sah.normalize.height(spectra=ins, range=[20, 50])
# Plot the spectra
sah.plot(ins)
```

More examples in the [`examples/`](https://github.com/pablogila/sah/tree/main/examples) folder.


---


# Contributing

If you are interested in opening an issue or a pull request, please feel free to do so on [GitHub](https://github.com/pablogila/sah/).  
For major changes, please get in touch first to discuss the details.  


## Code style

Please try to follow some general guidelines:  
- Use a code style consistent with the rest of the project.  
- Include docstrings to document new additions.  
- Include automated tests for new features or modifications, see [automated testing](#automated-testing).  
- Arrange function arguments by order of relevance. Most implemented functions follow something similar to `function(file, key/s, value/s, optional)`.  


## Automated testing

If you are modifying the source code, you should run the automated tests of the [`tests/`](https://github.com/pablogila/sah/tree/main/tests) folder to check that everything works as intended.
To do so, first install PyTest in your environment,
```bash
pip install pytest
```

And then run PyTest inside the base directory,
```bash
pytest -vv
```


## Compiling the documentation

The documentation can be compiled automatically to `docs/sah.html` with [Pdoc](https://pdoc.dev/) and [ATON](https://pablogila.github.io/aton), by running:
```shell
python3 makedocs.py
```

This runs Pdoc, updating links and pictures, and using the custom theme CSS template from the `css/` folder.


---


# License

Copyright (C) 2025 Pablo Gila-Herranz  
This program is free software: you can redistribute it and/or modify
it under the terms of the **GNU Affero General Public License** as published
by the Free Software Foundation, either version **3** of the License, or
(at your option) any later version.  
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the attached GNU Affero General Public License for more details.  

