# Principles

## Function Names

This is already a plotting library, Function names should not include "plot" suffix/prefix

e.g., instead of `plot_scatter` use `scatter`

instead of `violin_plot` use `violin`

### Multi vs Single Plotting Names

in the case of multi-plots, functions should change to plural form. e.g., `scatter` to `scatters`

## Abstractions

Abstractions should be done **modarately**. they come with cost in the form of *reduction* in *customizability* and *flexibility*.

Plots already returh customizable plot objects, So many things can be added later by the user.

Rather than taking everything as an argument, accept only non-customizable parts of the plot or for user comfort.

e.g., do not take color palette name as an argument

1. It limits color palettes that can be used...
2. User can always change the color palette by themselves such as `+scale_color_viridis()`

### Multi-Plot Abstractions

For multi-plots though, it might be accaptable to take a `scale_color/fill_*` as an argument. Since, gggrid is not customizable in terms of color.
