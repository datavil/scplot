from lets_plot import *
from lets_plot import (
    LetsPlot,
    aes,
    arrow,
    element_blank,
    element_line,
    element_text,
    geom_blank,
    geom_jitter,
    geom_point,
    geom_segment,
    geom_violin,
    gggrid,
    ggplot,
    ggsize,
    ggtb,
    guide_colorbar,
    guide_legend,
    guides,
    labs,
    layer_tooltips,
    scale_color_brewer,
    scale_color_continuous,
    scale_color_gradient,
    scale_color_hue,
    scale_color_viridis,
    scale_shape,
    theme,
    theme_classic,
)

LetsPlot.setup_html()


# ------------------------------ EXAMPLE STRUCTURE ------------------------------
def example(func):
    def wrapper(*args, **kwargs):
        # MUST DO: merge the default kwargs with the user-provided kwargs
        all_kwargs = func.__kwdefaults__
        all_kwargs.update(kwargs)
        # ------------------------------------------------------

        """ modify the output
        result = func(*args, **kwargs)

        # handle the case
        if all_kwargs.get("example"):
            result += something 
        else:
            pass
            
        return result
        """

    # MUST DO: inherit the default kwargs
    wrapper.__kwdefaults__ = func.__kwdefaults__  # inherit the default kwargs
    return wrapper


# ------------------------------ INTERACTIVE ------------------------------
def interactive(func):
    def wrapper(*args, **kwargs):
        # merge the default kwargs with the user-provided kwargs
        all_kwargs = func.__kwdefaults__
        all_kwargs.update(kwargs)
        # ------------------------------------------------------

        # get the value of the `interactive` kwarg
        inter = all_kwargs.get("interactive")
        if inter is True:
            return func(*args, **kwargs) + ggtb()
        elif inter is False:
            return func(*args, **kwargs)
        else:
            msg = f"expected True or False for 'interactive' argument, but received {inter}"
            raise ValueError(msg)

    wrapper.__kwdefaults__ = func.__kwdefaults__  # inherit the default kwargs
    return wrapper


def arrow_axis(func):
    def modifier(*args, **kwargs):
        # merge the default kwargs with the user-provided kwargs
        all_kwargs = func.__kwdefaults__
        all_kwargs.update(kwargs)
        # ------------------------------------------------------

        plot = func(*args, **kwargs)

        if all_kwargs.get("axis_type") == "arrow":
            arrow_size = kwargs.get("arrow_size")
            plot += theme(
                # remove axis elements
                axis_text_x=element_blank(),
                axis_text_y=element_blank(),
                axis_ticks_y=element_blank(),
                axis_ticks_x=element_blank(),
                axis_line=element_blank(),
                # position axis titles according to arrow size
                axis_title_x=element_text(hjust=arrow_size / 2),
                axis_title_y=element_text(hjust=arrow_size / 2),

            )
        elif all_kwargs.get("axis_type") == "axis":
            plot += theme()

        return plot

    modifier.__kwdefaults__ = func.__kwdefaults__  # inherit the default kwargs
    return modifier
