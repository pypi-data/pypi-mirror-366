"""Curses-based UI implementations for smooth Linux terminal experience"""

from typing import List, Dict
import platform

from .tables import format_timestamp
from ..utils import get_logger

# Set up module logger
logger = get_logger('catscan.ui.curses')

# Curses imports - only available on non-Windows platforms
if platform.system() != "Windows":
    try:
        import curses
        CURSES_AVAILABLE = True
    except ImportError:
        CURSES_AVAILABLE = False
        logger.warning("Curses not available on this platform")
else:
    CURSES_AVAILABLE = False
    curses = None


def show_scan_history_curses(history: List[Dict]):
    """Linux-optimized version using curses for buttery-smooth navigation"""
    if not CURSES_AVAILABLE:
        logger.error("Curses not available, cannot use curses UI")
        raise ImportError("Curses not available on this platform")
    
    logger.debug("Starting curses-based scan history viewer")
    selected_index = 0
    
    def curses_main(stdscr):
        nonlocal selected_index
        
        logger.debug("Initializing curses interface")
        
        # Curses initialization
        curses.curs_set(0)  # Hide cursor
        stdscr.keypad(True)  # Enable special keys
        stdscr.timeout(-1)  # Block on input (no timeout)
        
        # Set up colors if terminal supports them
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            # Define color pairs
            curses.init_pair(1, curses.COLOR_CYAN, -1)    # Cyan on default
            curses.init_pair(2, curses.COLOR_GREEN, -1)   # Green on default
            curses.init_pair(3, curses.COLOR_YELLOW, -1)  # Yellow on default
            curses.init_pair(4, curses.COLOR_BLUE, -1)    # Blue on default
            curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Selection
            logger.debug("Colors initialized")
        
        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()
            
            # Title
            title = "📈 Scan History (↑↓ navigate, Enter view, ESC return)"
            title_y = 0
            title_x = max(0, (width - len(title)) // 2)
            try:
                stdscr.addstr(title_y, title_x, title, curses.A_BOLD)
            except:
                stdscr.addstr(title_y, 0, title[:width-1], curses.A_BOLD)
            
            # Separator line
            stdscr.addstr(1, 0, "─" * min(width-1, 120))
            
            # Column headers
            headers = ["Date/Time", "Organization", "Workspaces", "Resources", "Status"]
            col_widths = [20, 25, 12, 12, 15]
            header_y = 2
            x_pos = 0
            
            for i, (header, w) in enumerate(zip(headers, col_widths)):
                if x_pos + w < width:
                    attr = curses.color_pair(i+1) | curses.A_BOLD if curses.has_colors() else curses.A_BOLD
                    stdscr.addstr(header_y, x_pos, header.ljust(w)[:w], attr)
                    x_pos += w + 2
            
            # Separator line
            stdscr.addstr(3, 0, "─" * min(width-1, 120))
            
            # Calculate visible range
            list_start_y = 4
            list_height = height - list_start_y - 3  # Leave room for footer
            
            # Ensure selected item is visible (scroll if needed)
            if selected_index < list_height:
                visible_start = 0
            else:
                visible_start = selected_index - list_height + 1
            
            visible_end = min(len(history), visible_start + list_height)
            
            # Display scan entries
            for idx in range(visible_start, visible_end):
                y_pos = list_start_y + (idx - visible_start)
                scan = history[idx]
                
                # Prepare data
                timestamp = format_timestamp(scan["timestamp"])
                org = scan["organization"]
                ws_count = scan["summary"]["processed_workspaces"]
                total_ws = scan["summary"]["total_workspaces"]
                resources = scan["summary"]["total_resources"]
                
                if scan["summary"]["error_workspaces"] > 0:
                    status = f"✅ {ws_count} ⚠️ {scan['summary']['error_workspaces']}"
                else:
                    status = f"✅ {ws_count}/{total_ws}"
                
                # Build row
                row_data = [
                    timestamp[:19],
                    org[:24],
                    str(total_ws)[:11],
                    str(resources)[:11],
                    status[:14]
                ]
                
                # Display row
                x_pos = 0
                for i, (data, w) in enumerate(zip(row_data, col_widths)):
                    if x_pos + w < width:
                        if idx == selected_index:
                            # Highlighted row
                            attr = curses.color_pair(5) if curses.has_colors() else curses.A_REVERSE
                        else:
                            # Normal row with column colors
                            attr = curses.color_pair(i+1) if curses.has_colors() else curses.A_NORMAL
                        
                        stdscr.addstr(y_pos, x_pos, data.ljust(w)[:w], attr)
                        x_pos += w + 2
            
            # Footer with instructions
            footer_y = height - 2
            footer = f"Item {selected_index + 1} of {len(history)} | ↑↓:Navigate Enter:View ESC:Return"
            stdscr.addstr(footer_y, 0, "─" * min(width-1, 120))
            stdscr.addstr(footer_y + 1, 0, footer[:width-1])
            
            # Scroll indicator if needed
            if visible_start > 0:
                stdscr.addstr(list_start_y, width-3, "↑", curses.A_BOLD)
            if visible_end < len(history):
                stdscr.addstr(list_start_y + list_height - 1, width-3, "↓", curses.A_BOLD)
            
            stdscr.refresh()
            
            # Handle input
            key = stdscr.getch()
            logger.debug(f"Curses key pressed: {key}")
            
            if key == curses.KEY_UP:
                if selected_index > 0:
                    selected_index -= 1
            elif key == curses.KEY_DOWN:
                if selected_index < len(history) - 1:
                    selected_index += 1
            elif key == curses.KEY_HOME:
                selected_index = 0
            elif key == curses.KEY_END:
                selected_index = len(history) - 1
            elif key == curses.KEY_PPAGE:  # Page Up
                selected_index = max(0, selected_index - list_height)
            elif key == curses.KEY_NPAGE:  # Page Down
                selected_index = min(len(history) - 1, selected_index + list_height)
            elif key in [curses.KEY_ENTER, 10, 13, ord('\n'), ord('\r')]:
                # Exit curses temporarily to show details
                logger.info(f"Viewing scan details at index {selected_index}")
                curses.endwin()
                try:
                    from .rich_ui import show_scan_details
                    show_scan_details(history[selected_index])
                finally:
                    # Reinitialize curses
                    stdscr = curses.initscr()
                    curses.noecho()
                    curses.cbreak()
                    stdscr.keypad(True)
                    curses.curs_set(0)
                    if curses.has_colors():
                        curses.start_color()
                        curses.use_default_colors()
                        # Re-init color pairs
                        curses.init_pair(1, curses.COLOR_CYAN, -1)
                        curses.init_pair(2, curses.COLOR_GREEN, -1)
                        curses.init_pair(3, curses.COLOR_YELLOW, -1)
                        curses.init_pair(4, curses.COLOR_BLUE, -1)
                        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLUE)
            elif key == 27:  # ESC key - clean single press!
                logger.debug("ESC pressed, exiting curses interface")
                break
            elif key in [ord('q'), ord('Q')]:
                logger.debug("Q pressed, exiting curses interface")
                break
    
    # Run with curses wrapper for automatic cleanup
    logger.debug("Running curses wrapper")
    curses.wrapper(curses_main)
    logger.debug("Curses interface closed")