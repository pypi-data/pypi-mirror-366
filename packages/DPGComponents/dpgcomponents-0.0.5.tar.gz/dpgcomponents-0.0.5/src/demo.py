from datetime import datetime
import pandas as pd
import dearpygui.dearpygui as dpg
import DPGComponents.DPGComponents as comps

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

def _on_demo_close(sender, app_data, user_data):
    dpg.delete_item('date_picker_1')
    dpg.delete_item('text_box_1')
    dpg.delete_item(sender)

with dpg.window(label="Example Components Window", on_close=_on_demo_close, width=800, 
                 height=800, pos=(100,100) ) as w:
    
    with dpg.tree_node(label="Date picker"):

        dpg.add_component(comps.DatePickerComp, tag=f'date_picker_1')

        # Set default date to today
        dpg.configure_item(f'date_picker_1', default_value = datetime.now().date())

    
    with dpg.tree_node(label="Data Grid"):

        dpg.add_text(default_value="Render a Pandas Data Frame to the GUI", show_label=False)
        # Add Data Grid component
        dpg.add_component(comps.DataGridComp, tag=f'data_grid_1')
        
        data = {
            'Name': ['Alice', 'Bob', 'Charlie'],
            'Age': [25, 30, 28],
            'City': ['New York', 'London', 'Paris']
        }
        df = pd.DataFrame(data)
        
        # Set data grid value
        dpg.set_value('data_grid_1', value = df)
        
        # get component config
        config = dpg.get_item_configuration('data_grid_1')

# show dpg registry
dpg.show_item_registry()

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()