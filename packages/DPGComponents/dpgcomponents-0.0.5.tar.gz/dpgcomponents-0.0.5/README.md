## dpg-components

 "A component is a piece of the UI (user interface) that has its own logic and appearance. A component can be as small as a button, or as large as an entire page." Components are a powerful abstraction.   

The goal of this project is to bring Components to [DearPyGui](https://github.com/hoffstadt/DearPyGui)   

 - Components should be first class citizens, i.e. use the same API as regular DPG Items.
 - Components can contain other Components or regular DPG Items.
 - Reusability is achieved through composition.

### Install
```python 
pip install DPGComponents
```

### How it works ?

Copy file DPGComponents.py into your project, then after import, you can interact with DPG as normal and also call the method "add_component" to add
complex components to your project. You can also define your own components by implementing abstract class "DPGComponent".

```python 
from datetime import datetime
import dearpygui.dearpygui as dpg
import DPGComponents
import DPGComponents.DPGComponents as comps
import pandas as pd

def save_callback():
    print("Save Clicked")

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

with dpg.window(label="Example Window"):
    dpg.add_text("Hello world")
    dpg.add_button(label="Save", callback=save_callback)
    dpg.add_input_text(label="string")
    dpg.add_slider_float(label="float")

    # add a Date Picker component
    dpg.add_component(comps.DatePickerComp, tag=f'date_picker_1')
    # Set default date to today
    dpg.configure_item(f'date_picker_1', default_value = datetime.now().date())

    #Add data grid
    dpg.add_component(comps.DataGridComp, tag=f'data_grid_1')    
    data = {
        'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [25, 30, 28],
        'City': ['New York', 'London', 'Paris']
    }
    df = pd.DataFrame(data)
        
    # Set data grid value
    dpg.set_value('data_grid_1', value = df)
        

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
```

