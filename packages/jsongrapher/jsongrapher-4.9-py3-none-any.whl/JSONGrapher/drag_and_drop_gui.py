import os
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD


#This module contains a class called DragDropApp and also a function called create_and_launch.
#This module creates a GUI for users to select (and clear) files to be used with a developer's
# main program, such as JSONGrapher.  The way to use this module is through the create_and_launch function
# A developer should not (normally) ever need to make a DragAndDrop object instance themselves.


#The below class creates a window for dragging and dropping or browsing and selecting files
#And each time one or more file is added, the full file list and most recently added files will be passed to
#The function supplied by the user (function_for_after_file_addition)
#with the two variables passed being all_selected_file_paths, newly_added_file_paths
#This class **cannot** be initiated directly, it should initiated using the
#companion function create_and_launch
class DragDropApp:
    """
    GUI application for selecting files via drag-and-drop or browsing.

    This class provides a graphical interface that allows users to add files 
    either by dragging and dropping into a defined zone or by manual selection.
    Each time new files are added, the provided callback function 
    (function_for_after_file_addition) is invoked with two lists: 
    all_selected_file_paths and newly_added_file_paths.

    The callback function allows the developer's main program
    to take actions after the user has selected files.
    For example, with JSONGrapher, data is read in and merged into
    a global dataset each time a file is selected. 

    The app enables chosing files, displays selected filenames, allows clearing the selection,
    and can optionally download processed output returned by the callback function.
    The class *cannot* be initaited directly, it 
    must be initialized using the companion function `create_and_launch`.

    Attributes:
        root (Tk): The main Tkinter window object.
        app_name (str): Optional name for the application window.
        function_for_after_file_addition (Callable): User-defined function to be called 
            whenever new files are added.
        drop_frame (tk.Label): Drop zone for drag-and-drop file addition.
        file_listbox (tk.Listbox): Visual list displaying a list of filenames in a 'listbox' of the GUI
        select_button (tk.Button): Opens file dialog for manual selection.
        clear_button (tk.Button): Clears all selected files.
        download_button (tk.Button): Saves the output from the callback function.
        done_button (tk.Button): Ends the file selection session.
        all_selected_file_paths (list[str]): List of all currently selected file paths.
    """
    def __init__(self, root, app_name = '', function_for_after_file_addition = None):
        """
        Initializes the drag-and-drop application window.

        Sets up the GUI layout, enabling file selection via drag-and-drop and
        manual browsing. Once files are added, the provided callback function
        is triggered with the list of all selected file paths and the newly added ones.
        Also prepares buttons for clearing files, downloading output, and ending the session.

        Args:
            root (Tk): The Tkinter root window instance.
            app_name (str, optional): Name to display in the window title. Defaults to an empty string.
            function_for_after_file_addition (Callable, optional): Function to be called after new files 
                are added. It should accept two arguments: all_selected_file_paths and 
                newly_added_file_paths. Defaults to None.
        """


        self.root = root
        self.root.title(app_name)
        self.function_for_after_file_addition = function_for_after_file_addition

        # Enable native drag-and-drop capability
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind("<<Drop>>", self.drop_files)

        # Create a drop zone
        self.drop_frame = tk.Label(root, text="Drag and drop files here \n\n Click End When Finished", bg="lightgray", width=50, height=10)
        self.drop_frame.pack(pady=10)

        # Create a listbox to display selected files - it is a part of the GUI to show the filenames in a list.
        self.file_listbox = tk.Listbox(root, width=60, height=10)
        self.file_listbox.pack(pady=10)

        # Buttons for manual selection and finalizing selection
        self.select_button = tk.Button(root, text="Select Files By Browsing", command=self.open_file_dialog)
        self.select_button.pack(pady=5)

        # Create a frame for the middle buttons
        button_frame_middle = tk.Frame(root)
        button_frame_middle.pack(pady=5)

        self.clear_button = tk.Button(button_frame_middle, text="Clear Files List", command=self.clear_file_list)  # New "Clear" button
        self.clear_button.pack(side = tk.LEFT, pady=5)

        # "Download Output" button
        self.download_button = tk.Button(button_frame_middle, text="Download Output", command=self.download_output)
        self.download_button.pack(side = tk.RIGHT, pady=5)

        self.done_button = tk.Button(root, text="End", command=self.finish_selection)
        self.done_button.pack(pady=5)

        # Store selected file paths
        self.all_selected_file_paths = []

    def clear_file_list(self):
        """
        Clears all selected files from the interface and resets internal storage.

        Removes all items from the filelist in the GUI listbox display and resets the list of selected 
        file paths. If a callback function is provided, it is called with empty lists
        for both all_selected_file_paths and newly_added_file_paths.
        """

        self.file_listbox.delete(0, tk.END)  # Clear listbox
        self.all_selected_file_paths = []  # Reset file list
        self.function_for_after_file_addition(all_selected_file_paths=[], newly_added_file_paths=[])
        print("File list cleared!")  # Optional debug message

    def open_file_dialog(self):
        """
        Opens a file dialog for manually selecting files.

        Allows the user to choose one or more files using the system's file browser.
        Newly selected files are added to the internal list and reflected in the GUI filelist listbox.
        If a callback function is defined, it is called with updated lists of 
        all_selected_file_paths and newly_added_file_paths.
        """

        newly_added_file_paths = self.root.tk.splitlist(tk.filedialog.askopenfilenames(title="Select files"))
        if newly_added_file_paths:
            self.all_selected_file_paths.extend(newly_added_file_paths)
            self.update_file_list(newly_added_file_paths)

    def drop_files(self, event):
        """
        Handles files dropped into the GUI window.

        Parses the dropped file paths from the drag-and-drop event, updates the 
        internal list of selected files, and refreshes the GUI filelist listbox display. If a 
        callback function is provided, it is invoked with the current lists of 
        all_selected_file_paths and newly_added_file_paths.
        
        Args:
            event (tk.Event): The drag-and-drop event containing file path data.
        """

        newly_added_file_paths = self.root.tk.splitlist(event.data)
        if newly_added_file_paths:
            self.all_selected_file_paths.extend(newly_added_file_paths)
            self.update_file_list(newly_added_file_paths)

    def update_file_list(self, newly_added_file_paths):
        """
        Updates the GUI with all selected files and triggers post-addition actions.

        Clears the visual list of filenames in the GUI filelist listbox, reinserts updated entries,
        and invokes the callback function if defined. The callback receives both the 
        complete list of selected files and the list of newly added ones. The first 
        item returned by the callback is stored for later download.

        Args:
            newly_added_file_paths (list[str]): List of file paths recently added 
                via drag-and-drop or manual selection.
        """
        self.file_listbox.delete(0, tk.END)  # Clear listbox
        for filename_and_path in self.all_selected_file_paths:
            self.file_listbox.insert(tk.END, os.path.basename(filename_and_path))  # Show filenames only
        # If there is a function_for_after_file_addition, pass full list and newly added files into function_for_after_file_addition
        if self.function_for_after_file_addition is not None:
            output = self.function_for_after_file_addition(self.all_selected_file_paths, newly_added_file_paths)
            self.output_for_download = output[0] #store the first part of the output for download.

    def download_output(self):
        """
        Opens a dialog to save the output returned by the callback function.

        If the callback function has previously returned downloadable content, this method
        allows the user to choose a file path for saving that output. The output is written 
        as plain text to the selected location. If no downloadable output is available or the 
        save operation is canceled, appropriate messages are printed.
        """

        if hasattr(self, "output_for_download"):
            file_path = filedialog.asksaveasfilename(filetypes=[("*.*", "*.txt")], title="Save Output As")
            if file_path:  # If a valid path is chosen
                with open(file_path, "w") as file:
                    file.write(str(self.output_for_download))
                print(f"Output saved as '{file_path}'!")
            else:
                print("File save operation canceled.")
        else:
            print("No output available to download.")


    def finish_selection(self):
        """
        Terminates the application window and ends the selection session.

        Closes the GUI and stops the event loop. After this method is called,
        the list of all selected files is available for use outside the interface.
        """

        self.root.quit() # Close the window

# This function is a companion function to
# The class DragDropApp for creating a file selection and function call app
# The function_for_after_file_addition should return a list where the first item is something that can be downloaded.
def create_and_launch(app_name = '', function_for_after_file_addition=None):
    """
    Launches the drag-and-drop file selection GUI.

    Creates and initializes a window using the DragDropApp class, allowing users
    to select files via drag-and-drop or manual browsing. 
    As each file is added, a callback function from the user's main program
    is called, so that the user's main program can take action each time a file is selected.
    For example, JSONGrapher reads in the contents of each file
    and merges the data into a global data set each time a file is added.
    Once the window is closed by the user, the complete list of selected file paths is returned.

    Args:
        app_name (str, optional): Title for the GUI window. Defaults to an empty string.
        function_for_after_file_addition (Callable, optional): Function to be called 
            each time new files are added. This is a callback function.
            Receives all_selected_file_paths and 
            newly_added_file_paths as arguments. Defaults to None.

    Returns:
        list[str]: List of all file paths selected during the session.
    """
    root = TkinterDnD.Tk()
    app = DragDropApp(root, app_name=app_name, function_for_after_file_addition=function_for_after_file_addition)
    root.mainloop() # Runs the Tkinter event loop
    return app.all_selected_file_paths # Returns selected files after the window closes
