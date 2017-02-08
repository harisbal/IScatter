''' Present a scatter plot with linked histograms on both axes.
Use the ``bokeh serve`` command to run the example by executing:

    bokeh serve IScatter.py

at your command prompt. Then navigate to the URL

    http://localhost:5006/IScatter

in your browser.

'''

import tkinter as tk
import numpy as np
import pandas as pd
from scipy import stats


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        b1 = tk.Button(root, text="Copy from Clipboard",
                       command=lambda: self.bokeh_plot('clipboard'))

        b2 = tk.Button(root, text="Use data.xlsx",
                       command=lambda: self.bokeh_plot('spreadsheet'))
        b1.pack()
        b2.pack()

    def bokeh_plot(self, input_src):
        from bokeh.models import (ColumnDataSource, Label, BoxSelectTool,
                                  PanTool, WheelZoomTool, PolySelectTool,
                                  ResetTool, HoverTool)
        from bokeh.plotting import figure, curdoc

        if input_src == 'spreadsheet':
            df = pd.read_excel('data.xlsx')
        else:
            df = pd.read_clipboard(header=None)
            colNames = ['description', 'x', 'y']
            if len(df.columns) == 3:
                df.columns = colNames
            elif len(df.columns) == 2:
                df.columns = colNames[1:]
            else:
                print('Invalid clipboard input')
                return 0

        # create three normal population samples with different parameters
        x = df.x
        y = df.y

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

        toolset = [PanTool(), WheelZoomTool(), BoxSelectTool(),
                   PolySelectTool(), ResetTool(), hover]

        # create the scatter plot
        p = figure(tools=toolset, plot_width=600, plot_height=600,
                   min_border=10, min_border_left=50,
                   toolbar_location='right',
                   x_axis_location='below', y_axis_location='left',
                   title='IScatter')
        p.background_fill_color = "#fafafa"

        p.toolbar.active_drag = None
        p.toolbar.active_scroll = None
        p.toolbar.active_tap = None

        r = p.scatter(x, y, size=3, color="#3A5785", alpha=0.6, source=source)

        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        xline = np.linspace(min(x), max(x), 2)
        yline = intercept + slope * xline
        src_line = ColumnDataSource(data=dict(x=xline, y=yline))
        eq_str = r'y = {:.2f} * x {:+.2f} | R2 = {:.3f}'
        regr_eq = eq_str.format(slope, intercept, r_value**2)

        p.line('x', 'y', source=src_line)

        citation = Label(x=90, y=510, x_units='screen', y_units='screen',
                         text=regr_eq, render_mode='css',
                         border_line_color='black', border_line_alpha=1.0,
                         background_fill_color='white',
                         background_fill_alpha=1.0)

        p.add_layout(citation)
        layout = p
        curdoc().add_root(layout)
        curdoc().title = 'IScatter'
        r.data_source.on_change('selected', self.update)

    def update(self, attr, old, new):
        inds = np.array(new['1d']['indices'])
        if len(inds) == 0 or len(inds) == len(x):
            x_regr = x
            y_regr = y
        else:
            x_regr = x[inds]
            y_regr = y[inds]
        (slope, intercept, r_value,
         p_value, std_err) = stats.linregress(x_regr, y_regr)
        xline = np.linspace(min(x_regr), max(x_regr), 2)
        yline = intercept + slope * xline
        self.src_line.data = dict(x=xline, y=yline)
        eq_str = r'y = {:.2f} * x {:+.2f} | R2 = {:.3f}'
        regr_eq = eq_str.format(slope, intercept, r_value**2)
        citation.text = regr_eq

if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
    
