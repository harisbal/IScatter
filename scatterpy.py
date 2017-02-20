import numpy as np
import pandas as pd
from scipy import stats
from tornado.ioloop import IOLoop

from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from bokeh.layouts import column
from bokeh.models import (ColumnDataSource, Label, BoxSelectTool,
                          PanTool, WheelZoomTool, PolySelectTool,
                          ResetTool, HoverTool, RadioButtonGroup)
from bokeh.plotting import figure
from bokeh.server.server import Server

io_loop = IOLoop.current()


def modify_doc(doc):
    def update_src(attr, old, new):
        src_scatter.data = dict(x=[], y=[], descr=[])
        src_regrline.data = dict(x=[], y=[])
        citation.text = 'Invalid Source'

        try:
            if new == 0:
                df = pd.read_excel('data.xlsx')
            elif new == 1:
                df = pd.read_clipboard(header=None, thousands=',')
                if len(df.columns) == 2:
                    df.columns = ['x', 'y']
                else:
                    df.columns = ['descr', 'x', 'y']

            df[['x', 'y']] = df[['x', 'y']].apply(pd.to_numeric)
            src_scatter.data = ColumnDataSource.from_df(df)
            update_regr(df.x, df.y)
        except:
            if new == 2:
                citation.text = 'Cleared'

    def update_sel(attr, old, new):
        # Selected Indices
        inds = np.array(new['1d']['indices'])

        # Original Data
        # TOdo ask Babis for cleaner way to write it
        x = np.array(src_scatter.data['x'])
        y = np.array(src_scatter.data['y'])

        if len(inds) != 0 and len(inds) != len(x):
            # Get selected data
            x = x[inds]
            y = y[inds]
        update_regr(x, y)

    def update_regr(x, y):
        (slope, intercept, r_value, p_value, std_err) = stats.linregress(x, y)
        xline = np.linspace(min(x), max(x), 2)
        yline = intercept + slope * xline
        src_regrline.data = dict(x=xline, y=yline)
        eq_str = r'y = {:.2f} * x {:+.2f} | R2 = {:.3f}'
        regr_eq = eq_str.format(slope, intercept, r_value**2)
        citation.text = regr_eq

    hover = HoverTool(
        tooltips=[
            ("index", "$index"),
            ("(x,y)", "(@x, @y)"),
            ("desc", "@desc"),
        ]
    )

    toolset = [PanTool(), WheelZoomTool(), BoxSelectTool(),
               PolySelectTool(), ResetTool(), hover]

    src_scatter = ColumnDataSource(data=dict(x=[], y=[], descr=[]))
    src_regrline = ColumnDataSource(data=dict(x=[], y=[]))

    # create the scatter plot
    p = figure(tools=toolset, plot_width=600, plot_height=600,
               min_border=10, min_border_left=50, toolbar_location='right',
               x_axis_location='below', y_axis_location='left',
               title='ScatterPy')
    p.background_fill_color = "#fafafa"

    p.toolbar.active_drag = None
    p.toolbar.active_scroll = None
    p.toolbar.active_tap = None

    r = p.scatter('x', 'y', size=3, color="#3A5785", alpha=0.6,
                  source=src_scatter)

    r.data_source.on_change('selected', update_sel)

    # Plot the line
    p.line('x', 'y', source=src_regrline)

    # Set the widgets
    btn_src = RadioButtonGroup(labels=['From xlsx', 'From Clipboard', 'Clear'],
                               active=-1)

    btn_src.on_change('active', update_src)

    citation = Label(x=90, y=510, x_units='screen', y_units='screen',
                     render_mode='css', border_line_color='black',
                     border_line_alpha=1.0, background_fill_color='white',
                     background_fill_alpha=1.0)

    p.add_layout(citation)

    doc.add_root(column(btn_src, p))
    doc.title = 'scatterpy'

bokeh_app = Application(FunctionHandler(modify_doc))

server = Server({'/': bokeh_app}, io_loop=io_loop)
server.start()

if __name__ == '__main__':
    print('Opening Bokeh application on http://localhost:5006/')

    io_loop.add_callback(server.show, "/")
    io_loop.start()
