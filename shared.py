from pathlib import Path
import pandas as pd

app_dir = Path(__file__).parent

Tarisio = pd.read_csv(app_dir / "Tarisio_df.csv") #, encoding='utf-8')

# Drop AuctionHouse, AuctionCity, MakerID, City, Country
Tarisio = Tarisio.drop(columns=['AuctionHouse', 'AuctionCity','City', 'Country','MakerID']) 

# Color palette for dashboard tree maps
custom_colors = ["#9c2a2a","#faebd7",'#e5c08f',"#c1b193","#3e4e6c","#c0c0c0","#360a08"]  

# Create violins dataframe from Tarisio
violins = Tarisio.query('Instrument == "Violin"').reset_index().drop(['index'], axis=1)

# Colors for checkboxes on Instrument page
color_map = {
    "Stradivari": "#e81416",   # red
    "del Gesu": "#ffa500",     # orange
    "Guadagnini": "#faeb36",   # yellow
    "Vuillaume": "#79c314",    # green      
    "Sartory": "#030303",      # black     
    "Tourte": "#66808a",       # medium orange
    "Other": "#487de7",        # blue
    "All Makers": "#487de7",   # blue
} 

# Colors for instrument checkboxes on Makers page
color_map_maker = {
        "Violin": "#e81416",            # red
        "Bow": "#050505",               # black
        "Viola": "#ffa500",             # orange
        "Cello": "#79c314",             # green
        "Bass": "#fcba03",              # dark yellow
        "Other": "#487de7",             # blue
        "All Instruments": "#487de7",   # blue
}