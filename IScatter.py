''' Present a scatter plot with linked histograms on both axes.
Use the ``bokeh serve`` command to run the example by executing:

    bokeh serve IScatter.py

at your command prompt. Then navigate to the URL

    http://localhost:5006/IScatter

in your browser.

'''

import numpy as np
import pandas as pd
from scipy import stats

from bokeh.models import (ColumnDataSource, Label, BoxSelectTool, 
                          PanTool, WheelZoomTool, PolySelectTool, ResetTool,
                          HoverTool)
from bokeh.plotting import figure, curdoc

df = pd.read_excel('data.xlsx')
# create three normal population samples with different parameters
x = df.x
y = df.y
descr = df.description.tolist()

source = ColumnDataSource(
        data=dict(
            x=df.x,
            y=df.y,
            desc=df.description,
        )
    )
        
hover = HoverTool(
        tooltips=[
            ("index", "$index"),
            ("(x,y)", "(@x, @y)"),
            ("desc", "@desc"),
        ]
    )

toolset= [PanTool(),WheelZoomTool(),BoxSelectTool(),
        PolySelectTool(),ResetTool(),hover]

# create the scatter plot
p = figure(tools=toolset, plot_width=600, plot_height=600, min_border=10, min_border_left=50,
           toolbar_location='right', x_axis_location='below', y_axis_location='left',
           title='IScatter')
p.background_fill_color = "#fafafa"

p.toolbar.active_drag = None
p.toolbar.active_scroll = None
p.toolbar.active_tap = None

r = p.scatter(x, y, size=3, color="#3A5785", alpha=0.6, source=source)

slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
xline = np.linspace(min(x),max(x),2)
yline = intercept + slope * xline
source_line = ColumnDataSource(data=dict(x=xline, y=yline))
regr_eq = r'y = {:.2f} * x {:+.2f} | R2 = {:.3f}'.format(slope, intercept,r_value**2)

p.line('x','y',source=source_line)

citation = Label(x=90, y=510, x_units='screen', y_units='screen',
                 text=regr_eq, render_mode='css',
                 border_line_color='black', border_line_alpha=1.0,
                 background_fill_color='white', background_fill_alpha=1.0)

p.add_layout(citation)
layout = p
curdoc().add_root(layout)
curdoc().title = 'IScatter'

def update(attr, old, new):
    inds = np.array(new['1d']['indices'])
    if len(inds) == 0 or len(inds) == len(x):
        x_regr = x
        y_regr = y
    else:
        x_regr = x[inds]
        y_regr = y[inds]
    slope, intercept, r_value, p_value, std_err = stats.linregress(x_regr,y_regr)
    xline = np.linspace(min(x_regr),max(x_regr),2)
    yline = intercept + slope * xline
    source_line.data=dict(x=xline, y=yline)
    regr_eq = r'y = {:.2f} * x {:+.2f} | R2 = {:.3f}'.format(slope, intercept,r_value**2)
    citation.text = regr_eq
r.data_source.on_change('selected', update)