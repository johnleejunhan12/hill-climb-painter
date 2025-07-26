import tkinter as tk

class VisibilityManager:
    """Manages widget visibility while maintaining proper order"""
    
    def __init__(self):
        self.controlled_widgets = {}  # {widget: {'pack_info': {}, 'controller': checkbox}}
        self.widget_order = []  # Maintains the original order of widgets
    
    def register_widget(self, widget, pack_info, controller=None):
        """Register a widget to be managed"""
        self.controlled_widgets[widget] = {
            'pack_info': pack_info,
            'controller': controller,
            'visible': True
        }
        if widget not in self.widget_order:
            self.widget_order.append(widget)
    
    def hide_widgets(self, widgets):
        """Hide specified widgets"""
        for widget in widgets:
            if widget in self.controlled_widgets:
                widget.pack_forget()
                self.controlled_widgets[widget]['visible'] = False
    
    def show_widgets(self, widgets):
        """Show specified widgets in proper order"""
        # Mark widgets as should be visible
        for widget in widgets:
            if widget in self.controlled_widgets:
                self.controlled_widgets[widget]['visible'] = True
        
        # Repack all widgets in original order
        self._repack_all_in_order()
    
    def _repack_all_in_order(self):
        """Repack all widgets in their original order"""
        # First, forget all managed widgets
        for widget in self.widget_order:
            if widget in self.controlled_widgets:
                widget.pack_forget()
        
        # Then pack them back in order, but only if they should be visible
        for widget in self.widget_order:
            if (widget in self.controlled_widgets and 
                self.controlled_widgets[widget]['visible']):
                pack_info = self.controlled_widgets[widget]['pack_info']
                widget.pack(**pack_info)

class OrderPreservingCheckbox(tk.Canvas):
    def __init__(self, master, text='', checked=False, command=None, 
                 visibility_manager=None, controlled_widgets=None,
                 width=200, height=32, box_size=16, font_size=11, bg_color='white', 
                 is_set_width_to_parent=False, **kwargs):
        """
        Checkbox that maintains proper widget order when showing/hiding controls.
        
        Parameters:
            visibility_manager: VisibilityManager instance to handle proper ordering
            controlled_widgets: List of widgets this checkbox controls
        """
        kwargs.setdefault('bg', bg_color)
        kwargs.setdefault('highlightthickness', 0)
        self.is_set_width_to_parent = is_set_width_to_parent
        self._user_height = height
        super().__init__(master, width=width, height=height, **kwargs)
        
        if is_set_width_to_parent:
            self.bind('<Configure>', self._on_resize)
        
        self.text = text
        self.checked = checked
        self.command = command
        self.box_size = box_size
        self.font_size = font_size
        self.width = width
        self.height = height
        self.box_pad = 14
        
        self.visibility_manager = visibility_manager
        self.controlled_widgets = controlled_widgets or []
        
        self._draw_checkbox()
        self.bind('<Button-1>', self._on_click)
        
        # NOTE: Don't apply initial state here - controlled_widgets might not be set yet

    def set_controlled_widgets(self, controlled_widgets):
        """Set the controlled widgets and apply initial visibility state"""
        self.controlled_widgets = controlled_widgets
        # Now apply the initial visibility state
        self._update_widget_visibility()

    def _on_resize(self, event):
        self.config(width=event.width)
        self.width = event.width
        self.height = self._user_height
        self._draw_checkbox()

    def _draw_checkbox(self):
        self.delete('all')
        # Draw box
        x0 = self.box_pad
        y0 = (self.height - self.box_size) // 2
        x1 = x0 + self.box_size
        y1 = y0 + self.box_size
        self.create_rectangle(x0, y0, x1, y1, outline='#007fff', width=2, fill='white', tags='box')
        
        # Draw check if checked
        if self.checked:
            self.create_line(x0+4, y0+self.box_size//2, x0+self.box_size//2, y1-4, x1-4, y0+4, 
                           fill='#007fff', width=3, capstyle=tk.ROUND, joinstyle=tk.ROUND)
        
        # Draw label (bold)
        self.create_text(x1 + 10, self.height//2, text=self.text, anchor='w', 
                        fill='black', font=('Arial', self.font_size, 'bold'))

    def _on_click(self, event):
        x0 = self.box_pad
        y0 = (self.height - self.box_size) // 2
        x1 = x0 + self.box_size
        y1 = y0 + self.box_size
        
        if x0 <= event.x <= x1 and y0 <= event.y <= y1 or event.x > x1:
            self.checked = not self.checked
            self._draw_checkbox()
            self._update_widget_visibility()
            
            if self.command:
                self.command(self.checked)

    def _update_widget_visibility(self):
        """Update visibility of controlled widgets"""
        if self.visibility_manager and self.controlled_widgets:
            if self.checked:
                self.visibility_manager.show_widgets(self.controlled_widgets)
            else:
                self.visibility_manager.hide_widgets(self.controlled_widgets)

    def get(self):
        return self.checked

    def set(self, checked):
        self.checked = checked
        self._draw_checkbox()
        self._update_widget_visibility()

# Demo application
class OrderPreservingDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("Order-Preserving Visibility Demo")
        self.root.geometry("500x600")
        
        main_frame = tk.Frame(root, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create visibility manager
        self.vis_manager = VisibilityManager()
        
        # Create widgets in the order you want them to appear
        self.create_widgets(main_frame)
        
        # Register all widgets with the visibility manager
        self.register_widgets()
    
    def create_widgets(self, parent):
        """Create all widgets in display order"""
        
        # Title
        title_label = tk.Label(parent, text="Visibility Control Demo", 
                              font=('Arial', 16, 'bold'), bg='white')
        title_label.pack(fill='x', pady=(0, 20))
        
        # First checkbox - controls advanced options
        self.advanced_checkbox = OrderPreservingCheckbox(
            parent,
            text="Show Advanced Options",
            checked=False,
            visibility_manager=self.vis_manager,
            is_set_width_to_parent=True,
            command=lambda x: print(f"Advanced options: {x}")
        )
        self.advanced_checkbox.pack(fill='x', pady=(0, 15))
        
        # Import your custom components
        try:
            from user_interface.tkinter_components import RangeSlider, SingleSlider, CustomTextInput
            
            # Advanced components (will be controlled by first checkbox)
            self.price_slider = RangeSlider(
                parent,
                min_val=0, max_val=1000,
                init_min=100, init_max=500,
                title="Price Range: $<current_min_value> - $<current_max_value>",
                subtitle="Select your budget range",
                is_set_width_to_parent=True
            )
            
            self.quality_slider = SingleSlider(
                parent,
                min_val=1, max_val=10,
                init_val=5,
                title="Quality Level: <current_value>/10",
                subtitle="Higher values mean better quality",
                is_set_width_to_parent=True
            )
            
        except ImportError:
            # Fallback to regular tkinter widgets for demo
            self.price_slider = tk.Label(parent, text="Price Range Slider (Custom Component)", 
                                       bg='lightblue', height=3)
            self.quality_slider = tk.Label(parent, text="Quality Slider (Custom Component)", 
                                         bg='lightgreen', height=3)
        
        self.price_slider.pack(fill='x', pady=(0, 15))
        self.quality_slider.pack(fill='x', pady=(0, 15))
        
        # Second checkbox - controls feature options
        self.features_checkbox = OrderPreservingCheckbox(
            parent,
            text="Enable Custom Features",
            checked=True,
            visibility_manager=self.vis_manager,
            is_set_width_to_parent=True,
            command=lambda x: print(f"Custom features: {x}")
        )
        self.features_checkbox.pack(fill='x', pady=(0, 15))
        
        # Feature components (controlled by second checkbox)
        try:
            self.custom_input = CustomTextInput(
                parent,
                title="Feature Name",
                subtitle="Enter a name for your custom feature",
                is_set_width_to_parent=True
            )
        except:
            self.custom_input = tk.Entry(parent, font=('Arial', 12))
        
        self.custom_input.pack(fill='x', pady=(0, 15))
        
        self.premium_checkbox = OrderPreservingCheckbox(
            parent,
            text="Enable Premium Features",
            checked=False,
            visibility_manager=self.vis_manager,
            is_set_width_to_parent=True,
            command=lambda x: print(f"Premium: {x}")
        )
        self.premium_checkbox.pack(fill='x', pady=(0, 15))
        
        # Always visible footer
        footer_label = tk.Label(parent, text="This footer is always visible", 
                               font=('Arial', 10, 'italic'), bg='white', fg='gray')
        footer_label.pack(fill='x', pady=(20, 0))
        
        # Register widgets with visibility manager
        widgets_and_pack_info = [
            (title_label, {'fill': 'x', 'pady': (0, 20)}),
            (self.advanced_checkbox, {'fill': 'x', 'pady': (0, 15)}),
            (self.price_slider, {'fill': 'x', 'pady': (0, 15)}),
            (self.quality_slider, {'fill': 'x', 'pady': (0, 15)}),
            (self.features_checkbox, {'fill': 'x', 'pady': (0, 15)}),
            (self.custom_input, {'fill': 'x', 'pady': (0, 15)}),
            (self.premium_checkbox, {'fill': 'x', 'pady': (0, 15)}),
            (footer_label, {'fill': 'x', 'pady': (20, 0)})
        ]
        
        for widget, pack_info in widgets_and_pack_info:
            self.vis_manager.register_widget(widget, pack_info)
        
        # NOW set controlled widgets and apply initial visibility
        self.advanced_checkbox.set_controlled_widgets([self.price_slider, self.quality_slider])
        self.features_checkbox.set_controlled_widgets([self.custom_input, self.premium_checkbox])
    
    def register_widgets(self):
        """Register widgets with their controllers"""
        # The visibility manager will handle everything automatically
        # based on the controlled_widgets lists we set up
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = OrderPreservingDemo(root)
    root.mainloop()