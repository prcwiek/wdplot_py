from numpy import arange
import math
import matplotlib.pyplot as plt
#import matplotlib.font_manager as font_manager
import pandas as pd
from pathlib import Path
from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny.ui import head_content, tags

# function weibull return a probability for given parameters:
# c scale factor
# k shape factor
# ws wind speed

def weibull(c, k, ws):
    return((k/c)*((ws/c)**(k-1)) * math.exp(-(ws/c)**k))

def mean_wind_speed(c,k):
    return c* math.gamma(1+1/k)

app_ui = ui.page_fluid(
    head_content(
        tags.style((Path(__file__).parent / "www/style.css").read_text())
    ),
                
    ui.row(
        ui.column(4,      
                  ui.h1("Weibull Distribution"),
                  ui.h3("Create Weibull distribution graph"),
                  ui.input_numeric("c", label = ui.h5("Scale factor c"), value = 7.0, step = 0.1, min = 0),
                  ui.input_numeric("k", label = ui.h5("Shape factor k"), value = 2.0, step = 0.1, min = 0),
                  ui.input_slider("range", label = ui.h5("Range of wind speeds"),
                                 min = 0, max = 25, value = [0,25]),
                  tags.style((Path(__file__).parent / "www/ion.rangeSlider.css").read_text())),

        ui.column(4, 
               ui.output_plot("wbplot", width='800px', height='600px'),
               ui.output_text("text1"), offset = 1)
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    
    mean_ws=reactive.Value(0)
    
    @reactive.Effect
    @reactive.event(input.c)
    def _():
        mean_ws.set(mean_wind_speed(input.c(), input.k()))
        
    @reactive.Effect
    @reactive.event(input.k)
    def _():
        mean_ws.set(mean_wind_speed(input.c(), input.k()))
    
    @output
    @render.plot
    def wbplot():
        c=input.c()
        k=input.k()
        min=input.range()[0]
        max=input.range()[1]
        ddist = pd.DataFrame(data=arange(0,30,0.1), columns=['wind_speed'])
        ddist['probability'] = ddist['wind_speed'].apply(lambda x: weibull(c, k, x))
        fig, ax = plt.subplots()
        #font=font_manager.FontProperties(family='Oswald')
        
        ax.plot(ddist.wind_speed, ddist.probability, color='#A52A2A',   
                label='Weibull distribution\nc={:.2f}\nk={:.2f}'.format(c,k) )
        ax.set_title("Weibull distribution")
        ax.set_xlabel("Wind speed (m/s)")
        ax.set_ylabel("Probability")
        ax.legend()
        plt.xlim(min, max)
        plt.ylim(0, 0.3)
        plt.xticks(range(min,max,5))
        plt.yticks(arange(0, 0.30, 0.05))
        
        return fig
    
    @output
    @render.text
    def text1():
        mean_ws_p=mean_ws.get()
        return f"Mean wind speed {mean_ws_p:.2f}  m/s"

app = App(app_ui, server)
