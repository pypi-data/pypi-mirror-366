from typing import List, Any, Callable, Union, Tuple
import importlib
import dearpygui.dearpygui as dpg
import dearpygui._dearpygui as internal_dpg
from abc import ABC, abstractmethod
from datetime import date
import os

# ICONS
ICO_CALENDAR    = 'ico_calendar_14'
ICO_ABC         = 'ico_abc_14'
ICO_FILE        = {ICO_CALENDAR : 'calendar_month_14dp_FFFFFF_FILL0_wght200_GRAD0_opsz20.png',
                    ICO_ABC: 'abc_16dp_FFFFFF_FILL0_wght200_GRAD0_opsz20.png'}

def use_icon(icon_name : str):
     '''
        Register icons for future user
     '''
     if  not dpg.does_item_exist(icon_name):
        fd_img_path = os.path.join(os.path.dirname(__file__), "images")
        width, height, _, data = dpg.load_image(os.path.join(fd_img_path, ICO_FILE[icon_name]))
        ico_ = [width, height, data]
        with dpg.texture_registry():
            dpg.add_static_texture(width=ico_[0], height=ico_[1], default_value=ico_[2], tag=icon_name)


'''
COM REGISTRY:
    COMP_ID(int,str) = {'comp_ref':CLASS_REF, 'source_id':ID}

SOURCE REGISTRY:
    SOURCE_ID(int,str) = {'value':Any, 'comps':[ID..]}

'''
# TODO Thread safe struct ?
COM_REG     = dict() 
SOURCE_REG  = dict()

def add_component(cls : any, tag : Union[int, str] = None, parent : Union[int, str] = None , source : Union[int, str] = None, *args, **kwargs):
    '''
		Create and register new components
    '''
    def create_instance(cls, *args, **kwargs):
        """
        Creates an instance of a class from its class.

        Args:
            cls (any): Class
            *args: Positional arguments to pass to the class constructor.
            **kwargs: Keyword arguments to pass to the class constructor.

        Returns:
            An instance of the class, or None if an error occurs.
        """
        try:
            instance = cls(*args, **kwargs)
            return instance
        except (ImportError, AttributeError, TypeError) as e:
            print(f"Error creating instance of: {cls}")
            raise e


    #_parent = parent if parent else dpg.last_item()
    _parent = parent
    _item =  tag if tag else dpg.generate_uuid()
    _source = source if source else _item
    assert _item not in COM_REG , f'Item {_item} already exist'
    
    # Create component
    _component = create_instance(cls,  _item,  _parent)

    # Add to COM_REG
    COM_REG[_item] = {'comp_ref':_component, 'source_id':_source}

    # Add to SOURCE REF
    if _source not in SOURCE_REG.keys():
      SOURCE_REG[_source] = {'value':None, 'comps':[_item]}
    else:
      SOURCE_REG[_source]['comps'].append(_item)
      _component.set_value(SOURCE_REG[_source]['value'])
	
    return _item

def _is_component(item : Union[int, str]) -> bool:    
    '''
        Returns True if this is a valid component Id
    '''
    return item in COM_REG
    
def get_value(item : Union[int, str], **kwargs) -> Any:
	"""	 Returns an item's value.

	Args:
		item (Union[int, str]): 
	Returns:
		Any
	"""

	return SOURCE_REG[COM_REG[item]['source_id']]['value'] if _is_component(item) else internal_dpg.get_value(item,**kwargs)
    
def set_value(item : Union[int, str], value : Any, **kwargs) -> None:
	"""	 Set's an item's value.

	Args:
		item (Union[int, str]): 
		value (Any): 
	Returns:
		None
	"""
	if _is_component(item):
		SOURCE_REG[COM_REG[item]['source_id']]['value'] = value
		for id in SOURCE_REG[COM_REG[item]['source_id']]['comps']:
			COM_REG[id]['comp_ref'].set_value(value)
		return None
	else:
		return internal_dpg.set_value(item, value, **kwargs)

def delete_item(item : Union[int, str], *, children_only: bool =False, slot: int =-1, **kwargs) -> None:
	"""	 Deletes an item..

	Args:
		item (Union[int, str]): 
		children_only (bool, optional): 
		slot (int, optional): 
	Returns:
		None
	"""

	if _is_component(item):
		COM_REG[item]['comp_ref'].delete(children_only, **kwargs)
		if COM_REG[item]['source_id'] in SOURCE_REG:
			del SOURCE_REG[COM_REG[item]['source_id']]
		del COM_REG[item]
	else:
		internal_dpg.delete_item(item, children_only=children_only, slot=slot, **kwargs)

def get_item_configuration(item : Union[int, str], **kwargs) -> dict:
	"""	 Returns an item's configuration.

	Args:
		item (Union[int, str]): 
	Returns:
		dict
	"""
	if _is_component(item):
		return COM_REG[item]['comp_ref'].get_item_configuration(**kwargs)
	else:
		return internal_dpg.get_item_configuration(item, **kwargs)

def configure_item(item : Union[int, str], **kwargs) -> None:
	"""Configures an item after creation."""

	if _is_component(item):
		COM_REG[item]['comp_ref'].configure_item(**kwargs)
	else:
		internal_dpg.configure_item(item, **kwargs)


# Update global module 
dpg.add_component = add_component
dpg.get_value = get_value
dpg.set_value = set_value
dpg.delete_item = delete_item
dpg.get_item_configuration = get_item_configuration
dpg.configure_item = configure_item


class DPGComponent(ABC):

    def __init__(self, tag: Union[int, str] = 0, parent: Union[int, str] = 0 , show : bool = True):
        
        self._parent    = parent
        self._tag       = tag if tag else dpg.generate_uuid() 
        self._configuration = {'show':show}


    def get_item_configuration(self, **kwargs):
        '''
            Returns the item configuration
        '''
        return self._configuration
        

    @abstractmethod
    def configure_item(self, **kwargs):
        '''
            Configure item. Implement the keys that make sense for this component
        '''

    @abstractmethod
    def delete(self, children_only: bool =False, **kwargs):
        '''
            Delete all the widgets from the visual tree. 
            IMPORTANT: if sub components are created as part of this component, you need to delete them here. 
        '''

    @abstractmethod
    def show(self):
        '''
            Show (or render) the visual widgets that form this component.
        '''

    @abstractmethod 
    def get_value(self):
        '''
            Returns the component value of the component
        '''
    @abstractmethod
    def set_value(self, value:any):
        '''
            Set the value of the component
        '''


###########################################################################
#  Components
###########################################################################

class ManagedWindow(DPGComponent):
     '''
        A managed window can have state and configuration persisted in between session.
        dpg.save_current_sate
     '''
     def __init__(self, tag = 0, parent = 0):

        super().__init__(tag, parent)

        self.show()

class DatePickerComp(DPGComponent):
    '''
        The Date Picker will be created using two widgets: a text box to to show the current value and date 
        picker on a modal window
    '''

    def __init__(self, tag = 0, parent = 0):
        
        super().__init__(tag, parent)

        self._group_tag                 = dpg.generate_uuid()
        self._text_box_tag              = dpg.generate_uuid()
        self._date_picker_window_tag    = dpg.generate_uuid()
        self._date_picker               = dpg.generate_uuid()

        use_icon(ICO_CALENDAR)

        self.show()
    
   
    def delete(self, children_only: bool =False, **kwargs):
        if dpg.does_item_exist(self._group_tag):
            dpg.delete_item(self._group_tag, children_only=children_only, **kwargs)
        if dpg.does_item_exist(self._date_picker_window_tag):
            dpg.delete_item(self._date_picker_window_tag, children_only=children_only, **kwargs)

    def configure_item(self, **kwargs):
        if 'default_value' in kwargs:
            dpg.set_value(self._tag, kwargs['default_value'])
        if 'show' in  kwargs:
            dpg.configure_item(self._group_tag, show=kwargs['show'])

    def get_value(self):
        return dpg.get_value(self._tag)

    def set_value(self, value:any):
        if dpg.does_item_exist(self._text_box_tag):
            dpg.set_value(self._text_box_tag,  value.strftime("%Y-%m-%d"))
        if dpg.does_item_exist(self._date_picker):
            dpg.set_value(self._date_picker, {'month_day': value.day, 'year':value.year-1900, 'month':value.month-1})

    def show_date_picker(self, sender, app_data, user_data):
        dpg.configure_item(self._date_picker_window_tag, show=True)
    
    def on_value_selected(self, sender, app_data, user_data):
        
        if app_data:
            value  = date(int(app_data['year']+1900), int(app_data['month']+1), int(app_data['month_day']))
            dpg.set_value(self._tag, value)

        dpg.configure_item(self._date_picker_window_tag, show=False)

    def show(self):
        '''
           This component is a text box and and date picker
        '''

        if not dpg.does_item_exist(self._group_tag) and self._configuration['show']:
        
            # Create a group at the root level
            with dpg.group(tag=self._group_tag, horizontal=True, show=self._configuration['show']):
                
                with dpg.window(label='Pick Date', modal=True, show=False, no_title_bar=False, tag=self._date_picker_window_tag):
                    dpg.add_date_picker(level=dpg.mvDatePickerLevel_Day, tag=self._date_picker,
                                        default_value={'month_day': 8, 'year':93, 'month':5}, callback=self.on_value_selected)
            
                dpg.add_input_text(tag = self._text_box_tag, enabled = False, width=80)
                dpg.add_image_button(ICO_CALENDAR, callback=self.show_date_picker)

            if self._parent:
                dpg.move_item(self._group_tag, parent=self._parent)
                
class TextBoxComp(DPGComponent):
    '''
        A wrapper for dpg TextBox 
    '''                    
    def __init__(self, tag = 0, parent = 0):
        
        super().__init__(tag, parent)

        self._group_tag                 = dpg.generate_uuid()
        self._text_box_tag              = dpg.generate_uuid()
      
        self.show()
    
    
    def delete(self, children_only: bool =False, **kwargs):
        if dpg.does_item_exist(self._group_tag):
            dpg.delete_item(self._group_tag, children_only=children_only, **kwargs)

    def configure_item(self, **kwargs):
        if 'show' in  kwargs:
            dpg.configure_item(self._group_tag, show=kwargs['show'])

    def get_value(self):
        return dpg.get_value(self._tag)

    def set_value(self, value:any):
        if dpg.does_item_exist(self._text_box_tag):
            dpg.set_value(self._text_box_tag,  value)

    def show(self):
        '''
           This component is a text box 
        '''

        if not dpg.does_item_exist(self._group_tag):
        
            # Create a group at the root level
            with dpg.group(tag=self._group_tag, show=self._configuration['show']):
                dpg.add_input_text(tag=self._text_box_tag, width=120)

            if self._parent:
                dpg.move_item(self._group_tag, parent=self._parent)

class DataGridComp(DPGComponent):
    '''
        A Data Grid Component. The value is a Pandas Data Frame.
    '''                    
    def __init__(self, tag = 0, parent = 0):
        
        super().__init__(tag, parent)

        self._group_tag                 = dpg.generate_uuid()
        self._table_tag                 = dpg.generate_uuid()
        self.show()

    
    def delete(self, children_only: bool =False, **kwargs):
        if dpg.does_item_exist(self._group_tag):
            dpg.delete_item(self._group_tag, children_only=children_only, **kwargs)

    def configure_item(self, **kwargs):
        if 'show' in  kwargs:
            dpg.configure_item(self._group_tag, show=kwargs['show'])

    def get_value(self):
        return dpg.get_value(self._tag)

    def set_value(self, value:any):
        self.delete()
        self.show()   

    def show(self):
        '''
           Use the table API to render the Data Grid.
        '''

            
        def sort_callback(sender, sort_specs):

            # sort_specs scenarios:
            #   1. no sorting -> sort_specs == None
            #   2. single sorting -> sort_specs == [[column_id, direction]]
            #   3. multi sorting -> sort_specs == [[column_id, direction], [column_id, direction], ...]
            #
            # notes:
            #   1. direction is ascending if == 1
            #   2. direction is ascending if == -1

            # no sorting case
            if sort_specs is None: return

            rows = dpg.get_item_children(sender, 1)

            # create a list that can be sorted based on first cell
            # value, keeping track of row and value used to sort
            sortable_list = []
            for row in rows:
                first_cell = dpg.get_item_children(row, 1)[0]
                sortable_list.append([row, dpg.get_value(first_cell)])

            def _sorter(e):
                return e[1]

            sortable_list.sort(key=_sorter, reverse=sort_specs[0][1] < 0)

            # create list of just sorted row ids
            new_order = []
            for pair in sortable_list:
                new_order.append(pair[0])
                            
            dpg.reorder_items(sender, 1, new_order)

        def _delete_table():
            if dpg.does_item_exist(self._table_tag):
                dpg.delete_item(self._table_tag)

        if not dpg.does_item_exist(self._group_tag):

            _delete_table()
        
            # Create a group at the root level
            with dpg.group(tag=self._group_tag, show=self._configuration['show']):

                with dpg.table(tag=self._table_tag, header_row=True, borders_innerH=True, sortable=True, callback=sort_callback,
                               borders_outerH=True, borders_innerV=True, borders_outerV=True):
                    
                    _data = dpg.get_value(self._tag)
                    if _data is not None and not _data.empty:
                        for c in _data.columns:
                            dpg.add_table_column(label=c)
                        for index, row in _data.iterrows():
                            with dpg.table_row():
                                for c in _data.columns:
                                     dpg.add_text(default_value=row[c])

            if self._parent:
                dpg.move_item(self._group_tag, parent=self._parent)