# copied from app0102.py
# &amp; in alphabetical dropdown fixed
# cleaned up code for deployment
# fixed selection bug with alphabetical makers


import pandas as pd
import logging
import geopy
import geopandas

# Load data 
from shared import *
from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shinywidgets import render_plotly, render_widget, output_widget
import plotly.express as px
import plotly.graph_objects as go

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import cross_val_score

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

from shiny import App, ui

# Compute static values
Year_range = (min(Tarisio.Year), max(Tarisio.Year))
Maker = Tarisio['Maker'].unique().tolist()

TopMakers = Tarisio.groupby('Maker')[['SalePrice']].sum().sort_values(by='SalePrice',ascending=False).reset_index()
TopMakers = TopMakers['Maker'].unique().tolist()
TopMakers = list(filter(lambda x: str(x) != 'nan', TopMakers))

Instrument = Tarisio['Instrument'].unique().tolist()
Instrument = sorted(Instrument)

# Wiki boxplot reference
url = 'https://en.wikipedia.org/wiki/Box_plot' 

# Contact page image
here = Path(__file__).parent

app_ui = ui.page_navbar(
    
####################  ABOUT INPUT  ################
   
    ui.nav_panel("About",
        ui.card(
            ui.h1("Welcome To My Tarisio.com Dashboard"),
            
            ui.p("This dashboard was made to explore and visualize  \
                Tarisio.com’s Cozio Archive, \
                the world’s largest database for the auction of fine stringed \
                instruments and bows. \
                It includes over 55,000 auction records for 14 types of instruments made by \
                3,573 unique makers. Auction records \
                span a period of almost 200 years, with the earliest dating \
                to 1829. Data for this app was collected in October 2024 and does not \
                include sales records or corrections made to the site since then."
            ),
        
            ui.p("It is my hope that this dashboard will provide a fun and easy way to explore \
                Tarisio's sales records by both instrument and maker, and to enable users to compare makers \
                within a selected price range."
            ),
       
        ),   
        
        ui.card(   
            ui.h2("About Instruments and Makers"),
            
            ui.card(  
                ui.p("Tarisio's Cozio Archive includes 14 different \
                instruments, \
                not all of which are represented equally. The Archive is made up primarily of auction \
                records for violins and violin bows, with those instruments making \
                up almost 75% of the data. Hover over each instrument type to see how many auction entries appear \
                    for that type."),
                ui.h4("Number of Auction Sales by Instrument:"),
                output_widget('instrument_counts_treemap'),
            ),
             
            ui.card(    
                ui.p("The amount of wealth each maker brings to auction varies considerably. The top 50 \
                    makers contributing the highest net sales at auction are visualized \
                    below. Instruments by Andrea Amati, while highly valued, are so rare that they appear \
                    only five times in the archive. Other makers, Sartory and \
                    Peccatte, for example, specialized in bow making, with relatively large numbers of \
                    instruments passing through auction houses. Hill & Sons crafted many types of instruments, \
                    with thousands of bows passing through the archive, making their instrument counts \
                    quite large. Hover over a maker's name to see their total sales \
                    and the number of their instruments that have been sold."),
                ui.h4("Total Auction Sales by Maker - Top 50 Makers:"),
                output_widget('top_makers_treemap'),
            ), 
        ),
    ),
  
################### INSTRUMENTS INPUT ###############
    
    ui.nav_panel("Instruments",
                 
        ui.card(
            ui.h2('Explore Sales by Instrument'),
            ui.input_selectize(
                "instrumentsfilter",
                "Select an instrument:",
                Instrument,
                selected='Violin',
            ),

            ui.output_text("instrument_value"),
            ui.p("Select an instrument type to see how its values have changed \
                over time. Because the price scale for individual instruments varies from a few \
                hundred dollars in the 1830s to more than $15 million in 2024, the data has been \
                partitioned into 3 plots. The first plot contains all the data for instruments \
                over the 185 year range of data. The second plot zooms in to look more closely \
                at the first 100 years, while the third plot considers the middle region when \
                prices begin to take off."),

            ui.p(""),
            ui.p(""),
            output_widget("instrument_plot"),
        ),
        
        ui.card(
            ui.p("A few makers dominate the data. \
                Of the 36 string instruments that have sold for more than $1 million dollars, 35 of them are by 3 makers: \
                Antonio Stradivari, Bartolomeo Giuseppe 'del Gesù' Guarneri, and Giovanni Battista Guadagnini. \
                With only 314 sales records, these 3 makers account for almost 20% of the wealth in the data. "),
            ui.p("Bows by Nicolas Eugène Sartory make up 12.8% of bow auction sales. \
                Bows by Tourte 'le Jeune' have the 4th highest aggregate bow sales but \
                claim the highest individual bow prices. Thirteen of the top 20 most valuable bows that have passed \
                through these auction houses are Tourte violin and cello bows."),
            ui.p("Choose an instrument above. Then select a maker in the checkboxes below to highlight their data \
                throughout the plots. With the exception of Tourte, these makers appear in order of \
                highest total sales. Note that \
                Guadagnini's instruments do not appear until after \
                1935. Bows, in general, do not appear until 1969. Other instrument selections\
                may appear later as well, or sparsely, producing empty plots for some date ranges."),
            ui.row(
                ui.column(4,
                    ui.card(
                        ui.input_checkbox("highlight_Strad", "Antonio Stradivari (violins, violas, cellos, small violins)", value=False), 
                        ui.input_checkbox("highlight_Guadagnini", "Giovanni Battista Guadagnini (violins, cellos, violas, beginning in 1935)", value=False),
                        ui.input_checkbox("highlight_Vuillaume", "Jean-Baptiste Vuillaume (violins, violas, cellos, small violins; violin, cello, and viola bows)", value=False),
                        ui.input_checkbox("highlight_Gesu", "Guarneri 'del Gesù' (violins)", value=False),


                        ui.h5("Select a 'Bow' type in the first dropdown menu to see data for Sartory and Tourte."),
                        
                        ui.input_checkbox("highlight_Sartory", "Eugène Nicolas Sartory (bows and small violins; no violins by this maker.)", value=False),
                        ui.input_checkbox("highlight_Tourte", "Tourte, François Xavier 'le Jeune' (bows; no violins by this maker.)", value=False),
                    ),
                ),
                
                ui.column(8,
                    ui.card(
                        ui.row(output_widget("instrument_zoom1_plot")),
                        ui.row(output_widget("instrument_zoom2_plot")),
                    ),
                ),

            ),
       
        ),
        
        ui.card(
            ui.p("For better visualization, outliers have been removed."),
            ui.output_plot("instrument_by_decade_plot"), 
            ui.tags.a("For more information on boxplots",
                    href=url,
                    target='_blank'),
        ),
    ),


################### MAKERS INPUT ###########
      
    ui.nav_panel("Makers",
    
        ui.card(
            ui.h2('Explore Sales by Maker'),
            ui.p("There are two ways to search auction records for makers. \
                The dropdown menu for the first plot is ordered by \
                makers with the highest, aggregate auction sales. These are the makers with the \
                richest sales histories. To explore a maker \
                of your own choosing, use the second plot below, with makers ordered alphabetically."),
            
            ui.p("Hover over points \
                in each plot to see the instrument type and sale price for that auction record. \
                The red, 2-degree polynomial line is for \
                visualization purposes, to show the trend in auction prices. "),
        
            ui.input_selectize(
                "topmakers",
                "Select a maker:",
                TopMakers,
            ),
            
            ui.card(    
                
                ui.p("Select instruments to highlight:"),
                ui.row(
                    ui.column(2,
                        ui.input_checkbox("highlight_Violin", "Violins", value=False), 
                        ui.input_checkbox("highlight_Viola", "Violas", value=False),
                        ui.input_checkbox("highlight_Cello", "Cellos", value=False),
                        ui.input_checkbox("highlight_Bass", "Basses", value=False),
                        
                        ui.input_checkbox("highlight_ViolinBow", "Violin Bows", value=False),
                        ui.input_checkbox("highlight_ViolaBow", "Viola Bows", value=False),
                        ui.input_checkbox("highlight_CelloBow", "Cello Bows", value=False),
                        ui.input_checkbox("highlight_BassBow", "Bass Bows", value=False),
                    ),
                    ui.column(10, output_widget('topmaker_plot'))
                ),
            ),
        ),
    
        ui.card(
            ui.p(""),
    
            ui.input_selectize(
                "makerletter",
                "First letter of maker's last name:",
                choices = sorted({name[0].upper() for name in Maker}),
                selected = 'S',
            ),
                
            ui.input_selectize(
                "makername",
                "Select a maker:",
                choices = [],
            ),
            
            ui.card(
    
                ui.p("Select instruments to highlight:"),

                ui.row(
                    ui.column(
                        2,
                        ui.input_checkbox("highlight_Violin2", "Violins", value=False), 
                        ui.input_checkbox("highlight_Viola2", "Violas", value=False),
                        ui.input_checkbox("highlight_Cello2", "Cellos", value=False),
                        ui.input_checkbox("highlight_Bass2", "Basses", value=False),
                        
                        ui.input_checkbox("highlight_ViolinBow2", "Violin Bows", value=False),
                        ui.input_checkbox("highlight_ViolaBow2", "Viola Bows", value=False),
                        ui.input_checkbox("highlight_CelloBow2", "Cello Bows", value=False),
                        ui.input_checkbox("highlight_BassBow2", "Bass Bows", value=False),
                    ),
                    ui.column(10, output_widget('maker_plot'))
                ),
            
            ),
            
        ),
               
        ui.card(
            ui.p("For better visualization, outliers have been removed."),
            ui.output_plot("maker_by_decade_plot"),
            ui.tags.a("For more information on boxplots",
                    href=url,
                    target='_blank'),
        ),
    ),


################### PRICE RANGE INPUT ###############

    ui.nav_panel("Price Range",       
        ui.card(
            ui.h2('Explore Instruments by Price Range'),
            
            ui.p("This table contains sales benchmarks for each maker in the dataset. \
                Select an instrument type. \
                Then enter a price range in the 'most recent sale price' \
                column to compare makers whose most recent sales records for that instrument \
                are within that price range. Use the Makers Page for \
                additional reference."), 
                    
            ui.row(
                ui.column(1,
                ),
                ui.column(11,
                    ui.input_selectize(
                        "instrumentsfiltercomp",
                        "Select an instrument:",
                        Instrument,
                        selected='Violin',           
                    ),

                ),
            
            ),    
            ui.output_data_frame("data_instrument_table"),
        
        ),

    ),    
    
#################### CONTACT INPUT ##################

    ui.nav_panel("Contact", 
        ui.card(    
            ui.row(
                ui.column(6,
                    ui.output_image("image"), 
                ),     
                ui.column(6, 
                    ui.p("Margaret Bowers is studying Data Science with NYC Data \
                        Science Academy. She earned a B.S. in Physics from the \
                        University of Rochester and studied violin performance at the \
                        Eastman School of Music. She \
                        is a professional violinist with the Spokane Symphony Orchestra \
                        in Spokane, Washington."),
                    ui.tags.p("Contact: margaret.bowers@gmail.com."),
                    ui.tags.i("photo: Instruments of the Spokane Symphony Orchestra"),
                ),               
                          
            ),
            
        ),
        
    ),
    
#################### PAGE AESTHETICS ####################
    
    
    title="Tarisio Dashboard",
    id="page",
    bg = '#9c2a2a', # background header color
    inverse=True,
       
    
)

#########################################################
def server(input, output, session):
    

########## ABOUT TAB  ################
    
    @render_plotly
    def instrument_counts_treemap():
        # Instruments and counts
        inst_numbers = Tarisio.groupby('Instrument').count().reset_index()
        # Create df with instrument and counts
        inst_numbers = inst_numbers[['Instrument', 'SaleDate']]
        inst_numbers.rename(columns={'SaleDate':'Number'}, inplace=True)
        
        custom_colors = ["#9c2a2a","#faebd7",'#e5c08f',"#c1b193","#3e4e6c","#c0c0c0","#360a08"]
        
        # Tree map with instrument counts
        fig = px.treemap(
            inst_numbers,
            path=["Instrument"],            # Hierarchical path for treemap
            values="Number",                # Sizes of the squares
            hover_data={"Number": True},    # Additional hover data
            color_discrete_sequence=custom_colors,  
        )

        # Customize hover template
        fig.update_traces(
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Number of instruments: %{value}<br>"
            )
        )

        fig.update_traces(
            textposition="middle center",
            textfont_size = 25
        )

        return fig
        
    @render_plotly
    def top_makers_treemap():
        # df of total sales by makers:
        total_sales_df = Tarisio.groupby(['Maker'])[['SalePrice']].sum().sort_values(by='SalePrice',ascending=False).reset_index()
        total_sales_df.rename(columns={'SalePrice':'NetSales'}, inplace=True)    

        # df of instrument counts for makers 
        inst_counts_df = Tarisio.groupby('Maker')['SaleDate'].count()
        inst_counts_df = pd.DataFrame(inst_counts_df).reset_index()
        inst_counts_df.rename(columns={'SaleDate':'InstCounts'}, inplace=True)
        
        # merge total sales and total instrument counts by maker and keep only the top 50
        top_50 = total_sales_df.merge(inst_counts_df, on='Maker')
        top_50 = top_50.drop(top_50.tail(3523).index)
        
        # calculate the average instrument value for each maker (NetSales / InstCounts)
        top_50 = top_50.assign(AverageInstValue = lambda x: (x['NetSales']/x['InstCounts']))
        
        # Create list of instruments for makers 
        maker_inst_list_df = pd.DataFrame(Tarisio.groupby('Maker')['Instrument'].unique().reset_index())
        maker_inst_list_df.rename(columns={'Instrument':'InstrList'}, inplace=True)
        
        # Ensure InstrList is converted from NumPy arrays to strings
        maker_inst_list_df['InstrList'] = maker_inst_list_df['InstrList'].apply(
            lambda x: ', '.join(x.tolist()) if isinstance(x, np.ndarray) else x
        )
                
        # Add list of maker instruments to the top 50 makers
        top_50 = top_50.merge(maker_inst_list_df, on='Maker')
            
        # Create a treemap of top 50 makers by total instrument sales
        fig = px.treemap(
            top_50,
            path=["Maker"],     # Hierarchical path for treemap
            values="NetSales",  # Sizes of treemap squares
            custom_data=['InstCounts','InstrList'],
            color_discrete_sequence=custom_colors,  
        )

        # Customize hover template 
        fig.update_traces(
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Net Sales: $%{value}<br>"
                "Number of Instruments: %{customdata[0]}<br>"
                "Types of Instruments: %{customdata[1]}"
            )
        )

        fig.update_traces(
            textposition="middle center",
            textfont_size = 25
        )

        return fig

    
    @render_plotly 
    ############# average price per instrument ###################
    def top_instruments_treemap():
        # df of total sales by makers:
        total_sales_df = Tarisio.groupby(['Maker'])[['SalePrice']].sum().sort_values(by='SalePrice',ascending=False).reset_index()
        total_sales_df.rename(columns={'SalePrice':'NetSales'}, inplace=True)    

        # df of instrument counts for makers 
        inst_counts_df = Tarisio.groupby('Maker')['SaleDate'].count()
        inst_counts_df = pd.DataFrame(inst_counts_df).reset_index()
        inst_counts_df.rename(columns={'SaleDate':'InstCounts'}, inplace=True)
        
        # merge total sales and total instrument counts by maker and keep only the top 50
        top_50 = total_sales_df.merge(inst_counts_df, on='Maker')
        top_50 = top_50.drop(top_50.tail(3523).index)
        
        # calculate the average instrument value for each maker (NetSales / InstCounts)
        top_50 = top_50.assign(AverageInstValue = lambda x: (x['NetSales']/x['InstCounts']))

        # Create a treemap of top 50 makers by average instrument values
        fig = px.treemap(
            top_50,
            path=["Maker"],             # Hierarchical path for treemap
            values="AverageInstValue",  # Sizes of the squares
            hover_data={"AverageInstValue": True, "NetSales": True, "InstCounts": True},  # Additional hover data
            title="Average Instrument Auction Price by Maker - Top 50 Makers"
        )

        # Customize hover template 
        fig.update_traces(
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Average price per instrument: $%{value}<br>"
                "InstCounts: %{customdata[2]}"
            )
        )

        return fig   
   
    
########## INSTRUMENTS TAB ####################
    
    @reactive.Calc
    def filtered_instrument_data():
        selected_instrument = input.instrumentsfilter()
        return Tarisio[Tarisio['Instrument'] == selected_instrument]
    
    ##### Checkboxes ########
    def checkbox_filter(): 
        # Highlight mappings for maker checkboxes, to be applied to all plots
        data = filtered_instrument_data()
        highlight_mappings = {
            "highlight_Strad": ("Stradivari", "Stradivari, Antonio"),
            "highlight_Gesu": ("del Gesu", "Guarneri, Bartolomeo Giuseppe 'del Gesù'"),
            "highlight_Guadagnini": ("Guadagnini", "Guadagnini, Giovanni Battista"),
            "highlight_Vuillaume": ("Vuillaume", "Vuillaume, Jean-Baptiste"),
            "highlight_Sartory": ("Sartory", "Sartory, Eugène Nicolas"),
            "highlight_Tourte": ("Tourte", "Tourte, François Xavier 'le Jeune'"), 
        }
        
        # Apply categories based on checkbox status
        def categorize_maker(maker):
            categories = []
            if input.highlight_Strad() and "Stradivari, Antonio" in maker:
                categories.append("Stradivari")
            if input.highlight_Gesu() and "Guarneri, Bartolomeo Giuseppe 'del Gesù'" in maker:
                categories.append("del Gesu")
            if input.highlight_Guadagnini() and "Guadagnini, Giovanni Battista" in maker:
                categories.append("Guadagnini")            
            if input.highlight_Vuillaume() and "Vuillaume, Jean-Baptiste" in maker:
                categories.append("Vuillaume")            
            if input.highlight_Sartory() and "Sartory, Eugène Nicolas" in maker:
                categories.append("Sartory")            
            if input.highlight_Tourte() and "Tourte, François Xavier 'le Jeune'" in maker:
                categories.append("Tourte")
    
            return " & ".join(categories) if categories else "Other"

        data['Instrument Maker'] = data['Maker'].apply(categorize_maker)
        return data

    
    ####### Instrument plot for full range of data: 1829-2024 ####################################################
    
    @render_plotly
    def instrument_plot():
        data = checkbox_filter()
        
        # Check if any makers are selected
        selected_makers = data['Instrument Maker'].unique()
        no_makers_selected = len(selected_makers) 
    
        # If no makers are selected, label as 'All Makers'; otherwise, keep 'Other' for unselected data
        if no_makers_selected == 1:
            data['Instrument Maker'] = 'All Makers'
        else:
            # Ensure 'Other' is applied to unselected data
            data.loc[~data['Instrument Maker'].isin(selected_makers), 'Instrument Maker'] = 'Other'
        
        # Group by 'Year' for selected instrument df to get total sale price and count of sales per year
        yearly_data = data.groupby(['Year', 'Instrument Maker']).agg(
            total_sale_price=('SalePrice', 'sum'),
            sale_count=('SalePrice', 'count')
        ).reset_index()
        
        # Create the histogram using aggregated data
        fig = px.bar(
            data_frame = yearly_data,
            x = "Year",
            y = "total_sale_price" ,
            color='Instrument Maker',
            color_discrete_map=color_map,
            labels={'total_sale_price': 'Total Sales', 'Year': 'Year'},
        )
        
        fig.update_layout(
            title={
                'text': f"{input.instrumentsfilter()} Sales 1829-2024",
                'x': 0.45,      # Center the title
                'xanchor': 'center',
                'yanchor': 'top',
            }
        )
        
        fig.update_traces(
            hovertemplate ='Year: %{x}<br>Total Sales: $%{y}<br>Intsruments Sold: %{customdata}',
            customdata=yearly_data['sale_count']
        )
        
        return fig
    
    
    ####### Instrument plot for 1829-1930 data ####################################################
    
    @render_plotly
    def instrument_zoom1_plot():
        data = checkbox_filter()

        # Check if any makers are selected
        selected_makers = data['Instrument Maker'].unique()
        no_makers_selected = len(selected_makers) 
    
        # If no makers are selected, label as 'All Makers'; otherwise, keep 'Other' for unselected data
        if no_makers_selected == 1:
            data['Instrument Maker'] = 'All Makers'
        else:
            # Ensure 'Other' is applied to unselected data
            data.loc[~data['Instrument Maker'].isin(selected_makers), 'Instrument Maker'] = 'Other'
    
        # Group by Year and Sales_Type
        yearly_data = data.groupby(['Year', 'Instrument Maker']).agg(
            total_sale_price=('SalePrice', 'sum'),
            sale_count=('SalePrice', 'count')
        ).reset_index()
        
        # Create the bar chart with color differentiation
        fig = px.bar(
            data_frame=yearly_data,
            x="Year",
            y="total_sale_price",
            color="Instrument Maker",
            color_discrete_map=color_map,
            labels={'total_sale_price': 'Total Sales', 'Year': 'Year'},
        )

        # Customize the chart layout
        fig.update_layout(
            title={
                'text': f"{input.instrumentsfilter()} Sales 1829-1930",
                'x': 0.44,      # Center the title
                'xanchor': 'center',
                'yanchor': 'top',
            }
        )
        
        fig.update_traces(
            hovertemplate ='Year: %{x}<br>Total Sales: $%{y}<br>Intsruments Sold: %{customdata}',
            customdata=yearly_data['sale_count']
        )
        
        # Set the date range
        fig.update_yaxes(range=[0, 15000])
        fig.update_xaxes(range=[1829, 1930])

        return fig
    

    ####### Instrument plot for 1930-1965 data ####################################################
    
    @render_plotly
    def instrument_zoom2_plot():

        data = checkbox_filter()
        
        # Check if any makers are selected
        selected_makers = data['Instrument Maker'].unique()
        no_makers_selected = len(selected_makers) 
       
        # If no makers are selected, label as 'All Makers'; otherwise, keep 'Other' for unselected data
        if no_makers_selected == 1:
            data['Instrument Maker'] = 'All Makers'
        else:
            # Ensure 'Other' is applied to unselected data
            data.loc[~data['Instrument Maker'].isin(selected_makers), 'Instrument Maker'] = 'Other'

        # Group by Year and Sales_Type
        yearly_data = data.groupby(['Year', 'Instrument Maker']).agg(
            total_sale_price=('SalePrice', 'sum'),
            sale_count=('SalePrice', 'count')
        ).reset_index()

        # Create the histogram using aggregated data
        fig = px.bar(
            data_frame = yearly_data,
            x = "Year",
            y = "total_sale_price",
            color='Instrument Maker',
            color_discrete_map=color_map,
            labels = {'total_sale_price': 'Total Sales', 'Year': 'Year'},
        )
        
        # Center the title
        fig.update_layout(
            title={
                'text': f"{input.instrumentsfilter()} Sales 1930-1965",
                'x': 0.44,      # Center the title
                'xanchor': 'center',
                'yanchor': 'top',
            }
        )
        
        fig.update_traces(
            hovertemplate ='Year: %{x}<br>Total Sales: $%{y}<br>'
        )
        
        # Set the date range
        fig.update_yaxes(range=[0,70000])
        fig.update_xaxes(range=[1930,1965])
        
        return fig      
    
    ####### Instrument boxplot trend by decade ####################################################

    @render.plot
    def instrument_by_decade_plot():
        
        data_by_decade = filtered_instrument_data()
        
        # Add a decade column to the df
        data_by_decade['Decade'] = (data_by_decade['Year'] // 10) * 10
        
        # Box plot by decade
        plt.figure(figsize=(14, 8))
        fig = sns.set_theme()   # set defaults: grey background and white grid lines
        fig = sns.boxplot(x='Decade', y='SalePrice', data=data_by_decade, showfliers=False)
        plt.xlabel('Decade')
        plt.ylabel('Price in Dollars')
        plt.title(f"Distribution of {input.instrumentsfilter()} Sales by Decade")
        plt.xticks(rotation=45)
        plt.tight_layout(pad=2)

        return fig
    

################### MAKERS TAB ###############
     
    @reactive.Calc
    def filtered_maker_data():
        selected_maker = input.makername()
        # return Tarisio[Tarisio['Maker'] == selected_maker]
        
        # Keep only needed columns
        df = Tarisio[Tarisio['Maker'] == selected_maker]
        df = df[['Maker','Instrument','Year','SalePrice']]
        return df
    
    @reactive.Calc
    # return selected top maker
    def top_maker_data():
        top_maker = input.topmakers()
        
        # Keep only the needed columns
        df = Tarisio[Tarisio['Maker'] == top_maker]
        df = df[['Maker','Instrument','Year','SalePrice']]
        return df
    
    ##### Instrument Checkboxes for top makers ########
    def checkbox_filter_instruments(): 
        # Highlight mappings for instrument checkboxes
        data = top_maker_data()
        highlight_mappings = {
            "highlight_Violin": ("Violin", "Violin"),
            "highlight_Viola": ("Viola", "Viola"),
            "highlight_Cello": ("Cello", "Cello"),
            "highlight_Bass": ("Bass", "Bass"),
            
            "highlight_ViolinBow": ("Bow", "Violin Bow"), 
            "highlight_ViolaBow": ("Bow", "Viola Bow"), 
            "highlight_CelloBow": ("Bow", "Cello Bow"), 
            "highlight_BassBow": ("Bow", "Bass Bow"), 
        }
    
        # Apply categories based on checkbox status
        def categorize_instrument(instrument):
            inst_categories = []
            if input.highlight_Violin() and ("Violin" in instrument and "Violin Bow" not in instrument):
                inst_categories.append("Violin")
            if input.highlight_Viola() and ("Viola" in instrument and "Viola Bow" not in instrument):
                inst_categories.append("Viola")            
            if input.highlight_Cello() and ("Cello" in instrument and "Cello Bow" not in instrument):
                inst_categories.append("Cello")            
            if input.highlight_Bass() and ("Bass" in instrument and "Bass Bow" not in instrument):
                inst_categories.append("Bass")
                
            if input.highlight_ViolinBow() and "Violin Bow" in instrument:
                inst_categories.append("Bow")            
            if input.highlight_ViolaBow() and "Viola Bow" in instrument:
                inst_categories.append("Bow")            
            if input.highlight_CelloBow() and "Cello Bow" in instrument:
                inst_categories.append("Bow")                        
            if input.highlight_BassBow() and "Bass Bow" in instrument:  
                inst_categories.append("Bow")            
        
            return " & ".join(inst_categories) if inst_categories else "Other"

        data['Category'] = data['Instrument'].apply(categorize_instrument)

        return data
    
    ############
    
    ##### Instrument Checkboxes for alphabetical makers ########
    def checkbox_filter_instruments2(): 
        # Highlight mappings for instrument checkboxes
        data = filtered_maker_data()
        highlight_mappings = {
            # highlight_instrument: (instrument category reference, name as it appears in df)
            "highlight_Violin2": ("Violin", "Violin"),
            "highlight_Viola2": ("Viola", "Viola"),
            "highlight_Cello2": ("Cello", "Cello"),
            "highlight_Bass2": ("Bass", "Bass"),
            
            "highlight_ViolinBow2": ("Bow", "Violin Bow"), 
            "highlight_ViolaBow2": ("Bow", "Viola Bow"), 
            "highlight_CelloBow2": ("Bow", "Cello Bow"), 
            "highlight_BassBow2": ("Bow", "Bass Bow"),     
        }
    
        # Apply categories based on checkbox status
        def categorize_instrument2(instrument):
            inst_categories2 = []
            if input.highlight_Violin2() and ("Violin" in instrument and "Violin Bow" not in instrument):
                inst_categories2.append("Violin")
            if input.highlight_Viola2() and ("Viola" in instrument and "Viola Bow" not in instrument):
                inst_categories2.append("Viola")            
            if input.highlight_Cello2() and ("Cello" in instrument and "Cello Bow" not in instrument):
                inst_categories2.append("Cello")            
            if input.highlight_Bass2() and ("Bass" in instrument and "Bass Bow" not in instrument):
                inst_categories2.append("Bass")
                
            if input.highlight_ViolinBow2() and "Violin Bow" in instrument:
                inst_categories2.append("Bow")            
            if input.highlight_ViolaBow2() and "Viola Bow" in instrument:
                inst_categories2.append("Bow")            
            if input.highlight_CelloBow2() and "Cello Bow" in instrument:
                inst_categories2.append("Bow")                        
            if input.highlight_BassBow2() and "Bass Bow" in instrument:  
                inst_categories2.append("Bow")    
            
            return " & ".join(inst_categories2) if inst_categories2 else "Other"

        data['Category2'] = data['Instrument'].apply(categorize_instrument2)

        return data


    ############
    
    @reactive.Calc
    # return filtered list of maker names by letter
    def letter_name_list():
        letter = input.makerletter()
        
        return Tarisio[Tarisio['Maker'].str.startswith(input.makerletter())]['Maker'].tolist()
           
    @reactive.effect
    # update makername with filtered list of maker names by letter
    def update_maker_name_choices():
        import html
        data = [html.unescape(name) for name in letter_name_list()]
        ui.update_selectize(
            'makername',
            choices=data,
            server=False,       # server=True creates the &amp; text in maker names
        )  
  

    ################## Plot top makers #####################  
    
    @render_plotly  
    # plot data for selected top maker
    def topmaker_plot():
        topmaker_df = checkbox_filter_instruments()

        # Check if any instruments are selected
        selected_instruments = topmaker_df['Category'].unique()
        no_instruments_selected = len(selected_instruments) 
    
        # If no instruments are selected, label as 'All Instruments'; otherwise, keep 'Other' for unselected data
        if no_instruments_selected == 0:
            topmaker_df['Category'] = 'All Instruments'
        else:
            # Ensure 'Other' is applied to unselected data
            topmaker_df.loc[~topmaker_df['Category'].isin(selected_instruments), 'Category'] = 'Other'
        
        num = topmaker_df['Year'].count()
        
        total_sales = topmaker_df['SalePrice'].sum()
        top_maker_instruments = topmaker_df['Instrument'].unique()
        
        # Ensure top_maker_instruments is converted from NumPy arrays to strings
        top_maker_instruments_str = ', '.join(top_maker_instruments)
              
        # formatting for dollar amounts in plot title
        add_commas = '{:,}'
       
        # Some makers have 1 or 2 data entries. Do the fit calculation for those with more entries. 
        if num > 5:
            
            X = topmaker_df[['Year']]
            y = topmaker_df['SalePrice']

            # Define the degree of the polynomial (e.g., 2 for quadratic, 3 for cubic)
            degree = 2
            poly = PolynomialFeatures(degree=degree)
            X_poly = poly.fit_transform(X)

            # Fit the polynomial regression model
            model = LinearRegression()
            model.fit(X_poly, y)

            # Generate predictions for plotting
            X_range = np.linspace(X.min(), X.max(), 500).reshape(-1, 1)
            X_range_poly = poly.transform(X_range)
            y_poly_pred = model.predict(X_range_poly)
        
            # Create Plotly scatter plot for data points
            fig = px.scatter(
                x=X.squeeze(), 
                y=y,
                color=topmaker_df['Category'],
                custom_data=[topmaker_df['Instrument']],
                symbol_sequence=['diamond'],
                color_discrete_map=color_map_maker,
                labels={'x': 'Year', 'y': 'Price in Dollars'} 
            )
             
            # Add the polynomial regression line
            fig.add_trace(go.Scatter(
                x=X_range.squeeze(), 
                y=y_poly_pred, mode='lines', 
                name=f'{degree}-degree polynomial fit', 
                line=dict(color='red')
            ))  
                 
            fig.update_traces(
                hovertemplate ='Year: %{x}<br>Sale Price: $%{y}<br>Instrument: %{customdata}<br>'
            )
        
            fig.update_layout(
                margin=dict(l=20, r=20, t=50, b=20),
                legend_title_text='Instrument',
                title={
                    'text': f'Total auction sales for {input.topmakers()}: ${add_commas.format(total_sales)}. <br>Instruments for this maker: {top_maker_instruments_str}.',
                    'x': 0.41,      # Center the title
                    'xanchor': 'center',
                    'yanchor': 'top',
                }
            )
                       
            return fig
            
        else:
            x = topmaker_df['Year']
            y = topmaker_df['SalePrice']
            
            fig, ax = plt.subplots() 
        
            fig = px.scatter(
                topmaker_df,
                x, 
                y,
                color=topmaker_df['Category'],
                custom_data=[topmaker_df['Instrument']],
                symbol_sequence=['diamond'],
                color_discrete_map=color_map_maker,
                labels={'x': 'Year', 'y': 'Price in Dollars'}, 
            )
                
            fig.update_traces(
                hovertemplate='Year: %{x}<br>Sale Price: $%{y}<br>Instrument: %{customdata}'
            )

            fig.update_layout(
                margin=dict(l=20, r=20, t=50, b=20),
                legend_title_text='Instrument',
                title={
                    'text': f'Total auction sales for {input.topmakers()}: $:{add_commas.format(total_sales)}. <br>Instruments for this maker: {top_maker_instruments_str}.',
                    'x': 0.41,      # Center the title
                    'xanchor': 'center',
                    'yanchor': 'top',
                }
            )
            
            return fig 
    
    ############## Plot makers alphabetically ####################

    @render_plotly  
    def maker_plot():
        maker_df = checkbox_filter_instruments2()
        
        # Check if any instruments are selected
        selected_instruments = maker_df['Category2'].unique()
        no_instruments_selected = len(selected_instruments) 
    
        # If no instruments are selected, label as 'All Instruments'; otherwise, keep 'Other' for unselected data
        if no_instruments_selected == 0:
            maker_df['Category2'] = 'All Instruments'
        else:
            # Ensure 'Other' is applied to unselected data
            maker_df.loc[~maker_df['Category2'].isin(selected_instruments), 'Category2'] = 'Other'
        
        num = maker_df['Year'].count()

        total_sales = maker_df['SalePrice'].sum()
        maker_instruments = maker_df['Instrument'].unique()
        
        # Ensure maker_instruments is converted from NumPy arrays to strings
        maker_instruments_str = ', '.join(maker_instruments)
        
        # formatting for dollar amounts in plot title
        add_commas = '{:,}'

        # Some makers have 1 or 2 data entries. Do the fit calculation for those with more entries. 
        if num > 5:
            
            X = maker_df[['Year']]
            y = maker_df['SalePrice']

            # Define the degree of the polynomial (e.g., 2 for quadratic, 3 for cubic)
            degree = 2
            poly = PolynomialFeatures(degree=degree)
            X_poly = poly.fit_transform(X)

            # Fit the polynomial regression model
            model = LinearRegression()
            model.fit(X_poly, y)

            # Generate predictions for plotting
            X_range = np.linspace(X.min(), X.max(), 500).reshape(-1, 1)
            X_range_poly = poly.transform(X_range)
            y_poly_pred = model.predict(X_range_poly)
    
            # Create Plotly scatter plot for data points
            fig = px.scatter(
                x=X.squeeze(), 
                y=y,
                color=maker_df['Category2'],
                custom_data=[maker_df['Instrument']],
                symbol_sequence=['diamond'],
                color_discrete_map=color_map_maker,
                labels={'x': 'Year', 'y': 'Price in Dollars'}, 
            )
            
            # Add the polynomial regression line
            fig.add_trace(go.Scatter(
                x=X_range.squeeze(), 
                y=y_poly_pred, mode='lines', 
                name=f'{degree}-degree polynomial fit', 
                line=dict(color='red')
            ))
            
            fig.update_traces(
                hovertemplate ='Year: %{x}<br>Sale Price: $%{y}<br>Instrument: %{customdata}'
            )
            
            fig.update_layout(
                legend_title_text='Instrument',
                margin=dict(l=20, r=20, t=50, b=20),
                title={
                    'text': f'Total auction sales for {input.makername()}: ${add_commas.format(total_sales)}. <br>Instruments for this maker: {maker_instruments_str}.',
                    'x': 0.41,      # Center the title
                    'xanchor': 'center',
                    'yanchor': 'top',
                }
            )
            
            return fig
            
        else:
            x = maker_df['Year']
            y = maker_df['SalePrice']
            
            fig, ax = plt.subplots() 
        
            fig = px.scatter(
                maker_df,
                x, 
                y,
                color=maker_df['Category2'],
                custom_data=[maker_df['Instrument']],
                symbol_sequence=['diamond'],
                color_discrete_map=color_map_maker,
                labels={'x': 'Year', 'y': 'Price in Dollars'}, 
            )
                
            fig.update_traces(
                hovertemplate='Year: %{x}<br>Sale Price: $%{y}<br>Instrument: %{customdata}'
            )
          
            fig.update_layout(
                margin=dict(l=20, r=20, t=50, b=20),
                legend_title_text='Instrument',
                title={
                    'text': f'Total auction sales for {input.makername()}: ${add_commas.format(total_sales)}. <br>Instruments for this maker: {maker_instruments_str}.',
                    'x': 0.41,      # Center the title
                    'xanchor': 'center',
                    'yanchor': 'top',
                }
            )
            
            return fig
        

    ############## Plot maker trend by decade ####################

    @render.plot
    def maker_by_decade_plot():
        mdata_by_decade = checkbox_filter_instruments2()

        # Add a decade column to the df
        mdata_by_decade['Decade'] = (mdata_by_decade['Year'] // 10) * 10
        
        # Box plot by decade
        plt.figure(figsize=(14, 8))
        fig = sns.set_theme()   # set defaults: grey background and white grid lines
        fig = sns.boxplot(x='Decade', y='SalePrice', data=mdata_by_decade, showfliers=False)
        plt.xlabel('Decade')
        plt.ylabel('Sale Price')
        plt.title(f"Distribution of Sales for {input.makername()} by Decade (outliers removed)")
        plt.xticks(rotation=45)
        plt.tight_layout(pad = 2)

        return fig


############### PRICE RANGE TAB #################

    
    @render.data_frame 
    def data_table():
        return render.DataGrid(Table, filters=True)
    
    @reactive.Calc
    @render.data_frame
    # return selected instrument for table
    def data_instrument_table():    
        selected_instrument = input.instrumentsfiltercomp()
        
        # Return selected instrument df
        selected_inst_df = Tarisio[Tarisio['Instrument'] == selected_instrument]

        inst_highest_sales = selected_inst_df.groupby('Maker').apply(
            lambda x: x.loc[x['SalePrice'].idxmax(), ['SalePrice','SaleDate']] 
        )
        inst_highest_sales.reset_index(inplace=True)

        # Rename columns
        inst_highest_sales.columns = ['Maker', 'max_sale_price', 'max_sale_date']
        inst_highest_sales

        # Get min and most recent sale dates and prices, on selected instrument df
        inst_mins_maxs = selected_inst_df.groupby('Maker').agg(
            min_sale_price = ('SalePrice','min'),
            most_recent_sale_date = ('SaleDate','max'),
        )
        inst_mins_maxs.reset_index(inplace=True)
        
        # merge with original dataframe to get prices on those dates
        # merge on selected instrument df
        inst_min_sale_prices = selected_inst_df.merge(
            inst_mins_maxs[['Maker','min_sale_price']],
            how='inner',
            left_on=['Maker','SalePrice'],
            right_on=['Maker','min_sale_price']
        )[['Maker', 'min_sale_price', 'SaleDate']].rename(columns={'SaleDate': 'min_sale_date'})
        inst_min_sale_prices
        
        # Drop duplicates for multiple maker sales made on the same day. Keep only the minimum.
        inst_min_sale_prices = inst_min_sale_prices.groupby('Maker').apply(
            lambda x: x.loc[x['min_sale_price'].idxmin(), ['min_sale_price', 'min_sale_date']] 
        ).reset_index()
        inst_min_sale_prices
        
        # Merge for most_recent_sale_date, on selected instrument df
        inst_most_recent_sale_prices = selected_inst_df.merge(
            inst_mins_maxs[['Maker', 'most_recent_sale_date']],
            how='inner',
            left_on=['Maker', 'SaleDate'],
            right_on=['Maker', 'most_recent_sale_date']
        )[['Maker', 'most_recent_sale_date', 'SalePrice']].rename(columns={'SalePrice': 'most_recent_sale_price'})
        
        # Drop duplicates for multiple sales made on the same day. Keep only the maximum.
        inst_most_recent_sale_prices = inst_most_recent_sale_prices.groupby('Maker').apply(
            lambda x: x.loc[x['most_recent_sale_price'].idxmax(), ['most_recent_sale_price', 'most_recent_sale_date']] 
        ).reset_index()
                
        # Merge everything back into a single dataframe
        inst_mins_maxs_final = inst_mins_maxs.merge(
            inst_min_sale_prices, on=['Maker', 'min_sale_price'], how='left'
        ).merge(
            inst_most_recent_sale_prices, on=['Maker', 'most_recent_sale_date'], how='left'
        )
         
        # Merge data_highest_sales and data_mins_maxs
        # This is the complete df of max/min sale/date data           
        inst_Table = inst_highest_sales.merge(inst_mins_maxs_final, on='Maker')
        
        # Rename columns
        inst_Table = inst_Table.rename(columns={
            'Maker':'maker',
            'most_recent_sale_price':'----most recent sale price----', # ---s are to allow readability of very large sale prices
            'most_recent_sale_date':'date of most recent sale',
            'max_sale_price':'highest sale price',
            'max_sale_date':'date of highest sale',    
            'min_sale_price':'lowest sale price',
            'min_sale_date':'date of lowest sale',
        })
        
        # Reorder the table rows for the app
        # maker, max_sale_price, max_sale_date, min_sale_date, most_recent_sale_date, min_sale_price, most_recent_sale_price
        inst_Table = inst_Table.iloc[:,[0,6,4,1,2,5,3]]

        # Get names of Makers of selected instruments
        instrument_data = Tarisio[Tarisio['Instrument'] == selected_instrument]
        instrument_maker_names = instrument_data['Maker'].unique()
        
        # Filter these makers out of the df with all maker price points
        InstrumentTable = inst_Table[inst_Table['maker'].isin(instrument_maker_names)]
        
        return render.DataGrid(InstrumentTable, filters=True)
            
    
######### CONTACT TAB ############

    @render.image  
    def image():
        #img = {"src": here / "www/Scrolls.jpg", "width": "100%", "alt": "Image of strined instruments"}  #  "height": "400px",
        img = {
            "src": here / "www/Instruments2.jpg", 
            "width": "100%", 
            "alt": "Image of strined instruments"}  #  "height": "400px",
        return img
             
#################################   
    @reactive.effect
    @reactive.event(input.reset)
    def _():
        ui.update_selectize("instrumentsfilter", value=Instrument)
        ui.update_selectize("instrumentsfiltercomp", value=Instrument)

app = App(app_ui, server)

