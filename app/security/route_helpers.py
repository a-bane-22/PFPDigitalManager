from plotly.graph_objs.scatter import Line

color_list = ['black', 'blue', 'cyan', 'green', 'red']


def line_generator(line_number=0):
    color_index = line_number % len(color_list)
    return Line(color=color_list[color_index], dash='solid', width=3)
