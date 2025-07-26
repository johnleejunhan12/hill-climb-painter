import tkinter as tk
import re

__all__ = [
    'VisibilityManager',
    'CustomToggleVisibilityCheckbox',
    'RangeSlider',
    'SingleSlider',
    'CustomCheckbox',
    'CustomTextInput',
    'Padding',
]

label_font = "Segoe UI Semibold"  # Default font for text in custom widgets
subtitle_font = "Segoe UI"  # Default font for subtitles in custom widgets


# --- VisibilityManager and CustomToggleVisibilityCheckbox for conditional UI logic ---
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
class CustomToggleVisibilityCheckbox(tk.Canvas):
    def __init__(self, master, text='', checked=False, command=None, 
                 visibility_manager=None, controlled_widgets=None,
                 width=200, height=32, box_size=16, font_size=13, bg_color='white', 
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
        
        # Find the scrollable frame reference
        self._scrollable_frame = None
        self._find_scrollable_frame()
        
        self._draw_checkbox()
        self.bind('<Button-1>', self._on_click)

    def _find_scrollable_frame(self):
        """Find the parent ScrollableFrame to enable auto-scrolling"""
        parent = self.master
        while parent:
            # Check if parent is a ScrollableFrame by looking for the canvas attribute
            if hasattr(parent, 'canvas') and hasattr(parent, 'frame'):
                self._scrollable_frame = parent
                break
            parent = parent.master if hasattr(parent, 'master') else None

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
        
        box_color = 'black' if self.checked else '#888'
        tick_color = 'black' if self.checked else '#888'
        text_color = 'black' if self.checked else '#888'
        
        self.create_rectangle(x0, y0, x1, y1, outline=box_color, width=2, fill='white', tags='box')
        
        # Draw check if checked
        if self.checked:
            self.create_line(x0+4, y0+self.box_size//2, x0+self.box_size//2, y1-4, 
                           x1-4, y0+4, fill=tick_color, width=3, 
                           capstyle=tk.ROUND, joinstyle=tk.ROUND)
        
        # Draw label 
        self.create_text(x1 + 10, self.height//2, text=self.text, anchor='w', 
                        fill=text_color, font=(label_font, 13))

    def _on_click(self, event):
        x0 = self.box_pad
        y0 = (self.height - self.box_size) // 2
        x1 = x0 + self.box_size
        y1 = y0 + self.box_size
        
        if x0 <= event.x <= x1 and y0 <= event.y <= y1 or event.x > x1:
            was_checked = self.checked
            self.checked = not self.checked
            self._draw_checkbox()
            self._update_widget_visibility()
            
            # Auto-scroll when revealing widgets
            if not was_checked and self.checked:
                self._scroll_to_show_revealed_content()
            
            if self.command:
                self.command(self.checked)

    def _scroll_to_show_revealed_content(self):
        """Automatically scroll to show newly revealed content"""
        if not self._scrollable_frame or not self.controlled_widgets:
            return
            
        # Wait for widgets to be shown and rendered
        self.after(50, self._perform_scroll)

    def _perform_scroll(self):
        """Perform the actual scrolling operation"""
        try:
            if not self._scrollable_frame or not self.controlled_widgets:
                return
                
            canvas = self._scrollable_frame.canvas
            
            # Update the scroll region first
            canvas.configure(scrollregion=canvas.bbox("all"))
            
            # Find the bottommost controlled widget
            bottom_widget = None
            max_bottom = 0
            
            for widget in self.controlled_widgets:
                if widget.winfo_viewable():
                    # Get widget position relative to the scrollable frame
                    widget_y = widget.winfo_y()
                    widget_height = widget.winfo_reqheight()
                    widget_bottom = widget_y + widget_height
                    
                    if widget_bottom > max_bottom:
                        max_bottom = widget_bottom
                        bottom_widget = widget
            
            if bottom_widget is None:
                return
                
            # Get canvas dimensions
            canvas_height = canvas.winfo_height()
            
            # Get current scroll region
            scroll_region = canvas.cget("scrollregion")
            if not scroll_region:
                return
                
            region_coords = scroll_region.split()
            if len(region_coords) != 4:
                return
                
            total_content_height = float(region_coords[3])
            
            # Calculate the position to scroll to show the bottom widget
            # We want to show the bottom widget near the bottom of the viewport
            target_bottom = max_bottom + 20  # Add some padding
            
            # Calculate what fraction of the content should be scrolled
            if total_content_height > canvas_height:
                # Calculate the scroll fraction to show the target position
                visible_top_target = target_bottom - canvas_height
                scroll_fraction = max(0, min(1, visible_top_target / (total_content_height - canvas_height)))
                
                # Smooth scroll to the target position
                self._smooth_scroll_to(canvas, scroll_fraction)
                
        except Exception as e:
            print(f"Error in auto-scroll: {e}")

    def _smooth_scroll_to(self, canvas, target_fraction, steps=10, current_step=0):
        """Smoothly scroll to the target position"""
        try:
            if current_step >= steps:
                return
                
            # Get current scroll position
            current_top, current_bottom = canvas.yview()
            current_fraction = current_top
            
            # Calculate intermediate position
            progress = (current_step + 1) / steps
            # Use easing function for smoother animation
            eased_progress = 1 - (1 - progress) ** 2  # Ease-out quadratic
            
            intermediate_fraction = current_fraction + (target_fraction - current_fraction) * eased_progress
            
            # Scroll to intermediate position
            canvas.yview_moveto(intermediate_fraction)
            
            # Schedule next step
            self.after(30, lambda: self._smooth_scroll_to(canvas, target_fraction, steps, current_step + 1))
            
        except Exception as e:
            print(f"Error in smooth scroll: {e}")

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
        was_checked = self.checked
        self.checked = checked
        self._draw_checkbox()
        self._update_widget_visibility()
        
        # Auto-scroll when programmatically revealing widgets
        if not was_checked and self.checked:
            self._scroll_to_show_revealed_content()
class RangeSlider(tk.Canvas):
    def __init__(self, master, min_val=0, max_val=100, init_min=None, init_max=None, width=300, height=None, command=None, title=None, subtitle=None, title_size=13, subtitle_size=10, bg_color='white', is_set_width_to_parent=False, show_value_labels=False, **kwargs):
        self._line_spacing = 6  # px between lines in title/subtitle (moved to top to avoid AttributeError)
        # Auto-calculate height if not specified
        if height is None:
            height = self._calculate_height(title, subtitle, title_size, subtitle_size)
        kwargs.setdefault('bg', bg_color)
        kwargs.setdefault('highlightthickness', 0)
        self.is_set_width_to_parent = is_set_width_to_parent
        self._user_height = height
        super().__init__(master, width=width, height=height, **kwargs)  # <-- moved up before any method calls
        if is_set_width_to_parent:
            self.bind('<Configure>', self._on_resize)
        self.min_val = min_val
        self.max_val = max_val
        self.command = command
        self.width = width
        self.height = height
        self.pad = 15  # Padding for thumbs
        self.thumb_radius = 10
        self.active_thumb = None
        self.slider_line_y = height // 2
        self.slider_line_width = 4
        self.value_range = max_val - min_val
        # Initial values
        self.val_min = init_min if init_min is not None else min_val
        self.val_max = init_max if init_max is not None else max_val
        self.title = title
        self.subtitle = subtitle
        self.title_size = 13
        self.subtitle_size = subtitle_size
        self.show_value_labels = show_value_labels
        # Draw initial
        self._draw_slider()
        self.bind('<Button-1>', self._on_click)
        self.bind('<B1-Motion>', self._on_drag)
        self.bind('<ButtonRelease-1>', self._on_release)

    def _calculate_height(self, title, subtitle, title_size, subtitle_size):
        """
        Calculate the total height based on presence of title and subtitle.
        
        Returns:
            int: Calculated height in pixels
        """
        slider_height = 24  # Height of the slider track and thumbs
        # Count lines for title and subtitle
        title_lines = title.count('\n') + 1 if title else 0
        subtitle_lines = subtitle.count('\n') + 1 if subtitle else 0
        title_height = title_size * title_lines + self._line_spacing * (title_lines - 1) if title else 0
        subtitle_height = subtitle_size * subtitle_lines + self._line_spacing * (subtitle_lines - 1) if subtitle else 0
        if title and subtitle:
            return title_height + 7 + subtitle_height + 15 + slider_height
        elif title:
            return title_height + 15 + slider_height
        elif subtitle:
            return subtitle_height + 15 + slider_height
        else:
            return slider_height

    def _on_resize(self, event):
        # Set width to parent width
        self.config(width=event.width)
        self.width = event.width
        self.height = self._user_height
        self._draw_slider()

    def _draw_slider(self):
        self.delete('all')
        # Calculate positions
        x1 = self._value_to_pos(self.val_min)
        x2 = self._value_to_pos(self.val_max)
        y = 0
        
        # Draw title if present (multi-line support, with string replacement)
        if self.title:
            title_str = self.title.replace('<current_min_value>', str(self.val_min)).replace('<current_max_value>', str(self.val_max))
            title_lines = title_str.split('\n')
            for i, line in enumerate(title_lines):
                self.create_text(self.pad, y, text=line, fill='black', font=(label_font, self.title_size), anchor='nw')
                y += self.title_size
                if i < len(title_lines) - 1:
                    y += self._line_spacing
            if self.subtitle:
                y += 7  # 7px gap between title and subtitle
            else:
                y += 15  # 15px gap between title and slider
        
        # Draw subtitle if present (multi-line support, with string replacement)
        if self.subtitle:
            subtitle_str = self.subtitle.replace('<current_min_value>', str(self.val_min)).replace('<current_max_value>', str(self.val_max))
            subtitle_lines = subtitle_str.split('\n')
            for i, line in enumerate(subtitle_lines):
                self.create_text(self.pad, y, text=line, fill='black', font=(subtitle_font, self.subtitle_size), anchor='nw')
                y += self.subtitle_size
                if i < len(subtitle_lines) - 1:
                    y += self._line_spacing
            y += 15  # 15px gap below subtitle
        
        # Draw track
        slider_y = y + 12  # 12px for half thumb height, so thumb sits flush with subtitle
        self.create_line(self.pad, slider_y, self.width - self.pad, slider_y, width=self.slider_line_width, fill='#ccc')
        # Draw selected range
        self.create_line(x1, slider_y, x2, slider_y, width=self.slider_line_width, fill='#007fff')
        # Draw thumbs as blue rectangles
        rect_w, rect_h = 12, 24
        self.thumb1 = self.create_rectangle(x1 - rect_w//2, slider_y - rect_h//2,
                                            x1 + rect_w//2, slider_y + rect_h//2,
                                            fill='#007fff', outline='', tags='thumb1')
        self.thumb2 = self.create_rectangle(x2 - rect_w//2, slider_y - rect_h//2,
                                            x2 + rect_w//2, slider_y + rect_h//2,
                                            fill='#007fff', outline='', tags='thumb2')
        # Draw value labels below thumbs if enabled
        if self.show_value_labels:
            self.create_text(x1, slider_y + rect_h//2 + 6, text=str(self.val_min), fill='#007fff', font=(label_font, 10))
            self.create_text(x2, slider_y + rect_h//2 + 6, text=str(self.val_max), fill='#007fff', font=(label_font, 10))
        self._slider_y = slider_y  # For hit testing

    def _value_to_pos(self, value):
        usable_width = self.width - 2 * self.pad
        rel = (value - self.min_val) / self.value_range
        return self.pad + rel * usable_width

    def _pos_to_value(self, x):
        usable_width = self.width - 2 * self.pad
        rel = (x - self.pad) / usable_width
        rel = min(max(rel, 0), 1)
        return round(self.min_val + rel * self.value_range)

    def _on_click(self, event):
        x = event.x
        x1 = self._value_to_pos(self.val_min)
        x2 = self._value_to_pos(self.val_max)
        
        # Check if click is within the slider track bounds
        if x < self.pad or x > self.width - self.pad:
            return
        
        # First check if clicking directly on a thumb (within thumb radius)
        thumb_hit = False
        if abs(x - x1) <= self.thumb_radius:
            self.active_thumb = 'min'
            thumb_hit = True
        elif abs(x - x2) <= self.thumb_radius:
            self.active_thumb = 'max'
            thumb_hit = True
        
        # If not clicking on a thumb, move the nearest thumb to the click position
        if not thumb_hit:
            click_value = self._pos_to_value(x)
            
            # Determine which thumb is closer to the click
            dist_to_min = abs(click_value - self.val_min)
            dist_to_max = abs(click_value - self.val_max)
            
            if dist_to_min <= dist_to_max:
                # Move min thumb, but ensure it doesn't go beyond max
                if click_value <= self.val_max:
                    self.val_min = max(click_value, self.min_val)
                    self.active_thumb = 'min'
            else:
                # Move max thumb, but ensure it doesn't go below min
                if click_value >= self.val_min:
                    self.val_max = min(click_value, self.max_val)
                    self.active_thumb = 'max'
            
            # Redraw and trigger callback
            self._draw_slider()
            if self.command:
                self.command(self.val_min, self.val_max)

    def _on_drag(self, event):
        if not self.active_thumb:
            return
        x = min(max(event.x, self.pad), self.width - self.pad)
        value = self._pos_to_value(x)
        if self.active_thumb == 'min':
            if value >= self.val_max:
                value = self.val_max
            if value < self.min_val:
                value = self.min_val
            self.val_min = value
        elif self.active_thumb == 'max':
            if value <= self.val_min:
                value = self.val_min
            if value > self.max_val:
                value = self.max_val
            self.val_max = value
        self._draw_slider()
        if self.command:
            self.command(self.val_min, self.val_max)

    def _on_release(self, event):
        self.active_thumb = None

    def get(self):
        return self.val_min, self.val_max

    def get_min(self):
        return self.val_min
        
    def get_max(self):
        return self.val_max

    def set(self, min_val, max_val):
        self.val_min = min_val
        self.val_max = max_val
        self._draw_slider()

class SingleSlider(tk.Canvas):
    def __init__(self, master, min_val=0, max_val=100, init_val=None, width=300, height=None, command=None, title=None, subtitle=None, title_size=13, subtitle_size=10, bg_color='white', is_set_width_to_parent=False, show_value_labels=False, **kwargs):
        self._line_spacing = 4  # px between lines in title/subtitle
        if height is None:
            height = self._calculate_height(title, subtitle, title_size, subtitle_size)
        kwargs.setdefault('bg', bg_color)
        kwargs.setdefault('highlightthickness', 0)
        self.is_set_width_to_parent = is_set_width_to_parent
        self._user_height = height
        super().__init__(master, width=width, height=height, **kwargs)
        if is_set_width_to_parent:
            self.bind('<Configure>', self._on_resize)
        self.min_val = min_val
        self.max_val = max_val
        self.command = command
        self.width = width
        self.height = height
        self.pad = 15
        self.thumb_radius = 10
        self.active_thumb = False
        self.slider_line_y = height // 2
        self.slider_line_width = 4
        self.value_range = max_val - min_val
        self.value = init_val if init_val is not None else min_val
        self.title = title
        self.subtitle = subtitle
        self.title_size = title_size
        self.subtitle_size = subtitle_size
        self.show_value_labels = show_value_labels
        self._draw_slider()
        self.bind('<Button-1>', self._on_click)
        self.bind('<B1-Motion>', self._on_drag)
        self.bind('<ButtonRelease-1>', self._on_release)

    def _calculate_height(self, title, subtitle, title_size, subtitle_size):
        slider_height = 24
        title_lines = title.count('\n') + 1 if title else 0
        subtitle_lines = subtitle.count('\n') + 1 if subtitle else 0
        title_height = title_size * title_lines + self._line_spacing * (title_lines - 1) if title else 0
        subtitle_height = subtitle_size * subtitle_lines + self._line_spacing * (subtitle_lines - 1) if subtitle else 0
        if title and subtitle:
            return title_height + 7 + subtitle_height + 15 + slider_height
        elif title:
            return title_height + 15 + slider_height
        elif subtitle:
            return subtitle_height + 15 + slider_height
        else:
            return slider_height

    def _on_resize(self, event):
        self.config(width=event.width)
        self.width = event.width
        self.height = self._user_height
        self._draw_slider()

    def _draw_slider(self):
        self.delete('all')
        x = self._value_to_pos(self.value)
        y = 0
        if self.title:
            title_str = self.title.replace('<current_value>', str(self.value))
            title_lines = title_str.split('\n')
            for i, line in enumerate(title_lines):
                self.create_text(self.pad, y, text=line, fill='black', font=(label_font, self.title_size), anchor='nw')
                y += self.title_size
                if i < len(title_lines) - 1:
                    y += self._line_spacing
            if self.subtitle:
                y += 7
            else:
                y += 15
        if self.subtitle:
            subtitle_str = self.subtitle.replace('<current_value>', str(self.value))
            subtitle_lines = subtitle_str.split('\n')
            for i, line in enumerate(subtitle_lines):
                self.create_text(self.pad, y, text=line, fill='black', font=(subtitle_font, self.subtitle_size), anchor='nw')
                y += self.subtitle_size
                if i < len(subtitle_lines) - 1:
                    y += self._line_spacing
            y += 15
        slider_y = y + 12
        self.create_line(self.pad, slider_y, self.width - self.pad, slider_y, width=self.slider_line_width, fill='#ccc')
        self.create_line(self.pad, slider_y, x, slider_y, width=self.slider_line_width, fill='#007fff')
        rect_w, rect_h = 12, 24
        self.thumb = self.create_rectangle(x - rect_w//2, slider_y - rect_h//2,
                                          x + rect_w//2, slider_y + rect_h//2,
                                          fill='#007fff', outline='', tags='thumb')
        if self.show_value_labels:
            self.create_text(x, slider_y + rect_h//2 + 6, text=str(self.value), fill='#007fff', font=(label_font, 10))

    def _value_to_pos(self, value):
        usable_width = self.width - 2 * self.pad
        rel = (value - self.min_val) / self.value_range
        return self.pad + rel * usable_width

    def _pos_to_value(self, x):
        usable_width = self.width - 2 * self.pad
        rel = (x - self.pad) / usable_width
        rel = min(max(rel, 0), 1)
        return round(self.min_val + rel * self.value_range)

    def _on_click(self, event):
        x = event.x
        if x < self.pad or x > self.width - self.pad:
            return
        y = 0
        if self.title:
            y += self.title_size
            if self.subtitle:
                y += 7
            else:
                y += 15
        if self.subtitle:
            y += self.subtitle_size + 15
        slider_y = y + 12
        rect_w, rect_h = 12, 24
        thumb_x = self._value_to_pos(self.value)
        thumb_left = thumb_x - rect_w // 2
        thumb_right = thumb_x + rect_w // 2
        thumb_top = slider_y - rect_h // 2
        thumb_bottom = slider_y + rect_h // 2
        if thumb_left <= x <= thumb_right and thumb_top <= event.y <= thumb_bottom:
            self.active_thumb = True
        else:
            value = self._pos_to_value(x)
            self.value = max(self.min_val, min(self.max_val, value))
            self.active_thumb = True
            self._draw_slider()
            if self.command:
                self.command(self.value)

    def _on_drag(self, event):
        if not self.active_thumb:
            return
        x = min(max(event.x, self.pad), self.width - self.pad)
        value = self._pos_to_value(x)
        if value < self.min_val:
            value = self.min_val
        if value > self.max_val:
            value = self.max_val
        self.value = value
        self._draw_slider()
        if self.command:
            self.command(self.value)

    def _on_release(self, event):
        self.active_thumb = False

    def get(self):
        return self.value

    def set(self, value):
        self.value = value
        self._draw_slider()


class CustomCheckbox(tk.Canvas):
    def __init__(self, master, text='', checked=False, command=None, width=200, height=32, box_size=16, font_size=13, bg_color='white', is_set_width_to_parent=False, **kwargs):
        """
        Custom styled checkbox.

        Parameters:
            master: Parent widget.
            text (str): Label text to display next to the checkbox.
            checked (bool): Initial checked state.
            command (callable): Callback function called with (checked: bool) when toggled.
            width (int): Initial width of the checkbox (overridden if is_set_width_to_parent=True).
            height (int): Height of the checkbox.
            box_size (int): Size of the checkbox square.
            font_size (int): Font size for the label.
            bg_color (str): Background color of the checkbox.
            is_set_width_to_parent (bool): If True, checkbox resizes to parent width.
            **kwargs: Additional Canvas options.
        Note: Left padding (box_pad) is set to 14 for extra space on the left.
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
        self.box_pad = 14  # Increased left padding
        self._draw_checkbox()
        self.bind('<Button-1>', self._on_click)

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
        box_color = 'black' if self.checked else '#888'
        tick_color = 'black' if self.checked else '#888'
        text_color = 'black' if self.checked else '#888'
        self.create_rectangle(x0, y0, x1, y1, outline=box_color, width=2, fill='white', tags='box')
        # Draw check if checked
        if self.checked:
            self.create_line(x0+4, y0+self.box_size//2, x0+self.box_size//2, y1-4, x1-4, y0+4, fill=tick_color, width=3, capstyle=tk.ROUND, joinstyle=tk.ROUND)
        # Draw label (bold)
        self.create_text(x1 + 10, self.height//2, text=self.text, anchor='w', fill=text_color, font=(label_font, 13))

    def _on_click(self, event):
        x0 = self.box_pad
        y0 = (self.height - self.box_size) // 2
        x1 = x0 + self.box_size
        y1 = y0 + self.box_size
        if x0 <= event.x <= x1 and y0 <= event.y <= y1 or event.x > x1:
            self.checked = not self.checked
            self._draw_checkbox()
            if self.command:
                self.command(self.checked)

    def get(self):
        return self.checked

    def set(self, checked):
        self.checked = checked
        self._draw_checkbox()
class CustomTextInput(tk.Frame): 
    def __init__(self, master, width=300, height=None, title=None, subtitle=None, title_size=13, subtitle_size=10, bg_color='white', is_set_width_to_parent=False, on_text_change=None, **kwargs):
        self._line_spacing = 6
        if height is None:
            title_lines = title.count('\n') + 1 if title else 0
            subtitle_lines = subtitle.count('\n') + 1 if subtitle else 0
            title_height = title_size * title_lines + self._line_spacing * (title_lines - 1) if title else 0
            subtitle_height = subtitle_size * subtitle_lines + self._line_spacing * (subtitle_lines - 1) if subtitle else 0
            if title and subtitle:
                height = title_height + 5 + subtitle_height + 15 + 4 + 32
            elif title:
                height = title_height + 15 + 4 + 32
            elif subtitle:
                height = subtitle_height + 15 + 4 + 32
            else:
                height = 32
        super().__init__(master, width=width, height=height, bg=bg_color, **kwargs)
        self.bg_color = bg_color
        self.is_set_width_to_parent = is_set_width_to_parent
        self._user_height = height
        self.title = title
        self.subtitle = subtitle
        self.title_size = title_size
        self.subtitle_size = subtitle_size
        self.on_text_change = on_text_change
        self.pack_propagate(False)

        x_pad = 12
        y = 0
        if self.title:
            self.title_label = tk.Label(self, text=self.title, anchor='w', font=(label_font, self.title_size), bg=bg_color, fg='black')
            self.title_label.pack(fill='x', anchor='w', pady=(0,0), padx=(x_pad,0))
            y += self.title_size
            if self.title.count('\n'):
                y += self._line_spacing * self.title.count('\n')
            if self.subtitle:
                y += 5
            else:
                y += 15
        if self.subtitle:
            self.subtitle_label = tk.Label(self, text=self.subtitle, anchor='w', font=(subtitle_font, self.subtitle_size), bg=bg_color, fg='black')
            self.subtitle_label.pack(fill='x', anchor='w', pady=(0,0), padx=(x_pad,0))
            y += self.subtitle_size
            if self.subtitle.count('\n'):
                y += self._line_spacing * self.subtitle.count('\n')
            y += 15

        entry_pad_top = 4 if self.subtitle else 0
        self.entry_border = tk.Frame(self, bg='black', bd=0, highlightthickness=0)
        self.entry_border.pack(fill='x', padx=(x_pad, x_pad), pady=(entry_pad_top,0))
        self.entry = tk.Entry(self.entry_border, font=(subtitle_font, 12), bg='white', relief='flat', highlightthickness=0, bd=0)
        self.entry.pack(fill='x', padx=0, pady=0, ipady=2)
        self.entry_border.config(highlightbackground='black', highlightcolor='black', highlightthickness=2, bd=0)
        self.entry.bind('<KeyRelease>', self._on_text_change)

        if is_set_width_to_parent:
            self.bind('<Configure>', self._on_resize)

    def _on_resize(self, event):
        self.config(width=event.width)
        self.entry_border.config(width=event.width)
        self.entry.config(width=event.width)

    def _on_text_change(self, event):
        # Validate and sanitize filename
        current_text = self.entry.get()
        safe_text = self._sanitize_filename(current_text)
        if current_text != safe_text:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, safe_text)
        if self.on_text_change:
            self.on_text_change(safe_text)

    def _sanitize_filename(self, name):
        # Remove unsafe characters (only allow letters, numbers, underscores, dashes)
        name = re.sub(r'[^A-Za-z0-9_-]', '_', name)
        # Optional: Limit length to 255 characters
        return name[:255]

    def get(self):
        return self.entry.get()

    def set(self, text):
        safe_text = self._sanitize_filename(text)
        self.entry.delete(0, tk.END)
        self.entry.insert(0, safe_text)

class Padding(tk.Frame):
    def __init__(self, master, height=20, bg_color='white', **kwargs):
        super().__init__(master, height=height, bg=bg_color, **kwargs)
        self.pack_propagate(False)



def on_slider_change(value):
    print(f"Slider value changed to: {value}")

    # Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Single Slider Demo")
    slider = SingleSlider(
        root,
        min_val=0,
        max_val=100,
        init_val=50,
        width=400,
        title="Adjust Value\n<current_value>",
        subtitle="Slider Control",
        show_value_labels=True,
        command=on_slider_change
    )
    slider.pack(padx=10, pady=10)
    root.mainloop()